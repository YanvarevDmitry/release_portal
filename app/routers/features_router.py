from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from schemas import User, FeatureTypeOut, FeatureTypeCreate, FeatureOut, FeatureCreate
from sql_app import features_service, releases_service, tasks_service
from sql_app.database import get_database
from sql_app.models.user import RolesEnum

router = APIRouter(prefix="/feature", tags=["features"])
get_current_user = Annotated[User, Depends(get_current_user)]
db_session = Annotated[Session, Depends(get_database)]


@router.post("/types", response_model=FeatureTypeOut, status_code=201)
def create_feature_type(feature: FeatureTypeCreate,
                        current_user: get_current_user,
                        db: db_session):
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if features_service.get_feature_type(name=feature.name, db=db):
        raise HTTPException(status_code=400, detail="Feature with this name already exists")
    return features_service.create_feature_type(name=feature.name,
                                                description=feature.description,
                                                db=db)


@router.get("/types/{feature_type_id}", status_code=200)
def get_feature_type(feature_type_id: int, db: db_session):
    return features_service.get_feature_type(feature_type_id=feature_type_id, db=db)


@router.delete("/types/{feature_type_id}", status_code=204)
def delete_feature_type(feature_type_id: int, current_user: get_current_user, db: db_session):
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not features_service.get_feature_type(feature_type_id=feature_type_id, db=db):
        raise HTTPException(status_code=404, detail="Feature type not found")
    return features_service.delete_feature_type(feature_type_id=feature_type_id, db=db)


@router.get('/', response_model=list[FeatureOut], status_code=200)
def get_all_features(db: db_session):
    return features_service.get_features(db=db)


@router.post('/', response_model=FeatureOut, status_code=201)
def create_feature(feature: FeatureCreate, db: db_session):
    if not features_service.get_features(feature_name=feature.name, db=db):
        raise HTTPException(status_code=400, detail="Feature with this name already exists")
    if not releases_service.get_release(release_id=feature.release_id, db=db):
        raise HTTPException(status_code=404, detail="Release not found")
    feature = features_service.create_feature(name=feature.name,
                                              feature_type_id=feature.feature_type_id,
                                              release_id=feature.release_id,
                                              status=feature.status, db=db)
    task_types = tasks_service.get_task_type_for_feature_type(db=db, feature_type_id=feature.feature_type_id)
    for task_type in task_types:
        tasks_service.create_task(feature_id=feature.id, task_type_id=task_type.id, status='created', db=db)
    return features_service.get_features(feature_id=feature.id, db=db)
