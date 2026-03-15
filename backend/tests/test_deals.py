import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from app.models.participant import Participant

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


async def test_create_deal_validation_error(async_client):
    # end_at in the past should trigger a 422 and the error handler must
    # produce a serializable response (no ValueError objects leaked).
    payload = {
        "title": "Old Deal",
        "description": "Expired",
        "price_cents": 1000,
        "min_qty_to_close": 1,
        "end_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    }
    response = await async_client.post("/api/v1/admin/deals", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    # the details list should not contain non-serializable ctx entries
    for err in body["error"]["details"]:
        assert "ctx" not in err or isinstance(err["ctx"], dict)
        # message should mention end_at or future
        assert "end_at" in err.get("loc", [])


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
    payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "qty": 3,
        "city": "Metropolis",
        "street": "Main St",
        "house_number": "123",
    }

    response = await async_client.post(f"/api/v1/deals/{seed_deal.id}/join", json=payload)
    await assert_ok_response(response, 200)

    data = response.json()["data"]
    assert data["deal"]["current_qty"] == 3
    assert data["participant"]["name"] == "John Doe"
    assert data["participant"]["email"] == "john@example.com"
    assert data["participant"]["qty"] == 3
    assert data["participant"]["city"] == "Metropolis"


async def test_join_deal_updates_existing_participant_and_adjusts_delta(async_client, seed_deal):
    payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "qty": 3,
        "city": "Metropolis",
        "street": "Main St",
        "house_number": "123",
    }

    first = await async_client.post(f"/api/v1/deals/{seed_deal.id}/join", json=payload)
    await assert_ok_response(first, 200)

    payload["qty"] = 5
    response = await async_client.post(f"/api/v1/deals/{seed_deal.id}/join", json=payload)
    await assert_ok_response(response, 200)

    data = response.json()["data"]
    assert data["deal"]["current_qty"] == 5
    assert data["participant"]["qty"] == 5


async def test_join_rejects_if_deal_closed(async_client, seed_deal, db_session):
    seed_deal.status = "CLOSED"
    db_session.commit()

    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "qty": 1,
        "city": "Gotham",
        "street": "1st Ave",
        "house_number": "1",
    }
    response = await async_client.post(f"/api/v1/deals/{seed_deal.id}/join", json=payload)

    assert response.status_code in (400, 409), response.text

    db_session.refresh(seed_deal)
    assert seed_deal.current_qty == 0


async def test_token_and_confirmation_flow(async_client, seed_deal, db_session):
    # join and ensure token is generated
    payload = {
        "name": "Token User",
        "email": "token@example.com",
        "qty": 2,
        "city": "City",
        "street": "Road",
        "house_number": "5",
    }
    await async_client.post(f"/api/v1/deals/{seed_deal.id}/join", json=payload)
    part = db_session.execute(
        select(Participant).where(Participant.email == "token@example.com")
    ).scalar_one()
    assert part.confirmation_token is not None
    assert not part.is_confirmed

    # confirm via API
    response = await async_client.post(f"/api/v1/confirm/{part.confirmation_token}")
    await assert_ok_response(response, 200)
    db_session.refresh(part)
    assert part.is_confirmed
    assert part.confirmation_token is None


async def test_send_confirmation_reminders(async_client, seed_deal, db_session, monkeypatch):
    # create several participants with different reminder counts
    from app.services.email_service import email_service

    sent = []
    def fake_send(to, sub, body, html=None):
        sent.append(to)
    monkeypatch.setattr(email_service, 'send_email', fake_send)

    # participant who just joined (reminder_count 0) and deal closing in 1 day
    part1 = Participant(
        deal_id=seed_deal.id,
        name="P1",
        email="p1@example.com",
        qty=1,
        state="JOINED",
        city="City", street="St", house_number="1",
        confirmation_token="token1",
    )
    db_session.add(part1)
    # participant already reminded once (reminder_count 1)
    part2 = Participant(
        deal_id=seed_deal.id,
        name="P2",
        email="p2@example.com",
        qty=1,
        state="JOINED",
        city="City", street="St", house_number="2",
        confirmation_token="token2",
        reminder_count=1,
    )
    db_session.add(part2)
    db_session.commit()

    # set deal end time to 1 day from now
    from datetime import datetime, timedelta, timezone
    seed_deal.end_at = datetime.now(timezone.utc) + timedelta(days=1)
    db_session.commit()

    response = await async_client.post("/api/v1/jobs/send-confirmation-reminders")
    await assert_ok_response(response, 200)
    data = response.json()["data"]
    assert data["sent"] >= 1
    assert len(sent) >= 1


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
        payload = {
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com",
            "qty": 1,
            "city": "City",
            "street": "Street",
            "house_number": str(user_id),
        }
        return await async_client.post(f"/api/v1/deals/{seed_deal.id}/join", json=payload)

    responses = await asyncio.gather(*[join_user(i) for i in range(10)])

    for r in responses:
        assert r.status_code == 200, r.text

    response = await async_client.get(f"/api/v1/deals/{seed_deal.id}")
    await assert_ok_response(response, 200)
    data = response.json()["data"]
    assert data["current_qty"] == 10
    # participants_count should reflect the 10 joins
    assert data.get("participants_count") == 10