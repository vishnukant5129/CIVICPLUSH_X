"""
CivicPulse AI — Domain Enum Tests.

Tests that all enums have expected values and are consistent.
"""

from __future__ import annotations

import pytest

from app.domain.enums import (
    AIAnalysisStatus,
    AssignmentStatus,
    CivicCategory,
    ComplaintStatus,
    DepartmentStatus,
    EvidenceProcessingStatus,
    NotificationStatus,
    NotificationType,
    PredictionStatus,
    PredictionType,
    UserRole,
    UserStatus,
)


class TestUserRole:
    def test_citizen_exists(self):
        assert UserRole.CITIZEN.value == "citizen"

    def test_authority_exists(self):
        assert UserRole.AUTHORITY.value == "authority"

    def test_admin_exists(self):
        assert UserRole.ADMIN.value == "admin"

    def test_role_count(self):
        assert len(UserRole) == 3


class TestComplaintStatus:
    def test_primary_lifecycle_statuses(self):
        """Primary flow: SUBMITTED → UNDER_REVIEW → VERIFIED → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED"""
        primary = [
            ComplaintStatus.SUBMITTED,
            ComplaintStatus.UNDER_REVIEW,
            ComplaintStatus.VERIFIED,
            ComplaintStatus.ASSIGNED,
            ComplaintStatus.IN_PROGRESS,
            ComplaintStatus.RESOLVED,
            ComplaintStatus.CLOSED,
        ]
        for s in primary:
            assert s.value  # all have non-empty values

    def test_alternate_outcomes(self):
        """Alternate outcomes: REJECTED, DUPLICATE, INVALID"""
        alternates = [
            ComplaintStatus.REJECTED,
            ComplaintStatus.DUPLICATE,
            ComplaintStatus.INVALID,
        ]
        for s in alternates:
            assert s.value

    def test_status_count(self):
        assert len(ComplaintStatus) == 10

    def test_all_values_are_lowercase(self):
        """Values should be consistent lowercase."""
        for status in ComplaintStatus:
            assert status.value == status.value.lower()


class TestCivicCategory:
    def test_prd_categories_present(self):
        """All categories from PRD FR-05 should exist."""
        expected = [
            "pothole_road_damage",
            "streetlight_electricity",
            "water_leakage",
            "sewage_drainage",
            "garbage_waste",
            "public_infrastructure",
            "traffic_signage",
            "other",
        ]
        actual_values = [c.value for c in CivicCategory]
        for cat in expected:
            assert cat in actual_values, f"Missing category: {cat}"

    def test_category_count(self):
        assert len(CivicCategory) == 8


class TestAIAnalysisStatus:
    def test_statuses(self):
        expected = ["pending", "processing", "completed", "failed"]
        for val in expected:
            assert AIAnalysisStatus(val)

    def test_count(self):
        assert len(AIAnalysisStatus) == 4


class TestEvidenceProcessingStatus:
    def test_statuses(self):
        expected = ["pending", "processing", "completed", "failed"]
        for val in expected:
            assert EvidenceProcessingStatus(val)
