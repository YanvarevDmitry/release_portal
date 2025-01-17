from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from schemas import User, UserCreate
from sql_app import users_service
from sql_app.database import get_database
from sql_app.models.user import RolesEnum
from sql_app.users_service import create_user, get_all_users, get_user
from auth import get_current_user

router = APIRouter(prefix='/admin', tags=['admin'])
get_current_user = Annotated[User, Depends(get_current_user)]
db_session = Annotated[Session, Depends(get_database)]


@router.get('/users')
def get_users(current_user: get_current_user, db: db_session):
    if current_user.role != RolesEnum.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')
    return get_all_users(db=db)


@router.post('/users')
def create_new_user(user: UserCreate, current_user: get_current_user, db: db_session):
    if current_user.role != RolesEnum.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    return create_user(user=user, db=db)


@router.put('/users/{user_id}')
def update_user(user_id: int,
                current_user: get_current_user,
                db: db_session,
                role: RolesEnum | None = None,
                password: str | None = None,
                ):
    if current_user.role != RolesEnum.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    return users_service.update_user(db=db, user_id=user_id, role=role.value)


@router.delete('/users/{user_id}')
def delete_user(user_id: int, current_user: get_current_user, db: Session = Depends(get_database)):
    if current_user.role != RolesEnum.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return users_service.delete_user(db=db, user_id=user_id)
