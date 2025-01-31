from sqlalchemy import select, insert
from sqlalchemy.orm import Session
from sql_app.models.platforms import Platform


def create_platform(name: str, db: Session):
    stmt = insert(Platform).values(name=name).returning(Platform)
    platform = db.execute(stmt).scalar()
    return platform


def get_platform(db: Session, platform_id: int | None = None, name: str | None = None):
    stmt = select(Platform)
    if platform_id:
        stmt = stmt.where(Platform.id == platform_id)
    if name:
        stmt = stmt.where(Platform.name == name)
    return db.execute(stmt).scalar_one_or_none()


def get_all_platforms(db: Session):
    stmt = select(Platform)
    return db.execute(stmt).scalars().all()
