# create_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth import get_password_hash
from settings import DbSettings
from sql_app.database import Base, SessionLocal
from sql_app.models.releases import ReleaseStage, ReleaseStageEnum
from sql_app.models.user import User, RolesEnum

engine = create_engine(DbSettings.DB_URL)

# Создание всех таблиц
Base.metadata.create_all(bind=engine)


def populate_releases():
    session = SessionLocal()
    session = Session(bind=engine)
    try:
        # Пример данных для таблицы ReleaseStage
        release1 = ReleaseStage(
            name="Release 1",
            status=ReleaseStageEnum.created,
            description="First release",
            start_date="2023-01-01T00:00:00",
            end_date="2023-01-31T23:59:59"
        )
        release2 = ReleaseStage(
            name="Release 2",
            status=ReleaseStageEnum.in_progress,
            description="Second release",
            start_date="2023-02-01T00:00:00",
            end_date="2023-02-28T23:59:59"
        )

        # Добавление данных в сессию
        session.add_all([release1, release2])
        session.commit()
    finally:
        session.close()


def populate_users():
    session = SessionLocal()
    session = Session(bind=engine)
    try:
        # Пример данных для таблицы User
        user1 = User(username="admin", hashed_password=get_password_hash('admin'), email="admin@example.com",
                     role=RolesEnum.ADMIN)
        user2 = User(username="manager", hashed_password=get_password_hash('manager'),
                     email="release_manager@example.com", role=RolesEnum.RELEASE_MANAGER)
        user3 = User(username="user", hashed_password=get_password_hash('user'), email="user@example.com",
                     role=RolesEnum.USER)

        # Добавление данных в сессию
        session.add_all([user1, user2, user3])
        session.commit()
    finally:
        session.close()


# Вызов функции для создания релизов
populate_releases()
