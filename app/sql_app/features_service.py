from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session

from sql_app.models.features import FeatureType, FeatureTypeTaskType, Feature
from sql_app.models.tasks import TaskType, Tasks


def get_feature_type(db: Session, name: str | None = None, feature_type_id: int | None = None):
    stmt = select(FeatureType, func.array_agg(func.json_build_object('id', TaskType.id,
                                                                     'key_name', TaskType.key_name,
                                                                     'name', TaskType.name,
                                                                     'description', TaskType.description,
                                                                     'is_required', TaskType.is_required)).label(
        'task_types'))
    stmt = stmt.join(FeatureTypeTaskType, FeatureTypeTaskType.feature_type_id == FeatureType.id)
    stmt = stmt.join(TaskType, TaskType.id == FeatureTypeTaskType.task_type_id)
    stmt = stmt.group_by(FeatureType.id)
    if name:
        stmt = stmt.where(FeatureType.name == name)
    if feature_type_id:
        stmt = stmt.where(FeatureType.id == feature_type_id)

    return db.execute(stmt).mappings().all()


def create_feature_type(name: str, description: str, db: Session):
    feature_type = FeatureType(name=name, description=description)
    db.add(feature_type)
    db.commit()
    db.refresh(feature_type)
    return feature_type


def delete_feature_type(feature_type_id: int, db: Session):
    stmt = delete(FeatureType).where(FeatureType.id == feature_type_id).returning(FeatureType)
    db.execute(stmt)
    db.commit()
    return None


def get_features(db: Session, feature_id: int | None = None, feature_name: str | None = None):
    stmt = select(FeatureType, func.array_agg(func.json_build_object('id', Tasks.id,
                                                                     'feature_id', Tasks.feature_id,
                                                                     'task_type_id', Tasks.task_type_id,
                                                                     'status', Tasks.status)).label('tasks'))
    if feature_id:
        stmt = stmt.where(FeatureType.id == feature_id)
    if feature_name:
        stmt = stmt.where(func.lower(FeatureType.name).like(f'%{feature_name.lower()}%'))
    stmt = stmt.group_by(FeatureType.id)
    if feature_id or feature_name:
        return db.execute(stmt).one_or_none()
    return db.execute(stmt).mappings().all()


def create_feature(name: str, feature_type_id: int, release_id: int, status: str, db: Session):
    feature = Feature(name=name, feature_type_id=feature_type_id, release_id=release_id, status=status)
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return feature

