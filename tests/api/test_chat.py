"""
https://fastapi.tiangolo.com/advanced/testing-websockets/
"""
from fastapi import WebSocketDisconnect


def test_websocket(client, create_user_in_db, create_token_in_db):
    db_user = create_user_in_db()
    db_token = create_token_in_db(user_id=db_user.id)

    with client.websocket_connect(f"/chat/ws/{db_user.id}?token={db_token.token}") as websocket:
        websocket.send_text("Test")
        data = websocket.receive_text()
        assert data == {"message": "You wrote: Test"}


def test_websocket_broadcast(client, create_user_in_db, create_token_in_db):
    db_user1 = create_user_in_db()
    db_token1 = create_token_in_db(user_id=db_user1.id)
    db_user2 = create_user_in_db()
    db_token2 = create_token_in_db(user_id=db_user2.id)

    with client.websocket_connect(f"/chat/ws/{db_user1.id}?token={db_token1.token}") as websocket1:
        with client.websocket_connect(f"/chat/ws/{db_user2.id}?token={db_token2.token}") as websocket2:
            websocket1.send_json({"message": "Test"})
            data1 = websocket1.receive_json()
            assert data1 == {"message": "You wrote: Test"}
            data2 = websocket2.receive_json()
            assert data2 == {"message": "Client #1 says: Test"}


def test_websocket_user_not_match_token(client, create_user_in_db, create_token_in_db):
    """ Auth test """
    db_user = create_user_in_db()
    db_token = create_token_in_db(user_id=db_user.id)
    db_wrong_user = create_user_in_db()

    websocket = client.websocket_connect(f"/chat/ws/{db_wrong_user.id}?token={db_token.token}")
    try:
        websocket.__enter__()
    except WebSocketDisconnect as exc:
        assert exc.code == 1008
