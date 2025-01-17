from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from schemas import User, UserCreate, RegisterUser, UserOut
from sql_app import users_service
from sql_app.database import get_database
from sql_app.models.user import RolesEnum

router = APIRouter(prefix="/users", tags=["users"])
get_current_user = Annotated[User, Depends(get_current_user)]
db_session = Annotated[Session, Depends(get_database)]


@router.get("/me", response_model=UserOut, status_code=200)
def get_me(current_user: get_current_user):
	"""
	Получение информации о текущем пользователе.

	Args:
		current_user (User): Текущий аутентифицированный пользователь.

	Returns:
		User: Информация о текущем пользователе.
	"""
	if not current_user:
		raise HTTPException(status_code=404, detail="User not found")
	return current_user


@router.post("/register", response_model=UserOut, status_code=201)
def register(user: RegisterUser, db: db_session):
	"""
	Регистрация нового пользователя.
	Args:
		user (User): Информация о новом пользователе.
		db (Session): Сессия для работы с базой данных.
	Returns:
		User: Информация о новом пользователе.
	"""
	db_user = users_service.get_user(username=user.username, db=db)
	if db_user:
		raise HTTPException(status_code=400, detail="Username already registered")
	new_user = UserCreate(username=user.username, password=user.password, email=user.email, role=RolesEnum.USER)
	return users_service.create_user(user=new_user, db=db)
