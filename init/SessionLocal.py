# create_db.py

from sqlalchemy.orm import Session
from app.sql_app.models import User, ReleaseStage
from database import SessionLocal, init_db


def create_initial_data(db: Session):
    # Добавление пользователей
    user1 = User(username="admin", password="hashed_password", role="admin")
    user2 = User(username="developer", password="hashed_password", role="user")

    db.add(user1)
    db.add(user2)
    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    # Добавление этапов релиза
    release_stage1 = ReleaseStage(
        name="Stage 1: Planning",
        description="Initial stage of planning.",
        start_date="2025-01-01",
        end_date="2025-01-10",
        responsible_person_id=user1.id
    )
    release_stage2 = ReleaseStage(
        name="Stage 2: Development",
        description="Development phase of the release.",
        start_date="2025-01-11",
        end_date="2025-02-01",
        responsible_person_id=user2.id
    )

    db.add(release_stage1)
    db.add(release_stage2)
    db.commit()


# Инициализация БД и добавление данных
def init():
    init_db()  # Создание таблиц
    db = SessionLocal()  # Открытие сессии
    create_initial_data(db)  # Добавление тестовых данных
    db.close()


if __name__ == "__main__":
    init()  # Запуск процесса
