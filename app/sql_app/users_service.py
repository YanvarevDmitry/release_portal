from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from schemas import UserCreate
from sql_app.models.user import User


def get_user(db: Session, username: str | None = None, user_id: int | None = None) -> User:
    stmt = select(User)
    if username:
        stmt = stmt.where(User.username == username)
    if user_id:
        stmt = stmt.where(User.id == user_id)
    return db.execute(stmt).first()


def update_user_email(user_id: int, email: str, db) -> User:
    stmt = update(User).where(User.id == user_id).values(email=email).returning(User)
    user = db.execute(stmt).first()
    db.commit()
    return user


def update_user_role(user_id: int, role: str, db) -> User:
    stmt = update(User).where(User.id == user_id).values(role=role).returning(User)
    user = db.execute(stmt).first()
    db.commit()
    return user


def create_user(user: UserCreate, db: Session) -> User:
    db_user = User(username=user.username, email=user.email, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users(db: Session) -> list[User]:
    return db.execute(select(User)).scalars().all()


def delete_user(db: Session, user_id: int):
    stmt = delete(User).where(User.id == user_id).returning(User)
    user = db.execute(stmt)
    db.commit()
    return user
