from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func

from sql_app.database import Base


class TaskType(Base):
    __tablename__ = 'task_types'

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_required = Column(Boolean, nullable=False, server_default='true')


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey('features.id', ondelete='CASCADE'), nullable=False)
    task_type_id = Column(Integer, ForeignKey('task_types.id'), nullable=False)
    status = Column(String, nullable=False)


class AttachmentLink(Base):
    __tablename__ = 'attachment_links'

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    link = Column(String, nullable=False)
    uploaded_at = Column(DateTime, nullable=False, server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=False)


class TaskTypeApprover(Base):
    __tablename__ = 'task_type_approvers'

    task_type_id = Column(Integer, ForeignKey('task_types.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, primary_key=True)

