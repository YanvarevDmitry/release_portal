from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import get_current_user
from schemas import User, FeatureTypeOut, FeatureTypeCreate, FeatureCreate, FeatureOut, PaginationFeatures
from sql_app import features_service, releases_service, tasks_service
from sql_app.database import get_database
from sql_app.models.user import RolesEnum
import logg_config

logger = logg_config.get_logger(__name__)

router = APIRouter(prefix="/feature", tags=["features"])
get_current_user = Annotated[User, Depends(get_current_user)]
db_session = Annotated[Session, Depends(get_database)]


@router.post("/types", response_model=FeatureTypeOut, status_code=201)
def create_feature_type(feature: FeatureTypeCreate,
                        current_user: get_current_user,
                        db: db_session):
    """
    Создание нового типа фичи.

    Args:
        feature (FeatureTypeCreate): Данные типа фичи для создания.
        current_user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если у пользователя нет прав администратора или менеджера релизов.
        HTTPException: Если тип фичи с таким именем уже существует.

    Returns:
        FeatureTypeOut: Созданный тип фичи.
    """
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        logger.warning("User %s does not have enough permissions", current_user.username)
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if features_service.get_feature_type(name=feature.name, db=db):
        logger.warning("Feature type with name %s already exists", feature.name)
        raise HTTPException(status_code=400, detail="Feature with this name already exists")
    logger.info("User %s create new feature type: %s ", current_user.username, feature.name)
    return features_service.create_feature_type(name=feature.name,
                                                description=feature.description,
                                                db=db)


@router.get("/types/{feature_type_id}", status_code=200)
def get_feature_type(feature_type_id: int, db: db_session):
    """
    Получение типа фичи по ID.

    Args:
        feature_type_id (int): ID типа фичи.
        db (Session): Сессия базы данных.

    Returns:
        FeatureTypeOut: Тип фичи с указанным ID.
    """
    logger.info("Getting feature type with ID: %d", feature_type_id)
    types = features_service.get_feature_type(feature_type_id=feature_type_id, db=db)
    return types


@router.delete("/types/{feature_type_id}", status_code=204)
def delete_feature_type(feature_type_id: int, current_user: get_current_user, db: db_session):
    """
    Удаление типа фичи по ID.

    Args:
        feature_type_id (int): ID типа фичи для удаления.
        current_user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если у пользователя нет прав администратора или менеджера релизов.
        HTTPException: Если тип фичи не найден.

    Returns:
        None
    """
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        logger.warning("User %s does not have enough permissions", current_user.username)
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not features_service.get_feature_type(feature_type_id=feature_type_id, db=db):
        logger.warning("Feature type with ID %d not found", feature_type_id)
        raise HTTPException(status_code=404, detail="Feature type not found")
    logger.info("User %s delete feature type with ID: %d", current_user.username, feature_type_id)
    return features_service.delete_feature_type(feature_type_id=feature_type_id, db=db)


@router.get('/all/', status_code=200)
def get_all_features(db: db_session,
                     user_id: int | None = None,
                     page: int = 1,
                     page_size: int = 50):
    """
    Получение всех фич.

    Args:
        db (Session): Сессия базы данных.
        user_id (int, optional): ID пользователя для фильтрации фич.
        page: (int, optional): Номер страницы.
        page_size: (int, optional): Размер страницы.

    Returns:
        list[FeatureOut]: Список всех фич.
    """
    logger.info("Getting all features")
    data, page_size, total = features_service.get_all_features_pagination(db=db,
                                                                          page=page,
                                                                          page_size=page_size,
                                                                          user_id=user_id)

    return {'data': data,
            'page_size': page_size,
            'total': total
            }


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
    logger.info("Getting feature with ID: %s or name: %s", feature_id, feature_name)
    feature = features_service.get_features(feature_id=feature_id, feature_name=feature_name, db=db)
    if not feature:
        logger.warning("Feature not found with ID: %s or name: %s", feature_id, feature_name)
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature[0]


@router.post('/', status_code=201)
def create_feature(feature: FeatureCreate, user: get_current_user, db: db_session):
    """
    Создание новой фичи.

    Args:
        feature (FeatureCreate): Данные фичи для создания.
        user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если фича с таким именем уже существует.
        HTTPException: Если релиз не найден.

    Returns:
        FeatureOut: Созданная фича.
    """
    if features_service.get_features(feature_name=feature.name, db=db):
        logger.warning("Feature with name %s already exists", feature.name)
        raise HTTPException(status_code=400, detail="Feature with this name already exists")
    if not releases_service.get_release(release_id=feature.release_id, db=db):
        logger.warning("Release not found with ID: %d", feature.release_id)
        raise HTTPException(status_code=404, detail="Release not found")
    if not features_service.get_feature_type(feature_type_id=feature.feature_type_id, db=db):
        logger.warning("Feature type not found with ID: %d", feature.feature_type_id)
        raise HTTPException(status_code=404, detail="Feature type not found")
    feature = features_service.create_feature(name=feature.name,
                                              user_id=user.id,
                                              feature_type_id=feature.feature_type_id,
                                              release_id=feature.release_id,
                                              status=feature.status, db=db)
    task_types = tasks_service.get_task_type_for_feature_type(db=db, feature_type_id=feature.feature_type_id)
    for task_type in task_types:
        tasks_service.create_task(feature_id=feature.id, task_type_id=task_type.id, status='open', db=db)
    logger.info("User %s create feature with name: %s, and ID: %d", user.username, feature.name, feature.id)
    return features_service.get_features(feature_id=feature.id, db=db)


