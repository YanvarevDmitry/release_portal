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

    @property
    def password(self):
        return self.hashed_password

    @password.setter
    def password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)
