def test_create_task(client):
    res = client.post("/tasks", json={"title": "Test", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    assert res.status_code == 201

def test_title_too_short(client):
    res = client.post("/tasks", json={"title": "Te", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    assert res.status_code == 422

def test_unauthorized(client):
    res = client.post("/tasks", json={"title": "Test", "status": "todo", "priority": 1})
    assert res.status_code == 401

def test_user_sees_only_own_tasks(client):
    client.post("/tasks", json={"title": "Task 1", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    client.post("/tasks", json={"title": "Task 2", "status": "todo", "priority": 1}, headers={"X-User-Id": "20"})
    res = client.get("/tasks", headers={"X-User-Id": "10"})
    assert len(res.json()) == 1

def test_filtering(client):
    client.post("/tasks", json={"title": "Task 1", "status": "done", "priority": 5}, headers={"X-User-Id": "10"})
    res = client.get("/tasks?status=done&min_priority=4", headers={"X-User-Id": "10"})
    assert len(res.json()) == 1

def test_change_status(client):
    post_res = client.post("/tasks", json={"title": "Task 1", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    task_id = post_res.json()["id"]
    res = client.patch(f"/tasks/{task_id}/status", json={"status": "done"}, headers={"X-User-Id": "10"})
    assert res.status_code == 200
    assert res.json()["status"] == "done"

def test_404_on_foreign_task(client):
    post_res = client.post("/tasks", json={"title": "Task 1", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    task_id = post_res.json()["id"]
    res = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert res.status_code == 404

def test_delete_task(client):
    post_res = client.post("/tasks", json={"title": "Task 1", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    task_id = post_res.json()["id"]
    res = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert res.status_code == 204

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"