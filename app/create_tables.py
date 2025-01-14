# create_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from auth import pwd_context
from settings import DbSettings
from sql_app.database import Base
from sql_app.models.channels import Channel
from sql_app.models.features import FeatureType, FeatureTypeTaskType
from sql_app.models.platforms import Platform
from sql_app.models.releases import Release, ReleaseStageEnum, ReleaseType
from sql_app.models.tasks import TaskType
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
        release1 = Release(
            name="Release ios",
            status=ReleaseStageEnum.created,
            description="First ios release",
            start_date="2023-01-01T00:00:00",
            end_date="2023-01-31T23:59:59",
            platform_id=2,
            channel_id=1,
            release_type_id=2,
        )
        release2 = Release(
            name="Release Android",
            status=ReleaseStageEnum.in_progress,
            description="First adnroid release",
            start_date="2023-02-01T00:00:00",
            end_date="2023-02-28T23:59:59",
            platform_id=1,
            channel_id=1,
            release_type_id=1
        )

        # Добавление данных в сессию
        session.add_all([release1, release2])
        session.commit()
    finally:
        session.close()


def populate_task_types():
    session = Session(bind=engine)
    try:
        task_type1 = TaskType(key_name="uxui",
                              name="Ux Review",
                              description="Проверка ux review экспертами",
                              is_required=True)
        task_type2 = TaskType(key_name="test",
                              name="Testing task",
                              description="Проверка на прохождение всех тестов",
                              is_required=True)
        task_type3 = TaskType(key_name="analitic",
                              name="Analitic task",
                              description="Проверка аналитики экспертами",
                              is_required=True)
        task_type4 = TaskType(key_name="feature_toggle",
                              name="Feature toggle task",
                              description="Проверка фичи на включение/выключение фиче тоглов",
                              is_required=True)
        session.add_all([task_type1, task_type2, task_type3, task_type4])
        session.commit()
    finally:
        session.close()


def populate_feature_types():
    session = Session(bind=engine)
    try:
        feature_type1 = FeatureType(name="Фича без ревью", description="тип фичи, где не требуется ревью ux ui")
        feature_type2 = FeatureType(name="Фича без тогглов", description="тип фичи, где не требуется наличие тогглов")
        session.add_all([feature_type1, feature_type2])
        session.commit()
    finally:
        session.close()


def populate_feature_type_task_types():
    session = Session(bind=engine)
    try:
        feature_type_task_type1 = FeatureTypeTaskType(feature_type_id=1, task_type_id=2)
        feature_type_task_type2 = FeatureTypeTaskType(feature_type_id=1, task_type_id=3)
        feature_type_task_type3 = FeatureTypeTaskType(feature_type_id=1, task_type_id=4)
        feature_type_task_type4 = FeatureTypeTaskType(feature_type_id=2, task_type_id=1)
        feature_type_task_type5 = FeatureTypeTaskType(feature_type_id=2, task_type_id=2)
        feature_type_task_type6 = FeatureTypeTaskType(feature_type_id=2, task_type_id=3)
        session.add_all([feature_type_task_type1,
                         feature_type_task_type2,
                         feature_type_task_type3,
                         feature_type_task_type4,
                         feature_type_task_type5,
                         feature_type_task_type6])
        session.commit()
    finally:
        session.close()


# Вызов функции для создания релизов
populate_users()
populate_platforms()
populate_channels()
populate_release_types()
populate_releases()
populate_task_types()
populate_feature_types()
populate_feature_type_task_types()
