from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.main import app
from app.sql_app.database import get_database
from app.sql_app.users_service import update_user_email

router = APIRouter(prefix="/profile", tags=["profile"])


@app.get("/")
def get_user_profile(current_user=Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.name,
    }


@app.put("/")
def update_user_profile(
        email: str,
        current_user=Depends(get_current_user), db: Session = Depends(get_database)
):
    update_user_email(user_id=current_user.id, email=email, db=db)
    return {"message": "Профиль обновлен"}
