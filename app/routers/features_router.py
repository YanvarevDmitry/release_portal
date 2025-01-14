from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user
from schemas import User
from sql_app.database import get_database

router = APIRouter(prefix="/feature", tags=["features"])
get_current_user = Annotated[User, Depends(get_current_user)]
db_session = Annotated[Session, Depends(get_database)]


