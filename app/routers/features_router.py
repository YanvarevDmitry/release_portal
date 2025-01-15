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
    """
    Создание нового типа доработки.

    Args:
        feature (FeatureTypeCreate): Данные типа доработки для создания.
        current_user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если у пользователя нет прав администратора или менеджера релизов.
        HTTPException: Если тип доработки с таким именем уже существует.

    Returns:
        FeatureTypeOut: Созданный тип доработки.
    """
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if features_service.get_feature_type(name=feature.name, db=db):
        raise HTTPException(status_code=400, detail="Feature with this name already exists")
    return features_service.create_feature_type(name=feature.name,
                                                description=feature.description,
                                                db=db)


@router.get("/types/{feature_type_id}", status_code=200)
def get_feature_type(feature_type_id: int, db: db_session):
    """
    Получение типа доработки по ID.

    Args:
        feature_type_id (int): ID типа доработки.
        db (Session): Сессия базы данных.

    Returns:
        FeatureTypeOut: тип доработки с указанным ID.
    """
    types = features_service.get_feature_type(feature_type_id=feature_type_id, db=db)
    return types


@router.delete("/types/{feature_type_id}", status_code=204)
def delete_feature_type(feature_type_id: int, current_user: get_current_user, db: db_session):
    """
    Удаление типа доработки по ID.

    Args:
        feature_type_id (int): ID типа доработки для удаления.
        current_user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если у пользователя нет прав администратора или менеджера релизов.
        HTTPException: Если тип доработки не найден.

    Returns:
        None
    """
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not features_service.get_feature_type(feature_type_id=feature_type_id, db=db):
        raise HTTPException(status_code=404, detail="Feature type not found")
    return features_service.delete_feature_type(feature_type_id=feature_type_id, db=db)


@router.get('/', status_code=200)
def get_all_features(db: db_session):
    """
    Получение всех фич.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        list[FeatureOut]: Список всех фич.
    """
    return features_service.get_features(db=db)


@router.get("/", status_code=200)
def get_feature(db: db_session, feature_id: int | None = None, feature_name: str | None = None):
    """
    Получение фичи по ID или имени.

    Args:
        db (Session): Сессия базы данных.
        feature_id (int, optional): ID фичи.
        feature_name (str, optional): Имя фичи.

    Exceptions:
        HTTPException: Если фича не найдена.

    Returns:
        FeatureOut: Фича с указанным ID или именем.
    """
    feature = features_service.get_features(feature_id=feature_id, feature_name=feature_name, db=db)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature[0]


@router.post('/', status_code=201)
def create_feature(feature: FeatureCreate, db: db_session):
    """
    Создание новой фичи.

    Args:
        feature (FeatureCreate): Данные фичи для создания.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если фича с таким именем уже существует.
        HTTPException: Если релиз не найден.

    Returns:
        FeatureOut: Созданная фича.
    """
    if features_service.get_features(feature_name=feature.name, db=db):
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