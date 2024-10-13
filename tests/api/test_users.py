"""
https://fastapi.tiangolo.com/advanced/testing-database/
"""
from smarthome import models


def test_get_users(client, create_user_in_db):
    db_users = [create_user_in_db() for _ in range(5)]

    result = client.get("/users")
    assert result.status_code == 200
    assert len(result.json()) == len(db_users)


def test_get_users_empty(client):
    result = client.get("/users")
    assert result.status_code == 200
    assert result.json() == []


def test_get_user(client, db, create_user_in_db):
    db_user = create_user_in_db()

    result = client.get("/users/1/")
    assert result.status_code == 200

    assert result.json() == {
        'email': db_user.email,
        'id': db_user.id,
        'is_active': db_user.is_active,
    }


def test_create_user(client, get_user_by_email_from_db):
    user = {"password": "testpassword", "email": "test@email.com"}
    result = client.post("/users", json=user)
    assert result.status_code == 200
    db_user = get_user_by_email_from_db(user_email=user["email"])
    assert result.json() == {
        'email': db_user.email,
        'id': db_user.id,
        'is_active': db_user.is_active,
    }
