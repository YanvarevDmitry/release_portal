from sqlalchemy.orm import Session

from schemas import UserCreate
from sql_app.models.user import User


def get_user(db: Session, username: str | None = None, user_id: int | None = None, ) -> User:
    stmt = db.query(User)
    if username:
        stmt = stmt.filter(User.username == username)
    if user_id:
        stmt = stmt.filter(User.id == user_id)
    return db.execute(stmt.first())


def update_user_email(user_id: int, email: str, db) -> User:
    stmt = db.query(User).filter(User.id == user_id)
    stmt = stmt.update({User.email: email})
    user = db.execute(stmt)
    db.commit()
    return user


def create_user(user: UserCreate, db: Session) -> User:
    db_user = User(username=user.username, email=user.email, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
