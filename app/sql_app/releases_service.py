from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select, delete
import pytz
from sqlalchemy.orm import Session

from schemas import ReleaseStageCreate
from sql_app.models.releases import ReleaseStage, ReleaseType


def create_release_stage(stage: ReleaseStageCreate, db) -> ReleaseStage:
    db_stage = ReleaseStage(**stage.dict())
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage


def get_all_releases(db) -> list[ReleaseStage]:
    return db.execute(select(ReleaseStage)).scalars().all()


def get_release(db: Session, name: str | None = None, release_id: int | None = None):
    stmt = select(ReleaseStage)
    if name:
        stmt = stmt.where(ReleaseStage.name == name)
    if release_id:
        stmt = stmt.where(ReleaseStage.id == release_id)
    return db.execute(stmt).scalar_one_or_none()


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


def delete_release_stage(stage_id: int, db: Session):
    stmt = delete(ReleaseStage).where(ReleaseStage.id == stage_id).returning(ReleaseStage)
    release = db.execute(stmt).one()
    db.commit()
    return release


def get_all_release_types(db: Session):
    return db.execute(select(ReleaseType)).scalars().all()


def create_release_type(name: str, platform_id: int, channel_id: int, db: Session):
    release_type = ReleaseType(name=name, platform_id=platform_id, channel_id=channel_id)
    db.add(release_type)
    db.commit()
    db.refresh(release_type)
    return release_type


def delete_release_type(release_type_id: int, db: Session):
    stmt = delete(ReleaseType).where(ReleaseType.id == release_type_id).returning(ReleaseType)
    release_type = db.execute(stmt).one()
    db.commit()
    return release_type
