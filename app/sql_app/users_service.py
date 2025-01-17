from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from auth import get_password_hash
from schemas import UserCreate
from sql_app.models.user import User


def get_user(db: Session, username: str | None = None, user_id: int | None = None) -> User:
    stmt = select(User)
    if username:
        stmt = stmt.where(User.username == username)
    if user_id:
        stmt = stmt.where(User.id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def update_user_email(user_id: int, email: str, db) -> User:
    stmt = update(User).where(User.id == user_id).values(email=email).returning(User)
    user = db.execute(stmt).first()
    db.commit()
    return user


def update_user(user_id: int, db: Session, role: str | None = None, password: str | None = None) -> User:
    values = {}
    if role:
        values['role'] = role
    if password:
        values['hashed_password'] = get_password_hash(password)
    stmt = update(User).where(User.id == user_id).values(**values).returning(User)
    user = db.execute(stmt).first()
    db.commit()
    return user


def create_user(user: UserCreate, db: Session) -> User:
    db_user = User(username=user.username, email=user.email, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users(db: Session) -> list[User]:
    return db.execute(select(User)).scalars().all()


def delete_user(db: Session, user_id: int):
    stmt = delete(User).where(User.id == user_id).returning(User)
    user = db.execute(stmt).scalar_one()
    db.commit()
    return user
