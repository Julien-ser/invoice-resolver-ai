"""
A/B Testing Framework for invoice follow-up campaigns.

This module provides functionality for:
- Creating and managing A/B test experiments
- Assigning variants to users/campaigns
- Tracking metrics (opens, clicks, payments)
- Analyzing results and determining winning variants
"""

from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any, cast
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import uuid

from ..models import ABTest, Campaign, EmailEvent, Template, User
from ..core.database import get_session


def generate_uuid():
    """Generate a new UUID string."""
    return str(uuid.uuid4())


class ExperimentManager:
    """Manager for A/B testing experiments."""

    def __init__(self, db: Session):
        self.db = db

    def create_experiment(
        self,
        user_id: str,
        name: str,
        test_type: str,
        variants: Dict[str, dict],
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> ABTest:
        """
        Create a new A/B test experiment.

        Args:
            user_id: ID of user creating the experiment
            name: Human-readable experiment name
            test_type: Type of test ('template', 'timing', 'subject_line')
            variants: Dict mapping variant IDs to variant config
                      Example: {
                          "A": {"template_id": "uuid1", "description": "Control"},
                          "B": {"template_id": "uuid2", "description": "Variant B"}
                      }
            description: Optional experiment description
            metadata: Optional additional metadata (target sample size, etc.)

        Returns:
            ABTest: Created experiment record
        """
        experiment = ABTest(
            user_id=user_id,
            name=name,
            description=description,
            test_type=test_type,
            variants=variants,
            experiment_metadata=metadata or {},
            is_active=True,
        )
        self.db.add(experiment)
        self.db.commit()
        self.db.refresh(experiment)
        return experiment

    def assign_variant(
        self,
        experiment_id: str,
        user_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Assign a variant to a user/campaign using round-robin or random assignment.

        Args:
            experiment_id: ID of the experiment
            user_id: Optional user ID for consistent assignment
            campaign_id: Optional campaign ID

        Returns:
            Optional[str]: Variant ID (e.g., "A", "B") or None if no variants
        """
        experiment = (
            self.db.query(ABTest)
            .filter(ABTest.id == experiment_id, ABTest.is_active == True)
            .first()
        )

        if not experiment:
            raise ValueError(f"Active experiment {experiment_id} not found")

        variants = list(experiment.variants.keys())
        if not variants:
            raise ValueError(f"Experiment {experiment_id} has no variants defined")

        # For consistent user assignment (user gets same variant across campaigns)
        if user_id:
            # Get existing assignments for this user and experiment
            existing_campaigns = (
                self.db.query(Campaign)
                .filter(
                    Campaign.user_id == user_id,
                    Campaign.ab_test_variant.isnot(None),
                )
                .all()
            )

            # If user already has a variant assigned in this experiment, use it
            for campaign in existing_campaigns:
                if campaign.ab_test_variant in variants:
                    return campaign.ab_test_variant

        # Simple round-robin based on total assignments
        variant_counts = {}
        for variant in variants:
            query = self.db.query(func.count(Campaign.id)).filter(
                Campaign.ab_test_variant == variant
            )
            if user_id:
                query = query.filter(Campaign.user_id == user_id)
            count = query.scalar() or 0
            variant_counts[variant] = count

        # Assign to variant with lowest count
        if not variant_counts:
            return None
        assigned_variant = min(variant_counts, key=lambda k: variant_counts[k])
        return assigned_variant

    def track_event(
        self,
        campaign_id: str,
        event_type: str,
        event_data: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> EmailEvent:
        """
        Track an email event (opened, clicked, etc.) for a campaign.

        Args:
            campaign_id: Campaign ID
            event_type: Type of event ('opened', 'clicked', 'bounced', etc.)
            event_data: Additional event data
            ip_address: IP address of the event
            user_agent: User agent string

        Returns:
            EmailEvent: Created event record
        """
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        event = EmailEvent(
            campaign_id=campaign_id,
            event_type=event_type,
            event_data=event_data or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(event)

        # Update campaign tracking fields
        if event_type == "opened":
            campaign.opened_at = func.now()
            campaign.opened_count = (campaign.opened_count or 0) + 1
        elif event_type == "clicked":
            campaign.clicked_at = func.now()
        elif event_type == "delivered":
            campaign.delivered_at = func.now()

        self.db.commit()
        self.db.refresh(event)
        return event

    def mark_invoice_paid(
        self, invoice_id: str, paid_amount: Optional[float] = None
    ) -> Optional[Campaign]:
        """
        Mark invoice as paid and update associated campaign metrics.

        Args:
            invoice_id: ID of paid invoice
            paid_amount: Amount paid (defaults to invoice amount)

        Returns:
            Campaign: Updated campaign or None if no campaign found
        """
        # Find campaigns for this invoice
        campaign = (
            self.db.query(Campaign)
            .filter(Campaign.invoice_id == invoice_id, Campaign.sent_at.isnot(None))
            .order_by(desc(Campaign.sent_at))
            .first()
        )

        if campaign:
            campaign.paid_after_send = True
            campaign.paid_amount = paid_amount
            self.db.commit()
            return campaign

        return None

    def get_experiment_results(self, experiment_id: str) -> Dict[str, dict]:
        """
        Calculate conversion metrics for each variant in an experiment.

        Args:
            experiment_id: ID of the experiment

        Returns:
            Dict mapping variant IDs to metrics:
            {
                "A": {
                    "campaigns_count": 100,
                    "total_sends": 100,
                    "opens": 45,
                    "open_rate": 0.45,
                    "clicks": 12,
                    "click_rate": 0.12,
                    "payments": 8,
                    "payment_rate": 0.08,
                    "revenue": 1200.00
                },
                "B": { ... }
            }
        """
        experiment = self.db.query(ABTest).filter(ABTest.id == experiment_id).first()
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        results = {}

        for variant_id, variant_config in experiment.variants.items():
            # Get all campaigns with this variant
            campaigns = (
                self.db.query(Campaign)
                .filter(
                    Campaign.ab_test_variant == variant_id,
                    Campaign.user_id == experiment.user_id,
                    Campaign.sent_at.isnot(None),
                )
                .all()
            )

            campaign_count = len(campaigns)

            # Aggregate metrics
            total_opens = sum(c.opened_count or 0 for c in campaigns)
            total_clicks = sum(1 for c in campaigns if c.clicked_at)
            total_payments = sum(1 for c in campaigns if c.paid_after_send)
            total_revenue = sum(
                c.paid_amount or 0 for c in campaigns if c.paid_after_send
            )

            # Calculate rates
            open_rate = total_opens / campaign_count if campaign_count > 0 else 0
            click_rate = total_clicks / campaign_count if campaign_count > 0 else 0
            payment_rate = total_payments / campaign_count if campaign_count > 0 else 0

            results[variant_id] = {
                "variant_config": variant_config,
                "campaigns_count": campaign_count,
                "total_sends": campaign_count,
                "opens": total_opens,
                "open_rate": round(open_rate, 4),
                "clicks": total_clicks,
                "click_rate": round(click_rate, 4),
                "payments": total_payments,
                "payment_rate": round(payment_rate, 4),
                "revenue": float(total_revenue) if total_revenue else 0.0,
            }

        return results

    def get_winning_variant(
        self,
        experiment_id: str,
        metric: str = "payment_rate",
        min_sample_size: int = 30,
        confidence_level: float = 0.95,
    ) -> Optional[Tuple[str, dict]]:
        """
        Determine the winning variant based on statistical analysis.

        Args:
            experiment_id: ID of the experiment
            metric: Metric to compare ('open_rate', 'click_rate', 'payment_rate', 'revenue')
            min_sample_size: Minimum sample size per variant for statistical significance
            confidence_level: Confidence level for statistical test

        Returns:
            Tuple of (variant_id, results) or None if no clear winner
        """
        results = self.get_experiment_results(experiment_id)

        # Filter variants with sufficient sample size
        valid_variants = {
            v: r for v, r in results.items() if r["campaigns_count"] >= min_sample_size
        }

        if len(valid_variants) < 2:
            return None  # Not enough data or only one variant

        # Find variant with highest metric
        best_variant = None
        best_value = -1

        for variant_id, metrics in valid_variants.items():
            value = metrics.get(metric, 0)
            if value > best_value:
                best_value = value
                best_variant = variant_id

        if best_variant:
            return (best_variant, results[best_variant])

        return None

    def complete_experiment(self, experiment_id: str) -> ABTest:
        """
        Mark an experiment as completed.

        Args:
            experiment_id: ID of the experiment

        Returns:
            ABTest: Updated experiment
        """
        experiment = self.db.query(ABTest).filter(ABTest.id == experiment_id).first()
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment.ended_at = func.now()
        experiment.is_active = False
        self.db.commit()
        return experiment


def assign_variant_to_campaign(
    campaign: Campaign, experiment_id: str, db: Session
) -> Optional[str]:
    """
    Assign an A/B test variant to a campaign.

    Args:
        campaign: Campaign object
        experiment_id: ID of the experiment to assign
        db: Database session

    Returns:
        Optional[str]: Assigned variant ID or None if assignment failed
    """
    manager = ExperimentManager(db)
    variant = manager.assign_variant(
        experiment_id=experiment_id, user_id=campaign.user_id, campaign_id=campaign.id
    )
    return variant


def track_email_open(
    campaign_id: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db: Optional[Session] = None,
) -> EmailEvent:
    """
    Track email open event via pixel tracking.

    Args:
        campaign_id: Campaign ID
        ip_address: IP address of the open
        user_agent: User agent string
        db: Database session (optional, will create new if None)

    Returns:
        EmailEvent: Created event record
    """
    if db is None:
        from ..core.database import SessionLocal

        db_session = SessionLocal()
        try:
            return track_email_open(campaign_id, ip_address, user_agent, db_session)
        finally:
            db_session.close()
    else:
        manager = ExperimentManager(db)
        return manager.track_event(
            campaign_id=campaign_id,
            event_type="opened",
            event_data={"tracking_type": "pixel"},
            ip_address=ip_address,
            user_agent=user_agent,
        )


def analyze_experiment(
    experiment_id: str, db: Optional[Session] = None
) -> Dict[str, dict]:
    """
    Analyze an experiment and return full results.

    Args:
        experiment_id: ID of the experiment
        db: Database session (optional)

    Returns:
        Dict with experiment details and variant metrics
    """
    if db is None:
        from ..core.database import SessionLocal

        db_session = SessionLocal()
        try:
            return analyze_experiment(experiment_id, db_session)
        finally:
            db_session.close()
    else:
        manager = ExperimentManager(db)
        return manager.get_experiment_results(experiment_id)
