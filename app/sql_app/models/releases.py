import enum

from sqlalchemy import Column, Integer, String, Date, Enum, DateTime, func, ForeignKey

from sql_app.database import Base


class ReleaseStageEnum(enum.Enum):
    open = "open"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


class Release(Base):
    __tablename__ = "releases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(Enum(ReleaseStageEnum), default='open')
    description = Column(String)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    platform_id = Column(Integer, ForeignKey('platforms.id', ondelete='CASCADE'), nullable=False)
    channel_id = Column(Integer, ForeignKey('channels.id', ondelete='CASCADE'), nullable=False)
    release_type_id = Column(Integer, ForeignKey('release_types.id', ondelete='CASCADE'), nullable=False)


class ReleaseType(Base):
    __tablename__ = "release_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    platform_id = Column(Integer, ForeignKey('platforms.id', ondelete='CASCADE'), nullable=False)
    channel_id = Column(Integer, ForeignKey('channels.id', ondelete='CASCADE'), nullable=False)
