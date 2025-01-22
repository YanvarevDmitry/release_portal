from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from schemas import User, TaskTypeOut, TaskTypeCreate
from sql_app import tasks_service
from sql_app.database import get_database
from sql_app.models.user import RolesEnum
import logg_config

logger = logg_config.get_logger(__name__)
router = APIRouter(prefix="/tasks", tags=["tasks"])
get_current_user = Annotated[User, Depends(get_current_user)]
db_session = Annotated[Session, Depends(get_database)]


@router.post("/types", response_model=TaskTypeOut, status_code=201)
def create_task_type(task: TaskTypeCreate,
                     current_user: get_current_user,
                     db: db_session):
    logger.info("User %s is attempting to create a new task type: %s", current_user.username, task.key_name)
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        logger.warning("User %s does not have enough permissions", current_user.username)
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if tasks_service.get_task_type(key_name=task.key_name, db=db):
        logger.warning("Task type with key name %s already exists", task.key_name)
        raise HTTPException(status_code=400, detail="Task with this name already exists")
    new_task_type = tasks_service.create_task_type(key_name=task.key_name,
                                                   name=task.name,
                                                   description=task.description,
                                                   is_required=task.is_required,
                                                   db=db)
    logger.info("Task type %s created successfully by user %s", task.key_name, current_user.username)
    return new_task_type


@router.get("/types", response_model=TaskTypeOut, status_code=200)
def get_task_type(key_name: str, db: db_session):
    logger.info("Fetching task type with key name: %s", key_name)
    task_type = tasks_service.get_task_type(key_name=key_name, db=db)
    if not task_type:
        logger.warning("Task type not found with key name: %s", key_name)
        raise HTTPException(status_code=404, detail="Task type not found")
    return task_type


@router.get("/types/all", response_model=list[TaskTypeOut], status_code=200)
def get_all_task_type(db: db_session):
    logger.info("Fetching all task types")
    task_types = tasks_service.get_all_task_types(db=db)
    logger.info("Fetched %d task types", len(task_types))
    return task_types


@router.delete("/types/{task_type_id}", status_code=204)
def delete_task_type(task_type_id: int, current_user: get_current_user, db: db_session):
    logger.info("User %s is attempting to delete task type with ID: %d", current_user.username, task_type_id)
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        logger.warning("User %s does not have enough permissions", current_user.username)
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not tasks_service.get_task_type(id=task_type_id, db=db):
        logger.warning("Task type not found with ID: %d", task_type_id)
        raise HTTPException(status_code=404, detail="Task type not found")
    tasks_service.delete_task_type(task_type_id=task_type_id, db=db)
    logger.info("Task type with ID: %d deleted successfully by user %s", task_type_id, current_user.username)
    return None


@router.get('/', response_model=list[TaskTypeOut], status_code=200)
def get_all_tasks(db: db_session,
                  feature_id: int | None = None,
                  feature_name: str | None = None,
                  key_name: str | None = None):
    logger.info("Fetching all tasks with filters - feature_id: %s, feature_name: %s, key_name: %s", feature_id,
                feature_name, key_name)
    task_types = tasks_service.get_all_task_types(db=db, feature_name=feature_name, feature_id=feature_id, key_name=key_name)
    return task_types
