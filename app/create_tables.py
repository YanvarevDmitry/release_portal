# create_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from auth import pwd_context
from settings import DbSettings
from sql_app.database import Base
from sql_app.models.channels import Channel
from sql_app.models.platforms import Platform
from sql_app.models.releases import ReleaseStage, ReleaseStageEnum, ReleaseType
from sql_app.models.user import User, RolesEnum

engine = create_engine(DbSettings.DB_URL)

# Создание всех таблиц
Base.metadata.create_all(bind=engine)


def populate_users():
    session = Session(bind=engine)
    try:
        # Пример данных для таблицы User
        user1 = User(username="admin", hashed_password=pwd_context.hash('admin'), email="admin@example.com",
                     role=RolesEnum.ADMIN)
        user2 = User(username="manager", hashed_password=pwd_context.hash('manager'),
                     email="release_manager@example.com", role=RolesEnum.RELEASE_MANAGER)
        user3 = User(username="user", hashed_password=pwd_context.hash('user'), email="user@example.com",
                     role=RolesEnum.USER)

        # Добавление данных в сессию
        session.add_all([user1, user2, user3])
        session.commit()
    finally:
        session.close()


def populate_platforms():
    session = Session(bind=engine)
    try:
        # Пример данных для таблицы Platform
        platform1 = Platform(name="Android")
        platform2 = Platform(name="iOS")
        platform3 = Platform(name="Web")

        # Добавление данных в сессию
        session.add_all([platform1, platform2, platform3])
        session.commit()
    finally:
        session.close()


def populate_channels():
    session = Session(bind=engine)
    try:
        # Пример данных для таблицы Channel
        channel1 = Channel(name="sbol")
        channel2 = Channel(name="investor")

        # Добавление данных в сессию
        session.add_all([channel1, channel2])
        session.commit()
    finally:
        session.close()


def populate_release_types():
    session = Session(bind=engine)
    try:
        # Пример данных для таблицы ReleaseType
        release_type1 = ReleaseType(name="Android", platform_id=1, channel_id=1)
        release_type2 = ReleaseType(name="iOS", platform_id=2, channel_id=1)

        # Добавление данных в сессию
        session.add_all([release_type1, release_type2])
        session.commit()
    finally:
        session.close()


def populate_releases():
    session = Session(bind=engine)
    try:
        # Пример данных для таблицы ReleaseStage
        release1 = ReleaseStage(
            name="Release ios",
            status=ReleaseStageEnum.created,
            description="First ios release",
            start_date="2023-01-01T00:00:00",
            end_date="2023-01-31T23:59:59",
            platform_id=2,
            channel_id=1,
            release_type=2,
        )
        release2 = ReleaseStage(
            name="Release Android",
            status=ReleaseStageEnum.in_progress,
            description="First adnroid release",
            start_date="2023-02-01T00:00:00",
            end_date="2023-02-28T23:59:59",
            platform_id=1,
            channel_id=1,
            release_type=1
        )

        # Добавление данных в сессию
        session.add_all([release1, release2])
        session.commit()
    finally:
        session.close()


# Вызов функции для создания релизов
populate_users()
populate_platforms()
populate_channels()
populate_release_types()
populate_releases()
