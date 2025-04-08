import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

@pytest.mark.asyncio(loop_scope="session")
async def test_full_table_lifecycle(client: AsyncClient):
    response = await client.post(
        "/tables/",
        json={"name": "VIP Table", "seats": 6, "location": "Lounge"}
    )
    assert response.status_code == 200

    list_response = await client.get("/tables/")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    table_id = response.json()["id"]
    delete_response = await client.delete(f"/tables/{table_id}")
    assert delete_response.status_code == 200

    get_deleted_response = await client.get(f"/tables/{table_id}")
    assert get_deleted_response.status_code == 404

@pytest.mark.asyncio(loop_scope="session")
async def test_full_reservation_lifecycle(client: AsyncClient):
    table_response = await client.post(
        "/tables/",
        json={"name": "Reservation Table", "seats": 4, "location": "Terrace"}
    )
    assert table_response.status_code == 200
    table_id = table_response.json()["id"]

    reservation_response = await client.post(
        "/reservations/",
        json={
            "customer_name": "First Customer",
            "table_id": table_id,
            "reservation_time": "2024-01-01T18:00:00",
            "duration_minutes": 120
        }
    )
    assert reservation_response.status_code == 200
    reservation_id = reservation_response.json()["id"]
    
    delete_response = await client.delete(f"/reservations/{reservation_id}")
    assert delete_response.status_code == 200

    get_deleted_response = await client.get(f"/reservations/{reservation_id}")
    assert get_deleted_response.status_code == 404

@pytest.mark.asyncio(loop_scope="session")
async def test_reservation_conflicts(client: AsyncClient):
    table = await client.post("/tables/", json={
        "name": "Conflict Test",
        "seats": 4,
        "location": "Test Area"
    })
    table_id = table.json()["id"]

    res1 = await client.post("/reservations/", json={
        "customer_name": "First",
        "table_id": table_id,
        "reservation_time": "2024-01-01T18:00:00",
        "duration_minutes": 120
    })
    assert res1.status_code == 200

    test_cases = [
        {
            "time": "2024-01-01T17:30:00",
            "duration": 90,
            "expected": 400
        },
        {
            "time": "2024-01-01T19:00:00",
            "duration": 60,
            "expected": 400
        },
        {
            "time": "2024-01-01T20:00:00",
            "duration": 30,
            "expected": 200
        },
        {
            "time": "2024-01-01T16:00:00",
            "duration": 120,
            "expected": 200
        }
    ]

    for case in test_cases:
        response = await client.post("/reservations/", json={
            "customer_name": "Conflict Test",
            "table_id": table_id,
            "reservation_time": case["time"],
            "duration_minutes": case["duration"]
        })
        assert response.status_code == case["expected"]
        if case["expected"] == 200:
            await client.delete(f"/reservations/{response.json()['id']}")

@pytest.mark.asyncio(loop_scope="session")
async def test_invalid_operations(client: AsyncClient):
    table = await client.post("/tables/", json={
        "name": "Test Table",
        "seats": 4,
        "location": "Hall"
    })
    valid_table_id = table.json()["id"]

    response = await client.post("/reservations/", json={
        "customer_name": "Test",
        "table_id": 999,
        "reservation_time": "2023-12-01T20:00:00",
        "duration_minutes": 60
    })
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]

    delete_table = await client.delete("/tables/999")
    assert delete_table.status_code == 404

    res1 = await client.post("/reservations/", json={
        "customer_name": "First",
        "table_id": valid_table_id,
        "reservation_time": "2023-12-01T18:00:00",
        "duration_minutes": 120
    })
    assert res1.status_code == 200

    res2 = await client.post("/reservations/", json={
        "customer_name": "Second",
        "table_id": valid_table_id,
        "reservation_time": "2023-12-01T19:00:00",
        "duration_minutes": 60
    })
    assert res2.status_code == 400
    assert "conflicts" in res2.json()["detail"]