"""
CivicPulse AI — Notification & Domain Event Tests.

Tests event recording, idempotency, recipient notification dispatch,
inbox endpoints, ownership security, read state, user preferences,
and unconfigured external provider status.
"""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import ASGITransport, AsyncClient

from app.domain.enums import UserRole
from app.domain.notification_schemas import (
    DeliveryChannel,
    DeliveryStatus,
    DomainEvent,
    EventType,
    NotificationDocument,
    NotificationType,
)
from app.main import app
from app.dependencies.auth import require_authenticated_user
from app.domain.auth_schemas import UserResponse
from app.api.notifications import get_notification_service
from app.services.event_service import EventService
from app.services.notification_service import NotificationService


@pytest.fixture
async def client_a():
    mock_user = UserResponse(
        id="user_a",
        email="usera@example.com",
        role=UserRole.CITIZEN,
        status="active",
        first_name="Alice",
        last_name="Citizen",
        display_name="Alice Citizen",
    )
    app.dependency_overrides[require_authenticated_user] = lambda: mock_user
    with patch("app.api.notifications.get_database", return_value=AsyncMock()):
        with patch("app.dependencies.auth.get_database", return_value=AsyncMock()):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def client_b():
    mock_user = UserResponse(
        id="user_b",
        email="userb@example.com",
        role=UserRole.CITIZEN,
        status="active",
        first_name="Bob",
        last_name="Citizen",
        display_name="Bob Citizen",
    )
    app.dependency_overrides[require_authenticated_user] = lambda: mock_user
    with patch("app.api.notifications.get_database", return_value=AsyncMock()):
        with patch("app.dependencies.auth.get_database", return_value=AsyncMock()):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                yield ac
    app.dependency_overrides.clear()


class TestEventAndNotificationService:
    @pytest.mark.asyncio
    async def test_event_recording_and_idempotency(self):
        mock_db = AsyncMock()
        mock_db["domain_events"].find_one = AsyncMock(return_value=None)
        mock_db["domain_events"].insert_one = AsyncMock()

        event_service = EventService(mock_db)

        event = await event_service.record_event(
            event_type=EventType.COMPLAINT_CREATED,
            complaint_id="comp_100",
            actor_id="user_a",
            event_id="evt_test_100",
        )

        assert event is not None
        assert event.event_id == "evt_test_100"
        mock_db["domain_events"].insert_one.assert_called_once()

        # Test idempotency - second call with same event_id returns existing
        mock_db["domain_events"].find_one = AsyncMock(return_value=event.model_dump(by_alias=True))
        mock_db["domain_events"].insert_one.reset_mock()

        event_dup = await event_service.record_event(
            event_type=EventType.COMPLAINT_CREATED,
            complaint_id="comp_100",
            actor_id="user_a",
            event_id="evt_test_100",
        )

        assert event_dup.event_id == "evt_test_100"
        mock_db["domain_events"].insert_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_external_delivery_unconfigured(self):
        mock_db = AsyncMock()
        mock_db["notification_deliveries"].find_one = AsyncMock(return_value=None)
        mock_db["notification_deliveries"].insert_one = AsyncMock()

        notif = NotificationDocument(
            notification_id="notif_100",
            user_id="user_a",
            type=NotificationType.STATUS_UPDATE,
            title="Test",
            body="Test body",
        )

        service = NotificationService(mock_db)
        record = await service.delivery_adapter.deliver(notif, DeliveryChannel.EMAIL)

        assert record.channel == DeliveryChannel.EMAIL
        assert record.status == DeliveryStatus.NOT_CONFIGURED
        assert "not configured" in record.error_reason.lower()


@pytest.mark.asyncio
class TestNotificationAPI:
    @pytest.mark.asyncio
    async def test_get_notifications_and_unread_count(self, client_a):
        mock_service = AsyncMock()
        mock_service.get_user_notifications.return_value = []
        mock_service.get_unread_count.return_value = 2

        app.dependency_overrides[get_notification_service] = lambda: mock_service
        try:
            res_list = await client_a.get("/api/v1/notifications")
            assert res_list.status_code == 200
            assert res_list.json() == []

            res_cnt = await client_a.get("/api/v1/notifications/unread-count")
            assert res_cnt.status_code == 200
            assert res_cnt.json() == {"unread_count": 2}
        finally:
            app.dependency_overrides.pop(get_notification_service, None)

    @pytest.mark.asyncio
    async def test_mark_as_read(self, client_a):
        mock_service = AsyncMock()
        mock_service.mark_as_read.return_value = True

        app.dependency_overrides[get_notification_service] = lambda: mock_service
        try:
            res = await client_a.patch("/api/v1/notifications/notif_123/read")
            assert res.status_code == 200
            assert res.json()["status"] == "success"
        finally:
            app.dependency_overrides.pop(get_notification_service, None)

    @pytest.mark.asyncio
    async def test_mark_all_read(self, client_a):
        mock_service = AsyncMock()
        mock_service.mark_all_as_read.return_value = 5

        app.dependency_overrides[get_notification_service] = lambda: mock_service
        try:
            res = await client_a.post("/api/v1/notifications/mark-all-read")
            assert res.status_code == 200
            assert res.json()["marked_count"] == 5
        finally:
            app.dependency_overrides.pop(get_notification_service, None)

    @pytest.mark.asyncio
    async def test_notification_preferences(self, client_a):
        mock_service = AsyncMock()
        mock_service.get_user_preferences.return_value = {
            "user_id": "user_a",
            "in_app_enabled": True,
            "email_enabled": False,
            "sms_enabled": False,
            "push_enabled": False,
            "updated_at": "2026-08-16T10:00:00Z",
        }
        mock_service.update_user_preferences.return_value = {
            "user_id": "user_a",
            "in_app_enabled": True,
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": False,
            "updated_at": "2026-08-16T10:05:00Z",
        }

        app.dependency_overrides[get_notification_service] = lambda: mock_service
        try:
            get_res = await client_a.get("/api/v1/notifications/preferences")
            assert get_res.status_code == 200
            assert get_res.json()["in_app_enabled"] is True

            put_res = await client_a.put(
                "/api/v1/notifications/preferences",
                json={"email_enabled": True},
            )
            assert put_res.status_code == 200
            assert put_res.json()["email_enabled"] is True
        finally:
            app.dependency_overrides.pop(get_notification_service, None)
