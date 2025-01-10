from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.models import User, UserCreate
from app.sql_app.database import get_database
from app.sql_app.models.user import RolesEnum
from app.sql_app.users_service import create_user

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users/")
def get_users(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_database)):
    if current_user.role != RolesEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db.query(User).all()

@router.post("/users/")
def create_new_user(user: UserCreate, db: Session = Depends(get_database)):
    create_user(user=user, db=db)
    return {"message": "User created successfully"}

@router.put("/users/{user_id}")
def update_user(user_id: int, role: RolesEnum, current_user: User = Depends(get_current_active_user),
                db: Session = Depends(get_database)):
    if current_user.role != RolesEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_current_active_user),
                db: Session = Depends(get_database)):
    if current_user.role != RolesEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} deleted successfully"}