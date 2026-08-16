"""
CivicPulse AI — Domain Schema Validation Tests.

Tests that Pydantic schemas enforce all validation rules correctly.
No database connection required — these are pure validation tests.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.domain.enums import (
    CivicCategory,
    ComplaintStatus,
    DepartmentStatus,
    UserRole,
    UserStatus,
)
from app.domain.schemas import (
    AuditLogDocument,
    ComplaintDocument,
    DepartmentDocument,
    EvidenceDocument,
    GeoJSONPoint,
    LocationData,
    StatusHistoryDocument,
    UserDocument,
)


class TestGeoJSONPoint:
    """Test GeoJSON Point validation."""

    def test_valid_coordinates(self):
        point = GeoJSONPoint(coordinates=[77.1025, 28.7041])
        assert point.coordinates == [77.1025, 28.7041]
        assert point.type == "Point"

    def test_longitude_out_of_range_positive(self):
        with pytest.raises(Exception) as exc_info:
            GeoJSONPoint(coordinates=[181.0, 28.0])
        assert "Longitude" in str(exc_info.value) or "longitude" in str(exc_info.value).lower()

    def test_longitude_out_of_range_negative(self):
        with pytest.raises(Exception):
            GeoJSONPoint(coordinates=[-181.0, 28.0])

    def test_latitude_out_of_range_positive(self):
        with pytest.raises(Exception) as exc_info:
            GeoJSONPoint(coordinates=[77.0, 91.0])
        assert "Latitude" in str(exc_info.value) or "latitude" in str(exc_info.value).lower()

    def test_latitude_out_of_range_negative(self):
        with pytest.raises(Exception):
            GeoJSONPoint(coordinates=[77.0, -91.0])

    def test_boundary_values_accepted(self):
        """Boundary values should be valid."""
        GeoJSONPoint(coordinates=[180.0, 90.0])
        GeoJSONPoint(coordinates=[-180.0, -90.0])
        GeoJSONPoint(coordinates=[0.0, 0.0])

    def test_wrong_type_rejected(self):
        with pytest.raises(Exception):
            GeoJSONPoint(type="LineString", coordinates=[77.0, 28.0])

    def test_wrong_coordinate_count_rejected(self):
        with pytest.raises(Exception):
            GeoJSONPoint(coordinates=[77.0])

    def test_too_many_coordinates_rejected(self):
        with pytest.raises(Exception):
            GeoJSONPoint(coordinates=[77.0, 28.0, 100.0])


class TestUserDocument:
    """Test User schema validation."""

    def _valid_user(self, **overrides):
        defaults = {
            "email": "test@example.com",
            "normalized_email": "test@example.com",
            "display_name": "Test User",
        }
        defaults.update(overrides)
        return UserDocument(**defaults)

    def test_valid_user(self):
        user = self._valid_user()
        assert user.email == "test@example.com"
        assert user.role == UserRole.CITIZEN
        assert user.status == UserStatus.ACTIVE
        assert user.department_id is None

    def test_invalid_email_rejected(self):
        with pytest.raises(Exception):
            self._valid_user(email="not-an-email", normalized_email="not-an-email")

    def test_normalized_email_must_be_lowercase(self):
        with pytest.raises(Exception):
            self._valid_user(normalized_email="Test@Example.com")

    def test_email_whitespace_stripped(self):
        user = self._valid_user(email=" test@example.com ")
        assert user.email == "test@example.com"

    def test_display_name_required(self):
        with pytest.raises(Exception):
            UserDocument(email="t@t.com", normalized_email="t@t.com", display_name="")

    def test_display_name_max_length(self):
        with pytest.raises(Exception):
            self._valid_user(display_name="x" * 101)

    def test_timestamps_are_utc(self):
        user = self._valid_user()
        assert user.created_at.tzinfo is not None
        assert user.updated_at.tzinfo is not None


class TestDepartmentDocument:
    """Test Department schema validation."""

    def test_valid_department(self):
        dept = DepartmentDocument(name="Public Works", code="PWD")
        assert dept.status == DepartmentStatus.ACTIVE
        assert dept.description is None

    def test_empty_name_rejected(self):
        with pytest.raises(Exception):
            DepartmentDocument(name="", code="PWD")

    def test_empty_code_rejected(self):
        with pytest.raises(Exception):
            DepartmentDocument(name="Public Works", code="")

    def test_code_max_length(self):
        with pytest.raises(Exception):
            DepartmentDocument(name="Dept", code="x" * 51)


class TestComplaintDocument:
    """Test Complaint schema validation."""

    def _valid_complaint(self, **overrides):
        defaults = {
            "user_id": "507f1f77bcf86cd799439011",
            "title": "Large pothole on Main Street",
            "description": "There is a large pothole causing traffic issues and vehicle damage.",
            "category": CivicCategory.POTHOLE_ROAD_DAMAGE,
            "location": LocationData(
                geo=GeoJSONPoint(coordinates=[77.1025, 28.7041]),
                address="123 Main Street",
            ),
        }
        defaults.update(overrides)
        return ComplaintDocument(**defaults)

    def test_valid_complaint(self):
        complaint = self._valid_complaint()
        assert complaint.status == ComplaintStatus.SUBMITTED
        assert complaint.priority_score is None
        assert complaint.evidence_count == 0

    def test_title_min_length(self):
        with pytest.raises(Exception):
            self._valid_complaint(title="Hi")

    def test_title_max_length(self):
        with pytest.raises(Exception):
            self._valid_complaint(title="x" * 301)

    def test_description_min_length(self):
        with pytest.raises(Exception):
            self._valid_complaint(description="Short")

    def test_description_max_length(self):
        with pytest.raises(Exception):
            self._valid_complaint(description="x" * 5001)

    def test_priority_score_range(self):
        c = self._valid_complaint(priority_score=50.0)
        assert c.priority_score == 50.0

    def test_priority_score_negative_rejected(self):
        with pytest.raises(Exception):
            self._valid_complaint(priority_score=-1.0)

    def test_priority_score_over_100_rejected(self):
        with pytest.raises(Exception):
            self._valid_complaint(priority_score=101.0)

    def test_invalid_category_rejected(self):
        with pytest.raises(Exception):
            self._valid_complaint(category="nonexistent_category")

    def test_all_statuses_accepted(self):
        """All ComplaintStatus values should be valid."""
        for status in ComplaintStatus:
            c = self._valid_complaint(status=status)
            assert c.status == status


class TestEvidenceDocument:
    """Test Evidence schema validation."""

    def test_valid_evidence(self):
        ev = EvidenceDocument(
            complaint_id="507f1f77bcf86cd799439011",
            user_id="507f1f77bcf86cd799439012",
            storage_key="uploads/2026/08/abc123.jpg",
            original_filename="photo.jpg",
            mime_type="image/jpeg",
            size_bytes=1024000,
        )
        assert ev.processing_status.value == "pending"

    def test_negative_size_rejected(self):
        with pytest.raises(Exception):
            EvidenceDocument(
                complaint_id="x",
                user_id="x",
                storage_key="k",
                original_filename="f.jpg",
                mime_type="image/jpeg",
                size_bytes=-1,
            )


class TestStatusHistoryDocument:
    """Test StatusHistory schema validation."""

    def test_valid_transition(self):
        sh = StatusHistoryDocument(
            complaint_id="507f1f77bcf86cd799439011",
            previous_status=ComplaintStatus.SUBMITTED,
            new_status=ComplaintStatus.UNDER_REVIEW,
            actor_id="507f1f77bcf86cd799439012",
            reason="Initial review started.",
        )
        assert sh.previous_status == ComplaintStatus.SUBMITTED
        assert sh.new_status == ComplaintStatus.UNDER_REVIEW

    def test_initial_transition_no_previous(self):
        """First status entry may have no previous_status."""
        sh = StatusHistoryDocument(
            complaint_id="507f1f77bcf86cd799439011",
            new_status=ComplaintStatus.SUBMITTED,
        )
        assert sh.previous_status is None
        assert sh.actor_id is None


class TestAuditLogDocument:
    """Test AuditLog schema validation."""

    def test_valid_audit_log(self):
        log = AuditLogDocument(
            actor_id="507f1f77bcf86cd799439012",
            action="complaint.created",
            resource_type="complaint",
            resource_id="507f1f77bcf86cd799439011",
        )
        assert log.metadata is None
        assert log.created_at.tzinfo is not None

    def test_system_actor(self):
        """System actions may have actor_id=None."""
        log = AuditLogDocument(
            action="system.index_rebuild",
            resource_type="database",
            resource_id="complaints",
        )
        assert log.actor_id is None
