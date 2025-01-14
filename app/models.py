from sqlalchemy import Column, Integer, String, Date, Boolean
from pydantic import BaseModel
from sql_app.database import Base


# Модели для передачи данных через API
class ReleaseStageCreate(BaseModel):
    name: str
    description: str
    start_date: str
    end_date: str
    status: str

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    username: str = None
    email: str = None
    password: str = None

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    username: str
    password: str
    role: str

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str
