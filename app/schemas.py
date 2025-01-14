import datetime

from pydantic import BaseModel

from sql_app.models.releases import ReleaseStageEnum


# Модели для передачи данных через API
class ReleaseStageCreate(BaseModel):
    name: str
    description: str
    start_date: str
    end_date: str
    status: str
    platform_id: int
    channel_id: int
    release_type_id: int

    class Config:
        orm_mode = True


class ReleaseStageOut(BaseModel):
    id: int
    name: str
    description: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    status: ReleaseStageEnum
    platform_id: int
    channel_id: int
    release_type_id: int

    class Config:
        orm_mode = True


class ReleaseTypeOut(BaseModel):
    id: int
    name: str
    platform_id: int
    channel_id: int

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


class PlatformCreate(BaseModel):
    name: str


class PlatformOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class ChannelCreate(BaseModel):
    name: str


class ChannelOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class ReleaseTypeCreate(BaseModel):
    name: str
    platform_id: int
    channel_id: int


