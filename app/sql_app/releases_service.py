from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select, delete, func
import pytz
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce

from schemas import ReleaseStageCreate
from sql_app.models.features import Feature
from sql_app.models.releases import Release, ReleaseType


def create_release(stage: ReleaseStageCreate, db) -> Release:
    db_stage = Release(**stage.dict())
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage


def get_all_releases(db: Session,
                     page: int,
                     page_size: int,
                     platform_id: int | None = None,
                     channel_id: int | None = None,
                     ):
    stmt = select(Release, coalesce(func.array_agg(func.json_build_object('id', Feature.id,
                                                                          'name', Feature.name,
                                                                          'feature_type_id', Feature.feature_type_id,
                                                                          'status', Feature.status,
                                                                          )).filter(Feature.id.isnot(None)),
                                    '{}').label('features'))
    stmt = stmt.join(Feature, Feature.release_id == Release.id, isouter=True)
    if platform_id:
        stmt = stmt.where(Release.platform_id == platform_id)
    if channel_id:
        stmt = stmt.where(Release.channel_id == channel_id)
    if page == 0:
        page = 1
    if page_size == 0:
        page_size = 50
    stmt = stmt.group_by(Release.id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    stmt = stmt.offset((page - 1) * page_size)
    stmt = stmt.limit(page_size)
    result = db.execute(stmt).mappings().all()

    return result, len(result), total


def get_release(db: Session, name: str | None = None, release_id: int | None = None):
    stmt = select(Release)
    if name:
        stmt = stmt.where(Release.name == name)
    if release_id is not None:
        stmt = stmt.where(Release.id == release_id)
    return db.execute(stmt).scalar_one_or_none()


def update_release(stage_id: int,
                   name: str | None,
                   description: str | None,
                   start_date: str | None,
                   end_date: str | None,
                   db: Session):
    stage = db.query(Release).filter(Release.id == stage_id).first()
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


def delete_release(stage_id: int, db: Session):
    stmt = delete(Release).where(Release.id == stage_id).returning(Release)
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


def get_release_with_features(release_id: int, db: Session):
    stmt = select(Release, coalesce(func.array_agg(func.json_build_object('id', Feature.id,
                                                                          'name', Feature.name,
                                                                          'feature_type_id', Feature.feature_type_id,
                                                                          'status', Feature.status,
                                                                          )).filter(Feature.id.isnot(None)),
                                    '{}').label('features'))
    stmt = stmt.join(Feature, Feature.release_id == Release.id, isouter=True)
    stmt = stmt.where(Release.id == release_id)
    stmt = stmt.group_by(Release.id)
    return db.execute(stmt).one()
