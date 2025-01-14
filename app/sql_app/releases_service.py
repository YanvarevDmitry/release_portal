from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import ReleaseStageCreate
from app.sql_app.models.releases import ReleaseStage


def create_release_stage(stage: ReleaseStageCreate, db) -> ReleaseStage:
    db_stage = ReleaseStage(**stage.dict())
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage


def get_all_releases(db) -> list[ReleaseStage]:
    return db.query(ReleaseStage).all()


def update_release(stage_id: int,
                   name: str | None,
                   description: str | None,
                   start_date: str | None,
                   end_date: str | None,
                   db: Session):
    stage = db.query(ReleaseStage).filter(ReleaseStage.id == stage_id).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Release stage not found")

    if name is not None:
        stage.name = name
    if description is not None:
        stage.description = description
    if start_date is not None:
        stage.start_date = datetime.fromisoformat(start_date).astimezone(pytz.UTC)
    if end_date is not None:
        stage.end_date = datetime.fromisoformat(end_date).astimezone(pytz.UTC)

    db.commit()
    db.refresh(stage)
    return stage
