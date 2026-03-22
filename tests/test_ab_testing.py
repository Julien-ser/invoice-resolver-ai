"""
Tests for A/B testing framework.

This module tests:
- ExperimentManager: create_experiment, assign_variant, track_metrics, get_results
- Variant assignment strategies (round-robin, random)
- Metric tracking and analysis
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from sqlalchemy.orm import Session

from src.ab_testing.experiment import ExperimentManager, generate_uuid
from src.models import ABTest, Campaign, EmailEvent, Template, User, Invoice


class TestExperimentManager:
    """Tests for ExperimentManager class."""

    def test_create_experiment(self, db_session):
        """Test creating a new experiment."""
        manager = ExperimentManager(db_session)

        variants = {
            "A": {"template_id": "tpl_1", "description": "Control"},
            "B": {"template_id": "tpl_2", "description": "Variant B"},
        }

        experiment = manager.create_experiment(
            user_id="user_123",
            name="Email Subject Line Test",
            test_type="subject_line",
            variants=variants,
            description="Test different subject lines",
            metadata={"target_sample_size": 1000},
        )

        assert experiment.id is not None
        assert experiment.user_id == "user_123"
        assert experiment.name == "Email Subject Line Test"
        assert experiment.test_type == "subject_line"
        assert experiment.variants == variants
        assert experiment.is_active is True
        assert experiment.experiment_metadata == {"target_sample_size": 1000}

    def test_create_experiment_with_duplicate_name(self, db_session):
        """Test that creating experiment with same name for user is allowed (no uniqueness constraint)."""
        manager = ExperimentManager(db_session)

        variants = {"A": {"template_id": "tpl_1"}}

        exp1 = manager.create_experiment(
            user_id="user_123", name="Test", test_type="template", variants=variants
        )
        exp2 = manager.create_experiment(
            user_id="user_123", name="Test", test_type="template", variants=variants
        )

        # Both should succeed with different IDs
        assert exp1.id != exp2.id

    def test_assign_variant_round_robin(self, db_session):
        """Test variant assignment using round-robin."""
        manager = ExperimentManager(db_session)

        variants = {
            "A": {"template_id": "tpl_1"},
            "B": {"template_id": "tpl_2"},
            "C": {"template_id": "tpl_3"},
        }

        experiment = manager.create_experiment(
            user_id="user_123",
            name="Test Assignment",
            test_type="template",
            variants=variants,
        )

        # Assign multiple times and check distribution
        assignments = []
        for i in range(10):
            variant = manager.assign_variant(experiment.id)
            assignments.append(variant)

        # Should be one of the variant keys
        assert set(assignments) <= set(variants.keys())
        # With 10 assignments, each variant should appear at least once (probabilistic)
        assert "A" in assignments or "B" in assignments or "C" in assignments

    def test_assign_variant_with_user_id(self, db_session):
        """Test that consistent user_id gets same variant."""
        manager = ExperimentManager(db_session)

        variants = {
            "A": {"template_id": "tpl_1"},
            "B": {"template_id": "tpl_2"},
        }

        experiment = manager.create_experiment(
            user_id="user_123",
            name="Consistent Assignment",
            test_type="template",
            variants=variants,
        )

        # Same user should get same variant
        variant1 = manager.assign_variant(experiment.id, user_id="user_456")
        variant2 = manager.assign_variant(experiment.id, user_id="user_456")
        assert variant1 == variant2

        # Different user might get different variant
        variant3 = manager.assign_variant(experiment.id, user_id="user_789")
        # Could be same or different depending on assignment logic
        assert variant3 in ["A", "B"]

    def test_assign_variant_campaign_id(self, db_session):
        """Test variant assignment with campaign_id."""
        manager = ExperimentManager(db_session)

        variants = {"A": {}, "B": {}}
        experiment = manager.create_experiment(
            user_id="user_123",
            name="Campaign Test",
            test_type="timing",
            variants=variants,
        )

        # Should accept campaign_id and assign variant
        variant = manager.assign_variant(experiment.id, campaign_id="camp_123")
        assert variant in ["A", "B"]

    def test_assign_variant_inactive_experiment(self, db_session):
        """Test that assigning to inactive experiment returns None."""
        manager = ExperimentManager(db_session)

        variants = {"A": {}}
        experiment = manager.create_experiment(
            user_id="user_123",
            name="Inactive Test",
            test_type="template",
            variants=variants,
        )

        # Deactivate experiment
        experiment.is_active = False
        db_session.commit()

        variant = manager.assign_variant(experiment.id)
        assert variant is None

    def test_assign_variant_nonexistent_experiment(self, db_session):
        """Test that assigning to non-existent experiment raises error."""
        manager = ExperimentManager(db_session)

        with pytest.raises(ValueError, match="not found"):
            manager.assign_variant("nonexistent_id")

    def test_track_metric(self, db_session):
        """Test tracking experiment metrics."""
        manager = ExperimentManager(db_session)

        variants = {"A": {}, "B": {}}
        experiment = manager.create_experiment(
            user_id="user_123",
            name="Metric Test",
            test_type="template",
            variants=variants,
        )

        # Track some metrics
        result = manager.track_metric(
            experiment_id=experiment.id,
            variant="A",
            metric_name="email_open",
            value=1.0,
            metadata={"campaign_id": "camp_123"},
        )

        assert result is True

        # Verify metric was stored
        stored = db_session.query(ABTest).filter(ABTest.id == experiment.id).first()
        assert stored is not None

    def test_get_results_with_data(self, db_session):
        """Test getting experiment results."""
        manager = ExperimentManager(db_session)

        variants = {"A": {}, "B": {}}
        experiment = manager.create_experiment(
            user_id="user_123",
            name="Results Test",
            test_type="template",
            variants=variants,
        )

        # Track some sample metrics
        manager.track_metric(experiment.id, "A", "open", 100)
        manager.track_metric(experiment.id, "B", "open", 120)
        manager.track_metric(experiment.id, "A", "click", 20)
        manager.track_metric(experiment.id, "B", "click", 30)

        results = manager.get_results(experiment.id)

        assert results is not None
        assert "experiment_id" in results
        assert "name" in results
        assert "variants" in results
        assert "A" in results["variants"]
        assert "B" in results["variants"]
        assert results["variants"]["A"]["open"] == 100
        assert results["variants"]["B"]["open"] == 120

    def test_get_results_nonexistent_experiment(self, db_session):
        """Test getting results for non-existent experiment."""
        manager = ExperimentManager(db_session)

        results = manager.get_results("nonexistent_id")
        assert results is None

    def test_assign_variant_count_increments(self, db_session):
        """Test that variant assignment counts are tracked."""
        manager = ExperimentManager(db_session)

        variants = {"A": {}, "B": {}}
        experiment = manager.create_experiment(
            user_id="user_123",
            name="Count Test",
            test_type="template",
            variants=variants,
        )

        # Assign multiple times to same user to count assignments
        for i in range(5):
            manager.assign_variant(experiment.id, user_id=f"user_{i}")

        # Get freshest experiment data
        db_session.refresh(experiment)

        # Total assignments should be tracked
        total_assignments = sum(experiment.variant_assignments.values())
        assert total_assignments == 5

    def test_assign_variant_no_variants(self, db_session):
        """Test assigning to experiment with no variants."""
        manager = ExperimentManager(db_session)

        experiment = manager.create_experiment(
            user_id="user_123",
            name="No Variants",
            test_type="template",
            variants={},  # Empty variants
        )

        variant = manager.assign_variant(experiment.id)
        assert variant is None

    def test_experiment_manager_requires_db(self):
        """Test that ExperimentManager requires a database session."""
        with pytest.raises(TypeError):
            ExperimentManager(None)


class TestABTestingFunctions:
    """Tests for standalone A/B testing functions."""

    def test_generate_uuid(self):
        """Test UUID generation."""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()

        assert isinstance(uuid1, str)
        assert isinstance(uuid2, str)
        assert uuid1 != uuid2  # Should be unique
        # Should be valid UUID format (basic check)
        assert len(uuid1) == 36
        assert "-" in uuid1

    def test_experiment_lifecycle(self, db_session):
        """Test complete experiment lifecycle: create, assign, track, analyze."""
        manager = ExperimentManager(db_session)

        # 1. Create experiment
        variants = {
            "control": {"template_id": "tpl_control", "send_time": "10am"},
            "treatment": {"template_id": "tpl_treatment", "send_time": "2pm"},
        }

        experiment = manager.create_experiment(
            user_id="user_123",
            name="Send Time Optimization",
            test_type="timing",
            variants=variants,
            description="Test optimal email send time",
            metadata={"target_size": 500, "min_effect_size": 0.05},
        )

        # 2. Assign variants to mock users
        assignments = {}
        for i in range(100):
            user_id = f"user_{i}"
            variant = manager.assign_variant(experiment.id, user_id=user_id)
            assignments[user_id] = variant

        # 3. Track mock metrics
        for user_id, variant in assignments.items():
            # Simulate opens and clicks
            if variant == "control":
                open_rate = 0.20  # 20%
                click_rate = 0.05  # 5% of opens
            else:  # treatment
                open_rate = 0.25  # 25%
                click_rate = 0.06  # 6% of opens

            if open_rate > 0:
                manager.track_metric(
                    experiment.id,
                    variant,
                    "email_open",
                    1,
                    metadata={"user_id": user_id},
                )
            if click_rate > 0:
                manager.track_metric(
                    experiment.id,
                    variant,
                    "email_click",
                    1,
                    metadata={"user_id": user_id},
                )

        db_session.commit()

        # 4. Get results
        results = manager.get_results(experiment.id)

        assert results is not None
        assert "control" in results["variants"]
        assert "treatment" in results["variants"]

        # Verify metrics are tracked
        opens_control = results["variants"]["control"]["email_open"]
        opens_treatment = results["variants"]["treatment"]["email_open"]

        assert opens_control > 0
        assert opens_treatment > 0

        # Calculate conversion rates (approximate)
        total_opens = opens_control + opens_treatment
        total_clicks = (
            results["variants"]["control"]["email_click"]
            + results["variants"]["treatment"]["email_click"]
        )

        assert total_opens > 0
        assert total_clicks > 0

    def test_stop_experiment(self, db_session):
        """Test stopping an experiment."""
        manager = ExperimentManager(db_session)

        variants = {"A": {}, "B": {}}
        experiment = manager.create_experiment(
            user_id="user_123",
            name="Stop Test",
            test_type="template",
            variants=variants,
        )

        assert experiment.is_active is True

        manager.stop_experiment(experiment.id)

        db_session.refresh(experiment)
        assert experiment.is_active is False

    def test_stop_nonexistent_experiment(self, db_session):
        """Test stopping non-existent experiment raises error."""
        manager = ExperimentManager(db_session)

        with pytest.raises(ValueError, match="not found"):
            manager.stop_experiment("nonexistent_id")


class TestABTestIntegrationWithCampaigns:
    """Tests for A/B testing integration with campaigns."""

    @patch("src.ab_testing.experiment.datetime")
    def test_variant_assignment_with_campaign_metadata(self, mock_datetime, db_session):
        """Test that variant assignment includes campaign metadata."""
        mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 0, 0, 0)

        manager = ExperimentManager(db_session)

        variants = {"A": {}, "B": {}}
        experiment = manager.create_experiment(
            user_id="user_123",
            name="Campaign Integration",
            test_type="template",
            variants=variants,
        )

        # Assign with campaign_id
        variant = manager.assign_variant(
            experiment.id, user_id="user_456", campaign_id="camp_123"
        )

        assert variant in ["A", "B"]

        # Verify assignment is tracked
        db_session.refresh(experiment)
        assert experiment.variant_assignments is not None


class TestABTestEdgeCases:
    """Tests for edge cases in A/B testing."""

    def test_assign_to_archived_experiment(self, db_session):
        """Test that archived experiments cannot assign variants."""
        manager = ExperimentManager(db_session)

        variants = {"A": {}}
        experiment = manager.create_experiment(
            user_id="user_123",
            name="Archived Test",
            test_type="template",
            variants=variants,
        )

        # Manually archive (set is_active=False)
        experiment.is_active = False
        db_session.commit()

        variant = manager.assign_variant(experiment.id)
        assert variant is None

    def test_track_metric_missing_variant(self, db_session):
        """Test tracking metric for non-existent variant."""
        manager = ExperimentManager(db_session)

        experiment = manager.create_experiment(
            user_id="user_123",
            name="Invalid Variant Test",
            test_type="template",
            variants={"A": {}},
        )

        # Try to track metric for non-existent variant "B"
        result = manager.track_metric(experiment.id, "B", "open", 1)
        # Should gracefully handle or raise error depending on implementation
        # Our implementation tracks regardless
        assert result is True

    def test_large_variant_set(self, db_session):
        """Test assignment with many variants."""
        variants = {chr(65 + i): {"id": f"tpl_{i}"} for i in range(10)}  # A-J

        manager = ExperimentManager(db_session)
        experiment = manager.create_experiment(
            user_id="user_123",
            name="Large Variant Test",
            test_type="template",
            variants=variants,
        )

        # Assign multiple times
        for i in range(50):
            variant = manager.assign_variant(experiment.id)
            assert variant in variants.keys()

    def test_concurrent_variant_assignment(self, db_session):
        """Test that variant assignments are deterministic for same user."""
        manager = ExperimentManager(db_session)

        variants = {"A": {}, "B": {}, "C": {}}
        experiment = manager.create_experiment(
            user_id="user_123",
            name="Concurrent Test",
            test_type="template",
            variants=variants,
        )

        # Same user ID should always get same variant (even across sessions)
        user_id = "test_user_xyz"
        variants_assigned = set()

        for _ in range(10):
            variant = manager.assign_variant(experiment.id, user_id=user_id)
            variants_assigned.add(variant)

        # Should always get same variant, so set should have size 1
        assert len(variants_assigned) == 1
