from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from datetime import datetime
from sql_app.database import Base


class Feature(Base):
    __tablename__ = 'features'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    jira_key = Column(String, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    release_id = Column(Integer, ForeignKey('releases.id', ondelete='CASCADE'), nullable=False)
    feature_type_id = Column(Integer, nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=False)


class FeatureType(Base):
    __tablename__ = 'feature_types'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)


class FeatureTypeTaskType(Base):
    __tablename__ = 'feature_type_task_types'

    id = Column(Integer, primary_key=True, index=True)
    feature_type_id = Column(Integer, ForeignKey('feature_types.id'), nullable=False)
    task_type_id = Column(Integer, ForeignKey('task_types.id'), nullable=False)
