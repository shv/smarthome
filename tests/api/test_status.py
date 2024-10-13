def test_status(client):
    result = client.get("/status")
    assert result.status_code == 200
    assert result.json() == {"status": "ok"}
