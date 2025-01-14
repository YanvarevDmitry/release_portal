from typing import Annotated

from docx import Document
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from sql_app import releases_service
from sql_app.channels_service import get_channel
from sql_app.database import get_database

from sql_app.models.user import RolesEnum
from sql_app.platforms_service import get_platform
from sql_app.releases_service import get_all_releases, update_release, get_release, get_all_release_types
from schemas import ReleaseStageCreate, User, ReleaseStageOut, ReleaseTypeOut
from auth import get_current_user

router = APIRouter(prefix="/releases", tags=["releases"])
get_current_user = Annotated[User, Depends(get_current_user)]
db_session = Annotated[Session, Depends(get_database)]


@router.post("/", response_model=ReleaseStageOut)
def create_release(stage: ReleaseStageCreate,
                   current_user: get_current_user,
                   db: db_session,
                   ):
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if get_release(name=stage.name, db=db):
        raise HTTPException(status_code=400, detail="Release stage with this name already exists")
    if not get_channel(channel_id=stage.channel_id, db=db):
        raise HTTPException(status_code=404, detail="Channel not found")
    if not get_platform(platform_id=stage.platform_id, db=db):
        raise HTTPException(status_code=404, detail="Platform not found")
    release = releases_service.create_release(stage=stage, db=db)
    return release


@router.get("/", response_model=list[ReleaseStageOut])
def get_all_releases(db: db_session):
    releases = releases_service.get_all_releases(db=db)
    return releases


@router.delete("/{stage_id}", status_code=204)
def delete_release(stage_id: int,
                   current_user: get_current_user,
                   db: db_session):
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    release = releases_service.get_release(release_id=stage_id, db=db)
    if not release:
        raise HTTPException(status_code=404, detail="Release stage not found")
    return releases_service.delete_release(stage_id=stage_id, db=db)


@router.get("/report", response_class=FileResponse)
def generate_report(db: db_session):
    stages = get_all_releases(db=db)
    doc = Document()
    doc.add_heading("Release Stages Report", level=1)
    for stage in stages:
        doc.add_heading(stage.name, level=2)
        doc.add_paragraph(f"Description: {stage.description}")
        doc.add_paragraph(f"Start Date: {stage.start_date}")
        doc.add_paragraph(f"End Date: {stage.end_date}")
        doc.add_paragraph(f"Status: {stage.status.value}")
    file_path = "release_report.docx"
    doc.save(file_path)
    return FileResponse(file_path,
                        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        filename=file_path)


@router.put("/{stage_id}")
def update_release(stage_id: int,
                   name: str | None,
                   description: str | None,
                   start_date: str | None,
                   end_date: str | None,
                   current_user: get_current_user,
                   db: db_session
                   ):
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return update_release(stage_id=stage_id,
                          name=name,
                          description=description,
                          start_date=start_date,
                          end_date=end_date,
                          db=db)


@router.get('/types', response_model=list[ReleaseTypeOut], status_code=200)
def get_release_types(db: db_session):
    return get_all_release_types(db=db)


@router.post("/types", response_model=ReleaseTypeOut, status_code=201)
def create_release_type(name: str,
                        platform_id: int,
                        channel_id: int,
                        current_user: get_current_user,
                        db: db_session):
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not get_platform(platform_id=platform_id, db=db):
        raise HTTPException(status_code=404, detail="Platform not found")
    if not get_channel(channel_id=channel_id, db=db):
        raise HTTPException(status_code=404, detail="Channel not found")
    return releases_service.create_release_type(name=name, platform_id=platform_id, channel_id=channel_id, db=db)
