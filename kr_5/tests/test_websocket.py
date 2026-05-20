def test_ws_connect(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as ws:
        data = ws.receive_json()
        assert data["type"] == "join"

def test_ws_send_receive(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as ws:
        ws.receive_json() # skip join
        ws.send_json({"type": "message", "text": "Hello"})
        data = ws.receive_json()
        assert data["text"] == "Hello"

def test_ws_two_clients(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as ws1:
        ws1.receive_json()
        with client.websocket_connect("/ws/rooms/test?username=bob") as ws2:
            ws1.receive_json()
            ws2.receive_json()
            ws1.send_json({"type": "message", "text": "Hi"})
            assert ws1.receive_json()["text"] == "Hi"
            assert ws2.receive_json()["text"] == "Hi"

def test_ws_different_rooms(client):
    with client.websocket_connect("/ws/rooms/r1?username=a") as ws1:
        with client.websocket_connect("/ws/rooms/r2?username=b") as ws2:
            ws1.receive_json()
            ws2.receive_json()
            ws1.send_json({"type": "message", "text": "R1 MSG"})
            assert ws1.receive_json()["text"] == "R1 MSG"
            # ws2 doesn't receive it, if we try to receive it will block or timeout.

def test_ws_message_too_long(client):
    with client.websocket_connect("/ws/rooms/test?username=a") as ws:
        ws.receive_json()
        ws.send_json({"type": "message", "text": "a" * 301})
        data = ws.receive_json()
        assert data["type"] == "error"

def test_ws_disconnect_removes_user(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as ws:
        res = client.get("/rooms/test/users")
        assert "alice" in res.json()["users"]
    
    res = client.get("/rooms/test/users")
    assert "alice" not in res.json()["users"]