import asyncio
from datetime import datetime, timedelta, timezone

import pytest

pytestmark = pytest.mark.asyncio


async def assert_ok_response(response, expected_status: int):
    if response.status_code != expected_status:
        try:
            body = response.json()
        except Exception:
            body = response.text
        pytest.fail(
            f"Expected status {expected_status}, got {response.status_code}. Response body: {body}"
        )


async def test_create_deal_success(async_client):
    payload = {
        "title": "New Deal",
        "description": "A great deal",
        "image_url": "http://example.com/image.jpg",
        "price_cents": 5000,
        "min_qty_to_close": 5,
        "end_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
    }
    response = await async_client.post("/api/v1/admin/deals", json=payload)
    await assert_ok_response(response, 201)

    data = response.json()["data"]
    assert "id" in data
    assert data["title"] == payload["title"]
    assert data["status"] == "ACTIVE"
    assert data["current_qty"] == 0
    assert data["min_qty_to_close"] == 5


async def test_list_deals_pagination(async_client, db_session):
    from app.models.deal import Deal

    for i in range(15):
        deal = Deal(
            title=f"Deal {i}",
            description=f"Description {i}",
            price_cents=1000,
            min_qty_to_close=10,
            current_qty=0,
            end_at=datetime.now(timezone.utc) + timedelta(days=1),
            status="ACTIVE",
        )
        db_session.add(deal)
    db_session.commit()

    response = await async_client.get("/api/v1/deals?page=1&page_size=10")
    await assert_ok_response(response, 200)

    data = response.json()["data"]
    assert len(data["items"]) == 10
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total"] == 15

    response = await async_client.get("/api/v1/deals?page=2&page_size=10")
    await assert_ok_response(response, 200)

    data = response.json()["data"]
    assert len(data["items"]) == 5
    assert data["page"] == 2
    assert data["total"] == 15


async def test_join_deal_creates_participant_and_increments_qty(async_client, seed_deal):
    payload = {"name": "John Doe", "email": "john@example.com", "qty": 3}

    response = await async_client.post(f"/api/v1/deals/{seed_deal.id}/join", params=payload)
    await assert_ok_response(response, 200)

    data = response.json()["data"]
    assert data["deal"]["current_qty"] == 3
    assert data["participant"]["name"] == "John Doe"
    assert data["participant"]["email"] == "john@example.com"
    assert data["participant"]["qty"] == 3


async def test_join_deal_updates_existing_participant_and_adjusts_delta(async_client, seed_deal):
    payload = {"name": "John Doe", "email": "john@example.com", "qty": 3}

    first = await async_client.post(f"/api/v1/deals/{seed_deal.id}/join", params=payload)
    await assert_ok_response(first, 200)

    payload["qty"] = 5
    response = await async_client.post(f"/api/v1/deals/{seed_deal.id}/join", params=payload)
    await assert_ok_response(response, 200)

    data = response.json()["data"]
    assert data["deal"]["current_qty"] == 5
    assert data["participant"]["qty"] == 5


async def test_join_rejects_if_deal_closed(async_client, seed_deal, db_session):
    seed_deal.status = "CLOSED"
    db_session.commit()

    payload = {"name": "Jane Doe", "email": "jane@example.com", "qty": 1}
    response = await async_client.post(f"/api/v1/deals/{seed_deal.id}/join", params=payload)

    assert response.status_code in (400, 409), response.text

    db_session.refresh(seed_deal)
    assert seed_deal.current_qty == 0


async def test_close_deals_marks_closed_and_generates_tracking_ids(async_client, db_session):
    from app.models.deal import Deal
    from app.models.participant import Participant

    deal = Deal(
        title="Close Test",
        description="Test",
        price_cents=1000,
        min_qty_to_close=5,
        current_qty=6,
        end_at=datetime.now(timezone.utc) - timedelta(days=1),
        status="ACTIVE",
    )
    db_session.add(deal)
    db_session.commit()
    db_session.refresh(deal)

    part1 = Participant(deal_id=deal.id, name="P1", email="p1@example.com", qty=3, state="JOINED")
    part2 = Participant(deal_id=deal.id, name="P2", email="p2@example.com", qty=3, state="JOINED")
    db_session.add_all([part1, part2])
    db_session.commit()

    response = await async_client.post("/api/v1/jobs/close-deals")
    await assert_ok_response(response, 200)

    data = response.json()["data"]
    assert data["closed_count"] == 1
    assert data["failed_count"] == 0

    db_session.refresh(deal)
    assert str(deal.status) == "CLOSED" or deal.status == "CLOSED"

    db_session.refresh(part1)
    db_session.refresh(part2)
    assert part1.tracking_id is not None
    assert part2.tracking_id is not None
    assert str(part1.state) == "INVITED_TO_PAY" or part1.state == "INVITED_TO_PAY"
    assert str(part2.state) == "INVITED_TO_PAY" or part2.state == "INVITED_TO_PAY"


async def test_close_deals_marks_failed_if_threshold_not_met(async_client, db_session):
    from app.models.deal import Deal

    deal = Deal(
        title="Fail Test",
        description="Test",
        price_cents=1000,
        min_qty_to_close=10,
        current_qty=5,
        end_at=datetime.now(timezone.utc) - timedelta(days=1),
        status="ACTIVE",
    )
    db_session.add(deal)
    db_session.commit()
    db_session.refresh(deal)

    response = await async_client.post("/api/v1/jobs/close-deals")
    await assert_ok_response(response, 200)

    data = response.json()["data"]
    assert data["closed_count"] == 0
    assert data["failed_count"] == 1

    db_session.refresh(deal)
    assert str(deal.status) == "FAILED" or deal.status == "FAILED"


async def test_concurrency_simulate_parallel_joins(async_client, seed_deal):
    async def join_user(user_id: int):
        payload = {"name": f"User {user_id}", "email": f"user{user_id}@example.com", "qty": 1}
        return await async_client.post(f"/api/v1/deals/{seed_deal.id}/join", params=payload)

    responses = await asyncio.gather(*[join_user(i) for i in range(10)])

    for r in responses:
        assert r.status_code == 200, r.text

    response = await async_client.get(f"/api/v1/deals/{seed_deal.id}")
    await assert_ok_response(response, 200)
    assert response.json()["data"]["current_qty"] == 10