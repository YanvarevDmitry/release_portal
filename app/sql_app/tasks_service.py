from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session

from sql_app.models.features import FeatureTypeTaskType, Feature, FeatureType
from sql_app.models.tasks import TaskType, Tasks


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
    task = Tasks(feature_id=feature_id, task_type_id=task_type_id, status=status)
    db.add(task)
    db.commit()
    db.refresh(task)
    return None


def get_task_for_feature(db: Session, feature_id: int):
    stmt = select(Tasks, func.array_agg(func.json_build_object('id', TaskType.id,
                                                               'key_name', TaskType.key_name,
                                                               'name', TaskType.name,
                                                               'description', TaskType.description,
                                                               'is_required', TaskType.is_required)).label(
        'task_type'))
    stmt = stmt.join(TaskType, TaskType.id == Tasks.task_type_id)
    stmt = stmt.where(Tasks.feature_id == feature_id)
    stmt = stmt.gtpup_by(Tasks.id)
    return db.execute(stmt).all()


def delete_task(task_id: int, db: Session):
    stmt = delete(Tasks).where(Tasks.id == task_id).returning(Tasks)
    db.execute(stmt)
    db.commit()
    return None
