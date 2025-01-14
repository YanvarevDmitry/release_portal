from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from starlette.status import HTTP_401_UNAUTHORIZED

from sql_app.database import get_database
from sql_app.models.releases import ReleaseStage
from sql_app.models.user import RolesEnum
from sql_app.releases_service import get_all_releases, update_release
from models import ReleaseStageCreate, User
from auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/release_stages", tags=["release_stages"])


@router.post("/token", response_model=dict)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_database)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/", response_model=ReleaseStageCreate)
def create_release_stage(stage: ReleaseStageCreate,
                         db: Session = Depends(get_database),
                         current_user: User = Depends(get_current_user)):
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    release = create_release_stage(stage=stage, db=db)
    return release


@router.get("/", response_model=list[ReleaseStageCreate])
def get_all_release_stages(db: Session = Depends(get_database)):
    return get_all_releases(db=db)


@router.put("/{stage_id}")
def update_release_stage(stage_id: int,
                         name: str | None,
                         description: str | None,
                         start_date: str | None,
                         end_date: str | None,
                         current_user: User,
                         db: Session = Depends(get_database)
                         ):
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return update_release(stage_id=stage_id,
                          name=name,
                          description=description,
                          start_date=start_date,
                          end_date=end_date,
                          db=db)


@router.get("/report")
def generate_report(db: Session = Depends(get_database)):
    stages = get_all_releases(db=db)
    doc = Document()
    doc.add_heading("Release Stages Report", level=1)
    for stage in stages:
        doc.add_heading(stage.name, level=2)
        doc.add_paragraph(f"Description: {stage.description}")
        doc.add_paragraph(f"Start Date: {stage.start_date}")
        doc.add_paragraph(f"End Date: {stage.end_date}")
        doc.add_paragraph(f"Responsible Person: {stage.responsible_person}")
    file_path = "release_report.docx"
    doc.save(file_path)
    return {"message": f"Report generated at {file_path}"}
