from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import get_db
from models import ReleaseStage, ReleaseStageCreate, UserCreate
from auth import get_current_user, create_user, verify_role

app = FastAPI()


@app.post("/users/")
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    create_user(user, db)
    return {"message": "User created successfully"}


@app.get("/admin/approve_release/{release_id}")
def approve_release(release_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_role(token, "admin", db)  # Проверяем роль пользователя
    # Логика утверждения релиза
    return {"message": f"Release {release_id} approved"}


# Маршрут для создания нового этапа релиза
@app.post("/release_stages/", response_model=ReleaseStageCreate)
def create_release_stage(stage: ReleaseStageCreate, db: Session = Depends(get_db),
                         current_user: str = Depends(get_current_user)):
    db_stage = ReleaseStage(**stage.dict())
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage


# Маршрут для получения всех этапов релиза
@app.get("/release_stages/", response_model=List[ReleaseStageCreate])
def get_all_release_stages(db: Session = Depends(get_db)):
    return db.query(ReleaseStage).all()


# Маршрут для получения токена
@app.post("/token/")
def login_for_access_token():
    # Пример возвращаемого токена (в реальности проверка на пароли и т.д.)
    return {"access_token": "dummy_token", "token_type": "bearer"}