@router.patch('/{feature_id}/type/{feature_type_id}', response_model=FeatureOut, status_code=200)
def change_feature_type(feature_id: int, feature_type_id: int, user: get_current_user, db: db_session):
    """
    Изменение типа фичи.
    Args:
        feature_id (int): ID фичи.
        feature_type_id (int): ID типа фичи.
        user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.
    Exceptions:
        HTTPException: Если фича не найдена.
        HTTPException: Если тип фичи не найден.

    Returns:
        FeatureOut:  Измененная фича.
    """
    feature = features_service.get_feature(feature_id=feature_id, db=db)
    if not feature:
        logger.warning("Feature not found with ID: %d", feature_id)
        raise HTTPException(status_code=404, detail="Feature not found")
    # Проверим что фича не закрыта
    if feature.status == 'done':
        logger.warning("Feature is done")
        raise HTTPException(status_code=400, detail="Feature is done. Cant change feature type")
    if not features_service.get_feature_type(feature_type_id=feature_type_id, db=db):
        logger.warning("Feature type not found with ID: %d", feature_type_id)
        raise HTTPException(status_code=404, detail="Feature type not found")
    # Проверим что пытается поменять либо создатель фичи, либо менеджер и админ.
    if feature.creator_id != user.id:
        if user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    # Проверим, что нет закрытых доров
    tasks = tasks_service.get_task_for_feature(feature_id=feature_id, db=db)
    for task in tasks:
        if task.Task.status == 'done':
            task_name = task.task_type.get('name')
            logger.warning("Task %s is done", task_name)
            raise HTTPException(status_code=400, detail=f"Task {task_name} is done. Cant change feature type")

    # Проверим какие Таски надо удалить и создать новые
    new_task_types = tasks_service.get_task_type_for_feature_type(db=db, feature_type_id=feature_type_id)
    old_task_types = tasks_service.get_task_type_for_feature_type(feature_type_id=feature.feature_type_id, db=db)
    new_task_types_id = [task.id for task in new_task_types]
    old_task_types_id = [task.id for task in old_task_types]
    tasks_to_delete = list(set(old_task_types_id) - set(new_task_types_id))
    tasks_to_create = list(set(new_task_types_id) - set(old_task_types_id))
    for task_id in tasks_to_delete:
        tasks_service.delete_task(feature_id=feature_id, task_type_id=task_id, db=db)
    for task_id in tasks_to_create:
        if task_id not in [task.Task.task_type_id for task in tasks]:
            tasks_service.create_task(feature_id=feature_id, task_type_id=task_id, status='open', db=db)
    logger.info('User %s change feature %d type to %d', user.username, feature_id, feature_type_id)
    return features_service.update_feature(feature_id=feature_id, feature_type_id=feature_type_id, db=db)


@router.patch('/{feature_id}/release/{release_id}', response_model=FeatureOut, status_code=200)
def change_feature_release(feature_id: int, release_id: int, user: get_current_user, db: db_session):
    """
    Изменение релиза фичи.
    Args:
        feature_id (int): ID фичи.
        release_id (int): ID релиза.
        user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.
    Exceptions:
        HTTPException: Если фича не найдена.
        HTTPException: Если релиз не найден.

    Returns:
        FeatureOut:  Измененная фича.
    """
    feature = features_service.get_feature(feature_id=feature_id, db=db)
    if not feature:
        logger.warning("Feature not found with ID: %d", feature_id)
        raise HTTPException(status_code=404, detail="Feature not found")
    if release_id == feature.release_id:
        return feature
    release = releases_service.get_release(release_id=release_id, db=db)
    if not release:
        logger.warning("Release not found with ID: %d", release_id)
        raise HTTPException(status_code=404, detail="Release not found")
    if release.status == 'done':
        logger.warning("Release is done")
        raise HTTPException(status_code=400, detail="Release is done. Cant change feature release")
    if feature.status == 'done':
        logger.warning("Feature is done")
        raise HTTPException(status_code=400, detail="Feature is done. Cant change feature release")
    if feature.creator_id != user.id:
        if user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    feature = features_service.update_feature(feature_id=feature_id, release_id=release_id, db=db)
    logger.info("User %s move feature %d to enw release %d", user.username, feature_id, release_id)
    return feature
