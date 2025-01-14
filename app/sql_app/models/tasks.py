from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from sql_app.database import Base


class TaskType(Base):
    __tablename__ = 'task_types'

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_required = Column(Boolean, nullable=False, server_default='true')


class Tasks(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey('features.id'), nullable=False)
    task_type_id = Column(Integer, ForeignKey('task_types.id'), nullable=False)
    status = Column(String, nullable=False)
