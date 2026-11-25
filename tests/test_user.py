import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


async def test_get_existed_user(client):
    response = await client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


async def test_create_user(client):
    payload = {"name": "Test User", "email": "test@example.com"}
    response = await client.post("/users", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == payload["name"]
    assert "id" in body


async def test_get_not_existed_user(client):
    response = await client.get("/users/999999")
    assert response.status_code == 404


async def test_update_user(client):
    created = (await client.post(
        "/users", json={"name": "Old", "email": "old@example.com"}
    )).json()
    response = await client.put(
        f"/users/{created['id']}", json={"name": "New", "email": "new@example.com"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New"


async def test_delete_user(client):
    created = (await client.post(
        "/users", json={"name": "ToDelete", "email": "del@example.com"}
    )).json()
    response = await client.delete(f"/users/{created['id']}")
    assert response.status_code == 204
    assert (await client.get(f"/users/{created['id']}")).status_code == 404
