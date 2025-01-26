from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from schemas import User, TaskTypeOut, TaskTypeCreate, TaskOut, TaskEnum, AttachmentOut
from sql_app import tasks_service, users_service
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
    if current_user.role not in [RolesEnum.ADMIN.value, RolesEnum.RELEASE_MANAGER.value]:
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
    if current_user.role not in [RolesEnum.ADMIN.value, RolesEnum.RELEASE_MANAGER.value]:
        logger.warning("User %s does not have enough permissions", current_user.username)
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not tasks_service.get_task_type(id=task_type_id, db=db):
        logger.warning("Task type not found with ID: %d", task_type_id)
        raise HTTPException(status_code=404, detail="Task type not found")
    tasks_service.delete_task_type(task_type_id=task_type_id, db=db)
    logger.info("Task type with ID: %d deleted successfully by user %s", task_type_id, current_user.username)
    return None


@router.get('/types/{task_type_id}/approver', status_code=200)
def get_task_type_approver(task_type_id: int, db: db_session):
    task_type = tasks_service.get_task_type(id=task_type_id, db=db)
    if not task_type:
        logger.warning("Task type not found with ID: %d", task_type_id)
        raise HTTPException(status_code=404, detail="Task type not found")
    kek = tasks_service.get_task_type_approver(task_type_id=task_type_id, db=db)
    return kek


@router.post('/types/{task_type_id}/approver', status_code=201)
def create_task_type_approver(task_type_id: int, role_name: str, db: db_session):
    task_type = tasks_service.get_task_type(id=task_type_id, db=db)
    if not task_type:
        logger.warning("Task type not found with ID: %d", task_type_id)
        raise HTTPException(status_code=404, detail="Task type not found")
    role = users_service.get_role(name=role_name, db=db)
    if not role:
        logger.warning("Role not found with name: %d", role_name)
        raise HTTPException(status_code=404, detail="Role not found")
    if not tasks_service.get_task_type_approver(task_type_id=task_type_id, db=db):
        logger.warning("Task type approver already exists for task type with ID: %d", task_type_id)
        raise HTTPException(status_code=400, detail="Task type approver already exists")
    tasks_service.create_task_type_approver(task_type_id=task_type_id, role_id=role.id, db=db)
    return None


@router.patch('/{task_id}', response_model=TaskOut, status_code=200)
def update_task(task_id: int,
                status: TaskEnum,
                current_user: get_current_user,
                db: db_session):
    if current_user.role not in [RolesEnum.ADMIN.value, RolesEnum.RELEASE_MANAGER.value]:
        logger.warning("User %s does not have enough permissions", current_user.username)
        raise HTTPException(status_code=403, detail="Only admin or release manager can update task")
    task = tasks_service.get_task(task_id=task_id, db=db)
    if not task:
        logger.warning("Task not found with ID: %d", task_id)
        raise HTTPException(status_code=404, detail="Task not found")
    task_approver = tasks_service.get_task_type_approver(task_type_id=task.task_type_id, db=db)
    if task_approver and task_approver['name'] != current_user.role:
        logger.warning("User %s does not have enough permissions. Only user with role %s can update task",
                       current_user.username,
                       task_approver['name'])
        raise HTTPException(status_code=403, detail=f"User {current_user.username} does not have enough permissions."
                                                    f"Only user with role {task_approver['name']} can update task")
    logger.info("User %s  update task with ID: %d", current_user.username, task_id)
    return tasks_service.update_task(task_id=task_id, status=status.value, db=db)


@router.post('/{task_id}/attachments', response_model=AttachmentOut, status_code=201)
def upload_attachment(task_id: int, link: str, current_user: get_current_user, db: db_session):
    task = tasks_service.get_task(task_id=task_id, db=db)
    if not task:
        logger.warning("Task not found with ID: %d", task_id)
        raise HTTPException(status_code=404, detail="Task not found")
    logger.info('User %s uploaded attachment link %s for task with ID: %d', current_user.username, link, task_id)
    if task.status == TaskEnum.DONE.value:
        logger.warning("Task with ID: %d is already done", task_id)
        raise HTTPException(status_code=400, detail="Task is already done")
    if task.status == TaskEnum.OPEN.value:
        tasks_service.update_task(task_id=task_id, status=TaskEnum.IN_PROGRESS.value, db=db)
    if not link.startswith("http://") and not link.startswith("https://"):
        logger.warning("Invalid link: %s", link)
        raise HTTPException(status_code=400, detail="Invalid link")
    return tasks_service.create_attachment(task_id=task_id, link=link, user_id=current_user.id, db=db)
