from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from docx import Document

from app.sql_app.database import get_database
from app.sql_app.models.releases import ReleaseStage
from app.sql_app.models.user import RolesEnum
from app.sql_app.releases_service import get_all_releases
from app.models import ReleaseStageCreate, User

router = APIRouter(prefix="/release_stages", tags=["release_stages"])


@router.post("/", response_model=ReleaseStageCreate)
def create_release_stage(stage: ReleaseStageCreate, db: Session = Depends(get_database)):
    release = create_release_stage(stage=stage, db=db)
    return release


@router.get("/", response_model=List[ReleaseStageCreate])
def get_all_release_stages(db: Session = Depends(get_database)):
    return get_all_releases(db=db)


@router.put("/{stage_id}")
def update_release_stage(stage_id: int, name: str, description: str, start_date: str, end_date: str,
                         responsible_person: str, current_user: User,
                         db: Session = Depends(get_database)):
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    stage = db.query(ReleaseStage).filter(ReleaseStage.id == stage_id).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Release stage not found")

    stage.name = name
    stage.description = description
    stage.start_date = start_date
    stage.end_date = end_date
    stage.responsible_person = responsible_person
    db.commit()
    db.refresh(stage)


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
