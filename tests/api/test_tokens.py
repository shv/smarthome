"""
https://fastapi.tiangolo.com/advanced/testing-database/
"""
from smarthome import models


def test_get_token(client, db, create_user_in_db):
    db_user = create_user_in_db()

    result = client.post("/token")
    assert result.status_code == 200

    db_token = db.query(models.Token).join(models.User).filter(models.User.id == db_user.id).first()

    assert result.json() == {"token": db_token.token, "user_id": db_user.id}

