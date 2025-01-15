from typing import Annotated
import openpyxl
from openpyxl.styles import Font

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from sql_app import releases_service
from sql_app.channels_service import get_channel
from sql_app.database import get_database

from sql_app.models.user import RolesEnum
from sql_app.platforms_service import get_platform
from sql_app.releases_service import get_all_releases, update_release, get_release, get_all_release_types
from schemas import ReleaseStageCreate, User, ReleaseStageOut, ReleaseTypeOut, ReleaseStageOutWithFeature
from auth import get_current_user

router = APIRouter(prefix="/releases", tags=["releases"])
get_current_user = Annotated[User, Depends(get_current_user)]
db_session = Annotated[Session, Depends(get_database)]


@router.post("/", response_model=ReleaseStageOut)
def create_release(stage: ReleaseStageCreate,
                   current_user: get_current_user,
                   db: db_session,
                   ):
    """
       Создание новой релиза.

       Args:
           stage (ReleaseStageCreate): Данные релиза для создания.
           current_user (User): Текущий аутентифицированный пользователь.
           db (Session): Сессия базы данных.

       Exceptions:
           HTTPException: Если у пользователя нет прав администратора или менеджера релизов.
           HTTPException: Если релиз с таким именем уже существует.
           HTTPException: Если канал не найден.
           HTTPException: Если платформа не найдена.

       Returns:
           ReleaseStageOut: Созданная релиз.
       """
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if get_release(name=stage.name, db=db):
        raise HTTPException(status_code=400, detail="Release stage with this name already exists")
    if not get_channel(channel_id=stage.channel_id, db=db):
        raise HTTPException(status_code=404, detail="Channel not found")
    if not get_platform(platform_id=stage.platform_id, db=db):
        raise HTTPException(status_code=404, detail="Platform not found")
    release = releases_service.create_release(stage=stage, db=db)
    return release


@router.get("/all", response_model=list[ReleaseStageOut])
def get_all_releases(db: db_session):
    """
    Получение всех релизов.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        list[ReleaseStageOut]: Список всех релизов.
    """
    releases = releases_service.get_all_releases(db=db)
    return releases


@router.get('/{release_id}', status_code=200)
def get_release(release_id: int, db: db_session):
    """
    Получение релиза по ID.

    Args:
        release_id (int): ID релиза.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если релиз не найдена.

    Returns:
        ReleaseStageOutWithFeature: релиз с указанным ID и его фичи.
    """
    release = releases_service.get_release_with_features(release_id=release_id, db=db)
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    response = ReleaseStageOutWithFeature.from_orm(release.Release)
    response.features = release.features
    return response


@router.delete("/{release_id}", status_code=204)
def delete_release(release_id: int,
                   current_user: get_current_user,
                   db: db_session):
    """
    Удаление релиза по ID.

    Args:
        release_id (int): ID релиза для удаления.
        current_user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если у пользователя нет прав администратора или менеджера релизов.
        HTTPException: Если релиз не найден.

    Returns:
        None
    """
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    release = releases_service.get_release(release_id=release_id, db=db)
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    return releases_service.delete_release(stage_id=release_id, db=db)


@router.get("/report", response_class=FileResponse)
def generate_report(db: db_session):
    """
    Генерация отчета по всем релизам.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        FileResponse: Сгенерированный отчет в виде файла Excel.
    """
    stages = get_all_releases(db=db)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Отчет по релизам"

    # Заголовки
    headers = ["Имя", "Описание", "Дата начала", "Дата окончания", "Статус"]
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = Font(bold=True)

    # Данные
    for row_num, stage in enumerate(stages, 2):
        ws.cell(row=row_num, column=1, value=stage.name)
        ws.cell(row=row_num, column=2, value=stage.description)
        ws.cell(row=row_num, column=3, value=stage.start_date)
        ws.cell(row=row_num, column=4, value=stage.end_date)
        ws.cell(row=row_num, column=5, value=stage.status.value)

    file_path = "release_report.xlsx"
    wb.save(file_path)
    return FileResponse(file_path,
                        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        filename=file_path)


@router.put("/{stage_id}")
def update_release(stage_id: int,
                   name: str | None,
                   description: str | None,
                   start_date: str | None,
                   end_date: str | None,
                   current_user: get_current_user,
                   db: db_session):
    """
    Обновление релиза по ID.

    Args:
        stage_id (int): ID релиза для обновления.
        name (str, optional): Новое имя релиза.
        description (str, optional): Новое описание релиза.
        start_date (str, optional): Новая дата начала релиза.
        end_date (str, optional): Новая дата окончания релиза.
        current_user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если у пользователя нет прав администратора или менеджера релизов.

    Returns:
        ReleaseStageOut: Обновленная релиз.
    """
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return update_release(stage_id=stage_id,
                          name=name,
                          description=description,
                          start_date=start_date,
                          end_date=end_date,
                          db=db)


@router.get('/types/', response_model=list[ReleaseTypeOut], status_code=200)
def get_release_types(db: db_session):
    """
    Получение всех типов релиза.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        list[ReleaseTypeOut]: Список всех типов релиза.
    """
    return get_all_release_types(db=db)


@router.post("/types/", response_model=ReleaseTypeOut, status_code=201)
def create_release_type(name: str,
                        platform_id: int,
                        channel_id: int,
                        current_user: get_current_user,
                        db: db_session):
    """
    Создание нового типа релиза.

    Args:
        name (str): Имя типа релиза.
        platform_id (int): ID платформы.
        channel_id (int): ID канала.
        current_user (User): Текущий аутентифицированный пользователь.
        db (Session): Сессия базы данных.

    Exceptions:
        HTTPException: Если у пользователя нет прав администратора или менеджера релизов.
        HTTPException: Если платформа не найдена.
        HTTPException: Если канал не найден.

    Returns:
        ReleaseTypeOut: Созданный тип релиза.
    """
    if current_user.role not in [RolesEnum.ADMIN, RolesEnum.RELEASE_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not get_platform(platform_id=platform_id, db=db):
        raise HTTPException(status_code=404, detail="Platform not found")
    if not get_channel(channel_id=channel_id, db=db):
        raise HTTPException(status_code=404, detail="Channel not found")
    return releases_service.create_release_type(name=name, platform_id=platform_id, channel_id=channel_id, db=db)
