import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import get_current_user, get_database

from app.schemas import ChannelCreate, User
from sql_app.models.user import RolesEnum

client = TestClient(app)


def mock_get_current_user_admin():
    return User(id=1, username="admin", role=RolesEnum.ADMIN)


def mock_get_current_user_user():
    return User(id=2, username="user", role=RolesEnum.USER)


app.dependency_overrides[get_current_user] = mock_get_current_user_admin


def create_channel_payload():
    return {
        "name": "Channel 1",
        "description": "First channel"
    }

    app.dependency_overrides[get_current_user] = mock_get_current_user_user
    response = client.post("/channels/", json=create_channel_payload())
    assert response.status_code == 403
    app.dependency_overrides[get_current_user] = mock_get_current_user_admin


def returns_400_if_channel_exists():
    response = client.post("/channels/", json=create_channel_payload())
    assert response.status_code == 400


def gets_all_channels():
    response = client.get("/channels/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
