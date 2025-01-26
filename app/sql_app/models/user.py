import enum

from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sql_app.database import Base


class RolesEnum(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    RELEASE_MANAGER = "release_manager"
    REVIEWER = "reviewer"
    TESTER = "tester"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String, ForeignKey('roles.name', ondelete='SET NULL'), default=RolesEnum.USER.value)
    hashed_password = Column(String)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
