from smarthome import cruds


async def test_get_user_by_token(client, db, create_user_in_db, create_token_in_db):
    db_user = create_user_in_db()
    db_token = create_token_in_db(user_id=db_user.id)
    user = await cruds.get_user_by_token(db=db, token=db_token.token)
    assert user.id == db_user.id
