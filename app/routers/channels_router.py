from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import get_current_user
from schemas import User, ChannelOut, ChannelCreate
from sql_app import channels_service
from sql_app.channels_service import get_channel
from sql_app.database import get_database

router = APIRouter(prefix="/channels", tags=["channels"])
get_current_user = Annotated[User, Depends(get_current_user)]
db_session = Annotated[Session, Depends(get_database)]


@router.post("/", response_model=ChannelOut, status_code=201)
def create_channel(channel: ChannelCreate,
                   current_user: get_current_user,
                   db: db_session):
    """
    Создание нового канала.

    Args:
        channel (ChannelCreate): Данные канала для создания.
        current_user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если у пользователя нет прав администратора.
        HTTPException: Если канал с таким именем уже существует.

    Returns:
        ChannelOut: Созданный канал.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if get_channel(name=channel.name, db=db):
        raise HTTPException(status_code=400, detail="Channel with this name already exists")
    return channels_service.create_channel(name=channel.name, db=db)


@router.get("/", response_model=list[ChannelOut], status_code=200)
def get_all_channels(db: db_session):
    """
    Получение всех каналов.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        list[ChannelOut]: Список всех каналов.
    """
    channels = channels_service.get_all_channels(db=db)
    return channels
