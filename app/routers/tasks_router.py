from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from schemas import User, TaskTypeOut, TaskTypeCreate
from sql_app import tasks_service
from sql_app.database import get_database
from sql_app.models.user import RolesEnum

router = APIRouter(prefix="/tasks", tags=["tasks"])
get_current_user = Annotated[User, Depends(get_current_user)]
db_session = Annotated[Session, Depends(get_database)]


@router.post("/types", response_model=TaskTypeOut, status_code=201)
def create_task_type(task: TaskTypeCreate,
                     current_user: get_current_user,
                     db: db_session):
    """
    Создание нового типа задачи.

    Args:
        task (TaskTypeCreate): Данные типа задачи для создания.
        current_user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если у пользователя нет прав администратора или менеджера релизов.
        HTTPException: Если тип задачи с таким ключевым именем уже существует.

    Returns:
        TaskTypeOut: Созданный тип задачи.
    """
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if tasks_service.get_task_type(key_name=task.key_name, db=db):
        raise HTTPException(status_code=400, detail="Task with this name already exists")
    return tasks_service.create_task_type(key_name=task.key_name,
                                          name=task.name,
                                          description=task.description,
                                          is_required=task.is_required,
                                          db=db)


@router.get("/types", response_model=TaskTypeOut, status_code=200)
def get_task_type(key_name: str, db: db_session):
    """
    Получение типа задачи по ключевому имени.

    Args:
        key_name (str): Ключевое имя типа задачи.
        db (Session): Сессия базы данных.

    Returns:
        TaskTypeOut: Тип задачи с указанным ключевым именем.
    """
    return tasks_service.get_task_type(key_name=key_name, db=db)


@router.get("/types/all", response_model=list[TaskTypeOut], status_code=200)
def get_all_task_type(db: db_session):
    """
    Получение всех типов задач.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        list[TaskTypeOut]: Список всех типов задач.
    """
    return tasks_service.get_all_task_types(db=db)


@router.delete("/types/{task_type_id}", status_code=204)
def delete_task_type(task_type_id: int, current_user: get_current_user, db: db_session):
    """
    Удаление типа задачи по ID.

    Args:
        task_type_id (int): ID типа задачи для удаления.
        current_user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если у пользователя нет прав администратора или менеджера релизов.
        HTTPException: Если тип задачи не найден.

    Returns:
        None
    """
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not tasks_service.get_task_type(id=task_type_id, db=db):
        raise HTTPException(status_code=404, detail="Task type not found")
    return tasks_service.delete_task_type(task_type_id=task_type_id, db=db)


@router.get('/', response_model=list[TaskTypeOut], status_code=200)
def get_all_tasks(db: db_session,
                  feature_id: int | None = None,
                  feature_name: str | None = None,
                  key_name: str | None = None):
    """
    Получение всех задач, с возможностью фильтрации по ID фичи, имени фичи или ключевому имени.

    Args:
        db (Session): Сессия базы данных.
        feature_id (int, optional): ID фичи для фильтрации задач.
        feature_name (str, optional): Имя фичи для фильтрации задач.
        key_name (str, optional): Ключевое имя для фильтрации задач.

    Returns:
        list[TaskTypeOut]: Список всех задач, соответствующих указанным фильтрам.
    """
    task_types = tasks_service.get_all_tasks(db=db, feature_name=feature_name, feature_id=feature_id, key_name=key_name)
    return task_types