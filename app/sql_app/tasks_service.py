from sqlalchemy import select, delete, func, and_, update, insert
from sqlalchemy.orm import Session

from sql_app.models.features import FeatureTypeTaskType, Feature, FeatureType
from sql_app.models.task import TaskType, Task, AttachmentLink, TaskTypeApprover, TaskComment
from sql_app.models.user import Role


def get_task_type(db: Session, key_name: str | None = None, id: int | None = None):
    stmt = select(TaskType)
    if key_name:
        stmt = stmt.where(TaskType.key_name == key_name)
    if id:
        stmt = stmt.where(TaskType.id == id)
    return db.execute(stmt).scalar_one_or_none()


def create_task_type(db: Session,
                     key_name: str,
                     name: str,
                     description: str,
                     is_required: bool | None = True):
    task_type = TaskType(key_name=key_name,
                         name=name,
                         description=description,
                         is_required=is_required,
                         )
    db.add(task_type)
    db.commit()
    db.refresh(task_type)
    return task_type


def delete_task_type(task_type_id: int, db: Session):
    stmt = delete(TaskType).where(TaskType.id == task_type_id).returning(TaskType)
    db.execute(stmt)
    db.commit()
    return None


def get_all_task_types(db: Session,
                       feature_id: int | None = None,
                       feature_name: str | None = None,
                       key_name: str | None = None):
    stmt = select(TaskType)
    if feature_id or feature_name:
        stmt = stmt.join(FeatureTypeTaskType, FeatureTypeTaskType.task_type_id == TaskType.id)
        stmt = stmt.join(FeatureType, FeatureTypeTaskType.feature_type_id == FeatureType.id)
        stmt = stmt.join(Feature, FeatureType.id == Feature.feature_type_id)
    if feature_id:
        stmt = stmt.where(Feature.id == feature_id)
    if feature_name:
        stmt = stmt.where(func.lower(Feature.name).like(f'%{feature_name.lower()}%'))
    if key_name:
        stmt = stmt.where(TaskType.key_name == key_name)
    return db.execute(stmt).scalars().all()


def get_task_type_for_feature_type(db: Session, feature_type_id: int):
    stmt = select(TaskType)
    stmt = stmt.join(FeatureTypeTaskType, FeatureTypeTaskType.task_type_id == TaskType.id)
    stmt = stmt.where(FeatureTypeTaskType.feature_type_id == feature_type_id)
    return db.execute(stmt).scalars().all()


def create_task(feature_id: int, task_type_id: int, status: str, db: Session):
    task = Task(feature_id=feature_id, task_type_id=task_type_id, status=status)
    db.add(task)
    db.commit()
    db.refresh(task)
    return None


def get_task_for_feature(db: Session, feature_id: int):
    stmt = select(Task, func.json_build_object('id', TaskType.id,
                                               'key_name', TaskType.key_name,
                                               'name', TaskType.name,
                                               'description', TaskType.description,
                                               'is_required', TaskType.is_required).label(
        'task_type'))
    stmt = stmt.join(TaskType, TaskType.id == Task.task_type_id)
    stmt = stmt.where(Task.feature_id == feature_id)
    stmt = stmt.group_by(Task.id, TaskType.id)
    return db.execute(stmt).all()


def delete_task(feature_id: int, task_type_id: int, db: Session):
    stmt = delete(Task).where(and_(Task.feature_id == feature_id,
                                   Task.task_type_id == task_type_id)).returning(Task)
    db.execute(stmt)
    db.commit()
    return None


def update_task(task_id: int, status: str, db: Session):
    stmt = update(Task).where(Task.id == task_id).values(status=status).returning(Task)
    result = db.execute(stmt).scalar()
    db.commit()
    return result


def get_task(task_id: int, db: Session):
    stmt = select(Task).where(Task.id == task_id)
    return db.execute(stmt).scalar_one_or_none()


def create_attachment(task_id: int, link: str, user_id: int, db: Session):
    stmt = insert(AttachmentLink).values(task_id=task_id, link=link, uploaded_by=user_id).returning(AttachmentLink)
    attachment = db.execute(stmt).scalar()
    db.commit()
    return attachment


def get_task_type_approver(task_type_id: int, db: Session):
    stmt = select(TaskTypeApprover.task_type_id, Role.name.label('role_name'))
    stmt = stmt.join(Role, Role.id == TaskTypeApprover.role_id)
    stmt = stmt.where(TaskTypeApprover.task_type_id == task_type_id)
    return db.execute(stmt).one_or_none()


def create_task_type_approver(task_type_id: int, role_id: int, db):
    stmt = insert(TaskTypeApprover).values(task_type_id=task_type_id, role_id=role_id).returning(TaskTypeApprover)
    approver = db.execute(stmt).scalar()
    db.commit()
    return approver


def add_comment(task_id: int, comment: str, user_id: int, db: Session):
    stmt = insert(TaskComment).values(task_id=task_id, comment=comment, user_id=user_id).returning(TaskComment)
    comment = db.execute(stmt).scalar()
    db.commit()
    return comment


def get_comments(task_id: int, db: Session):
    stmt = select(TaskComment)
    stmt = stmt.where(TaskComment.task_id == task_id)
    return db.execute(stmt).scalars().all()
