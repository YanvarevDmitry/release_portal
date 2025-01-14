import enum

from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, Enum
from sql_app.database import Base

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
