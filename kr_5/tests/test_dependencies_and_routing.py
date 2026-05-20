def test_users_me(client):
    res = client.get("/users/me", headers={"X-User-Id": "10", "X-User-Role": "admin"})
    assert res.json() == {"id": 10, "role": "admin"}

def test_missing_header_401(client):
    assert client.get("/users/me").status_code == 401

def test_user_forbidden_admin_stats(client):
    assert client.get("/admin/stats", headers={"X-User-Id": "10", "X-User-Role": "user"}).status_code == 403

def test_admin_gets_stats(client):
    client.post("/tasks", json={"title": "Task 1", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    res = client.get("/admin/stats", headers={"X-User-Id": "99", "X-User-Role": "admin"})
    assert res.status_code == 200
    assert res.json()["total_tasks"] == 1

def test_user_cannot_delete_foreign_task(client):
    res_post = client.post("/tasks", json={"title": "Task 1", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    task_id = res_post.json()["id"]
    assert client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "20"}).status_code == 404

def test_admin_can_delete_foreign_task(client):
    res_post = client.post("/tasks", json={"title": "Task 1", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    task_id = res_post.json()["id"]
    assert client.delete(f"/admin/tasks/{task_id}", headers={"X-User-Id": "99", "X-User-Role": "admin"}).status_code == 204

def test_swagger_tags(client):
    res = client.get("/openapi.json")
    assert res.status_code == 200