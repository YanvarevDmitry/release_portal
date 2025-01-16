import datetime
from typing import List

from pydantic import BaseModel

from sql_app.models.releases import ReleaseStageEnum
from sql_app.models.user import RolesEnum


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
    role: RolesEnum


class UserUpdate(BaseModel):
    username: str = None
    email: str = None
    password: str = None


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


class TaskTypeCreate(BaseModel):
    key_name: str
    name: str
    description: str
    is_required: bool | None


class TaskTypeOut(BaseModel):
    id: int
    key_name: str
    name: str
    description: str
    is_required: bool

    class Config:
        orm_mode = True


class FeatureTypeCreate(BaseModel):
    name: str
    description: str


class TaskOut(BaseModel):
    id: int
    feature_id: int
    task_type_id: int
    status: str

    class Config:
        orm_mode = True


class FeatureTypeOut(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


class FeatureCreate(BaseModel):
    name: str
    status: str
    feature_type_id: int
    release_id: int


class FeatureOut(BaseModel):
    id: int
    name: str
    status: str
    created_at: datetime.datetime
    feature_type_id: int
    release_id: int

    class Config:
        orm_mode = True


class ReleaseFeature(BaseModel):
    id: int
    name: str
    feature_type_id: int
    status: str

    class Config:
        orm_mode = True


class ReleaseStageOutWithFeature(ReleaseStageOut):
    features: list[ReleaseFeature] | None

    class Config:
        orm_mode = True
