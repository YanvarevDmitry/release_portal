from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from schemas import User, PlatformOut, PlatformCreate
from sql_app import platforms_service
from sql_app.database import get_database
from sql_app.platforms_service import get_platform

router = APIRouter(prefix="/platforms", tags=["platforms"])
get_current_user = Annotated[User, Depends(get_current_user)]
db_session = Annotated[Session, Depends(get_database)]


@router.post("/", response_model=PlatformOut, status_code=201)
def create_platform(platform: PlatformCreate,
                    current_user: get_current_user,
                    db: db_session):
    """
    Создание новой платформы.

    Args:
        platform (PlatformCreate): Данные платформы для создания.
        current_user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если у пользователя нет прав администратора.
        HTTPException: Если платформа с таким именем уже существует.

    Returns:
        PlatformOut: Созданная платформа.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if get_platform(name=platform.name, db=db):
        raise HTTPException(status_code=400, detail="Platform with this name already exists")
    return platforms_service.create_platform(name=platform.name, db=db)


@router.get("/", response_model=list[PlatformOut], status_code=200)
def get_all_platforms(db: db_session):
    """
    Получение всех платформ.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        list[PlatformOut]: Список всех платформ.
    """
    platforms = platforms_service.get_all_platforms(db=db)
    return platforms
