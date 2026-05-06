import pytest

@pytest.mark.asyncio
async def test_create_user(async_client, fake_user_data):
    # Создание пользователя (201) и валидация
    response = await async_client.post("/users", json=fake_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == fake_user_data["username"]
    assert data["age"] == fake_user_data["age"]
    assert "id" in data

@pytest.mark.asyncio
async def test_get_existing_user(async_client, fake_user_data):
    # Получение существующего пользователя (200)
    create_resp = await async_client.post("/users", json=fake_user_data)
    user_id = create_resp.json()["id"]

    response = await async_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == fake_user_data["username"]

@pytest.mark.asyncio
async def test_get_nonexistent_user(async_client):
    # Попытка получить несуществующего пользователя (404)
    response = await async_client.get("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_delete_existing_user(async_client, fake_user_data):
    # Удаление существующего пользователя (204)
    create_resp = await async_client.post("/users", json=fake_user_data)
    user_id = create_resp.json()["id"]

    response = await async_client.delete(f"/users/{user_id}")
    assert response.status_code == 204

    # Проверяем, что пользователь действительно удален
    get_resp = await async_client.get(f"/users/{user_id}")
    assert get_resp.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_user(async_client):
    # Повторное удаление (или удаление несуществующего) (404)
    response = await async_client.delete("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"