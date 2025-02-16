import datetime
import enum

from pydantic import BaseModel

from sql_app.models.releases import ReleaseStageEnum
from sql_app.models.user import RolesEnum


class BasePagination(BaseModel):
    page: int
    page_size: int
    total: int


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


class RegisterUser(BaseModel):
    username: str
    email: str
    password: str


class UserUpdate(BaseModel):
    username: str = None
    email: str = None
    password: str = None


class User(BaseModel):
    id: int
    username: str
    password: str
    role: str | RolesEnum

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: RolesEnum

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
    jira_key: str | None
    status: str
    feature_type_id: int
    release_id: int


class FeatureOut(BaseModel):
    id: int
    name: str
    jira_key: str | None
    status: str
    created_at: datetime.datetime
    feature_type_id: int
    release_id: int

    class Config:
        orm_mode = True


class ReleaseFeature(BaseModel):
    id: int
    name: str
    jira_key: str | None
    feature_type_id: int
    status: str

    class Config:
        orm_mode = True


class ReleaseStageOutWithFeature(ReleaseStageOut):
    features: list[ReleaseFeature] | None

    class Config:
        orm_mode = True


class TaskEnum(enum.Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    REVIEW = 'review'
    DONE = 'done'


class AttachmentOut(BaseModel):
    id: int
    link: str
    task_id: int
    uploaded_at: datetime.datetime
    uploaded_by: int

    class Config:
        orm_mode = True


class PaginationFeatures(BasePagination):
    data: list[FeatureOut]

    class Config:
        orm_mode = True


class PaginationReleaseStages(BasePagination):
    data: list[ReleaseStageOutWithFeature]

    class Config:
        orm_mode = True


class TaskApproverOut(BaseModel):
    task_type_id: int
    role_name: str

    class Config:
        orm_mode = True


class TaskCommentOut(BaseModel):
    id: int
    task_id: int
    comment: str
    user_id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class FeatureStatusENUM(enum.Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    REVIEW = 'review'
    DONE = 'done'
    CANCELLED = 'cancelled'


class ReleaseStatusENUM(enum.Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'
    CANCELLED = 'cancelled'
