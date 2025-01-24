from sqlalchemy import select, func, delete, update
from sqlalchemy.orm import Session

from sql_app.models.features import FeatureType, FeatureTypeTaskType, Feature
from sql_app.models.task import TaskType, Task, AttachmentLink


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


def get_features(db: Session,
                 feature_id: int | None = None,
                 feature_name: str | None = None,
                 user_id: int | None = None
                 ):
    task_attachments = select(AttachmentLink.id,
                              AttachmentLink.link,
                              AttachmentLink.uploaded_at,
                              AttachmentLink.uploaded_by).label('attachments')
    task_attachments_cte = task_attachments.cte('task_attachments_cte')
    stmt = select(Feature, func.array_agg(func.json_build_object('id', Task.id,
                                                                 'feature_id', Task.feature_id,
                                                                 'task_type_id', Task.task_type_id,
                                                                 'status', Task.status,
                                                                 'attachments', task_attachments_cte)).label('tasks'))
    stmt = stmt.join(Task, Task.feature_id == Feature.id)
    stmt = stmt.join(task_attachments_cte, task_attachments_cte.c.task_id == Task.id, isouter=True)
    if feature_id:
        stmt = stmt.where(Feature.id == feature_id)
    if feature_name:
        stmt = stmt.where(func.lower(Feature.name).like(f'%{feature_name.lower()}%'))
    if user_id:
        stmt = stmt.where(Feature.creator_id == user_id)
    stmt = stmt.group_by(Feature.id)
    return db.execute(stmt).mappings().all()


def get_feature(feature_id: int, db: Session) -> Feature:
    stmt = select(Feature).where(Feature.id == feature_id)
    return db.execute(stmt).scalar_one_or_none()


def create_feature(user_id: int, name: str, feature_type_id: int, release_id: int, status: str, db: Session):
    feature = Feature(creator_id=user_id,
                      name=name,
                      feature_type_id=feature_type_id,
                      release_id=release_id,
                      status=status)
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return feature


def update_feature(db: Session,
                   feature_id: int | None = None,
                   name: str | None = None,
                   feature_type_id: int | None = None,
                   release_id: int | None = None,
                   status: str | None = None
                   ):
    stmt = update(Feature).where(Feature.id == feature_id)
    if name:
        stmt = stmt.values(name=name)
    if feature_type_id:
        stmt = stmt.values(feature_type_id=feature_type_id)
    if release_id:
        stmt = stmt.values(release_id=release_id)
    if status:
        stmt = stmt.values(status=status)
    stmt = stmt.returning(Feature)
    result = db.execute(stmt).scalar_one()
    db.commit()
    return result
