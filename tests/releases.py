import pytest
from fastapi.testclient import TestClient

from app.auth import get_current_user
from app.main import app
from app.sql_app.database import get_database
from app.sql_app.models.user import RolesEnum
from schemas import ReleaseStageCreate, User

client = TestClient(app)


def mock_get_current_user_admin():
    return User(id=1, username="admin", role=RolesEnum.ADMIN)


def mock_get_current_user_release_manager():
    return User(id=2, username="release_manager", role=RolesEnum.RELEASE_MANAGER)


def mock_get_current_user_user():
    return User(id=3, username="user", role=RolesEnum.USER)


app.dependency_overrides[get_current_user] = mock_get_current_user_admin


def create_release_stage_payload():
    return {
        "name": "Release 1",
        "description": "First release",
        "start_date": "2023-10-01",
        "end_date": "2023-10-31",
        "status": "PLANNED",
        "channel_id": 1,
        "platform_id": 1
    }


def returns_403_if_user_not_authorized():
    app.dependency_overrides[get_current_user] = mock_get_current_user_user
    response = client.post("/release_stages/", json=create_release_stage_payload())
    assert response.status_code == 403
    app.dependency_overrides[get_current_user] = mock_get_current_user_admin


def returns_400_if_release_stage_exists():
    response = client.post("/release_stages/", json=create_release_stage_payload())
    assert response.status_code == 400


def returns_404_if_channel_not_found():
    payload = create_release_stage_payload()
    payload["channel_id"] = 999
    response = client.post("/release_stages/", json=payload)
    assert response.status_code == 404


def returns_404_if_platform_not_found():
    payload = create_release_stage_payload()
    payload["platform_id"] = 999
    response = client.post("/release_stages/", json=payload)
    assert response.status_code == 404
