from sqlalchemy import Column, Integer, String, Date, Boolean
from pydantic import BaseModel
from database import Base


# Модели для базы данных
class ReleaseStage(Base):
    __tablename__ = "release_stages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    responsible_person = Column(String)


# Модели для передачи данных через API
class ReleaseStageCreate(BaseModel):
    name: str
    description: str
    start_date: str
    end_date: str
    responsible_person: str

    class Config:
        orm_mode = True


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")  # Роль: user, admin и т.д.


class UserCreate(BaseModel):
    username: str
    password: str
    role: str

    class Config:
        orm_mode = True
