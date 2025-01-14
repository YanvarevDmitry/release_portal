from sqlalchemy import select
from sqlalchemy.orm import Session
from sql_app.models.channels import Channel


def create_channel(name: str, db: Session):
    channel = Channel(name=name)
    db.add(Channel)
    db.commit()
    db.refresh(channel)
    return channel


def get_channel(db: Session, channel_id: int | None = None, name: str | None = None):
    stmt = select(Channel)
    if channel_id is not None:
        stmt = stmt.where(Channel.id == channel_id)
    if name is not None:
        stmt = stmt.where(Channel.name == name)
    return db.execute(stmt).scalar_one_or_none()


def get_all_channels(db: Session):
    stmt = select(Channel)
    return db.execute(stmt).scalars().all()
