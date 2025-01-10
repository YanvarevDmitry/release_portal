import enum

from sqlalchemy import Column, Integer, String, Date, Enum

from app.sql_app.database import Base


class ReleaseStageEnum(enum.Enum):
    created = "created"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


class ReleaseStage(Base):
    __tablename__ = "release_stages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    staged = Column(Enum(ReleaseStageEnum), default='created')
    description = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    responsible_person = Column(String)
