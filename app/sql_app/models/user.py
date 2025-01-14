import enum

from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import Session

from app.sql_app.database import Base

# Инициализация контекста для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RolesEnum(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    RELEASE_MANAGER = "release_manager"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(Enum(RolesEnum), default=RolesEnum.USER)
    hashed_password = Column(String)
