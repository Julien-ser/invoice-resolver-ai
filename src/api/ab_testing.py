"""
A/B Testing API module.

This module provides REST API endpoints for managing A/B test experiments:
- Create, read, update, delete experiments
- Assign variants to campaigns
- View experiment results and analytics
- Track email opens via pixel tracking
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import uuid

from src.api.deps import get_db, get_current_active_user, get_current_admin_user
from src.models import User, ABTest, Campaign, EmailEvent
from src.ab_testing.experiment import (
    ExperimentManager,
    assign_variant_to_campaign,
    track_email_open,
    analyze_experiment,
)
from src.core.config import settings


router = APIRouter(prefix="/api/ab-tests", tags=["ab-testing"])


# ========== Schemas ==========


class VariantCreate(BaseModel):
    """Schema for a single variant in an experiment."""

    variant_id: str = Field(
        ..., description="Unique variant identifier (e.g., 'A', 'B')"
    )
    template_id: Optional[str] = Field(None, description="Template ID for this variant")
    description: Optional[str] = Field(None, description="Variant description")
    metadata: Optional[dict] = Field(
        default_factory=dict, description="Additional variant config"
    )


class ExperimentCreate(BaseModel):
    """Schema for creating a new A/B test experiment."""

    name: str = Field(..., max_length=255, description="Experiment name")
    description: Optional[str] = Field(None, description="Experiment description")
    test_type: str = Field(
        ..., description="Type of test: 'template', 'timing', 'subject_line'"
    )
    variants: Dict[str, VariantCreate] = Field(
        ..., description="Dictionary of variant configurations"
    )
    metadata: Optional[dict] = Field(
        default_factory=dict,
        description="Experiment metadata (e.g., target_sample_size)",
    )


class ExperimentResponse(BaseModel):
    """Schema for experiment response."""

    id: str
    user_id: str
    name: str
    description: Optional[str]
    test_type: str
    variants: dict
    experiment_metadata: dict
    is_active: bool
    started_at: datetime
    ended_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExperimentUpdate(BaseModel):
    """Schema for updating an experiment."""

    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    variants: Optional[dict] = None
    experiment_metadata: Optional[dict] = None


class ExperimentResultsResponse(BaseModel):
    """Schema for experiment results."""

    experiment_id: str
    experiment_name: str
    test_type: str
    is_active: bool
    variants: Dict[str, Dict[str, Any]]
    winning_variant: Optional[Dict[str, Any]] = None
    analysis_date: datetime


class CampaignVariantAssign(BaseModel):
    """Schema for manually assigning a variant to a campaign."""

    variant_id: str = Field(..., description="Variant ID to assign")
    experiment_id: Optional[str] = Field(
        None, description="Optional experiment ID (if not provided, auto-detects)"
    )


# ========== Utility Functions ==========


def validate_test_type(test_type: str) -> bool:
    """Validate test type is allowed."""
    allowed_types = {"template", "timing", "subject_line"}
    return test_type in allowed_types


# ========== API Endpoints ==========


@router.post(
    "/", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED
)
async def create_experiment(
    experiment_data: ExperimentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new A/B test experiment.

    The experiment will be associated with the authenticated user.
    Variants should be defined with unique IDs (e.g., 'A', 'B', 'control').
    """
    if not validate_test_type(experiment_data.test_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid test_type. Must be one of: template, timing, subject_line",
        )

    # Convert variants to the format expected by the model
    variants_dict = {}
    for variant_id, variant in experiment_data.variants.items():
        variants_dict[variant_id] = {
            "template_id": variant.template_id,
            "description": variant.description,
            **(variant.metadata or {}),
        }

    manager = ExperimentManager(db)
    experiment = manager.create_experiment(
        user_id=current_user.id,
        name=experiment_data.name,
        test_type=experiment_data.test_type,
        variants=variants_dict,
        description=experiment_data.description,
        metadata=experiment_data.metadata,
    )

    return experiment


@router.get("/", response_model=List[ExperimentResponse])
async def list_experiments(
    include_inactive: bool = Query(False, description="Include inactive experiments"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List all A/B test experiments for the current user.

    By default, only returns active experiments. Set include_inactive=true to see all.
    """
    query = db.query(ABTest).filter(ABTest.user_id == current_user.id)

    if not include_inactive:
        query = query.filter(ABTest.is_active == True)

    query = query.order_by(ABTest.created_at.desc())
    experiments = query.all()

    return experiments


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get details of a specific A/B test experiment.

    Users can only access their own experiments unless they are admins.
    """
    experiment = db.query(ABTest).filter(ABTest.id == experiment_id).first()

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    # Check access (owner or admin)
    if experiment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this experiment",
        )

    return experiment


@router.patch("/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(
    experiment_id: str,
    update_data: ExperimentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update an A/B test experiment.

    Allows updating name, description, is_active status, variants, and metadata.
    """
    experiment = db.query(ABTest).filter(ABTest.id == experiment_id).first()

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    # Check ownership (owner or admin)
    if experiment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this experiment",
        )

    # Update fields if provided
    if update_data.name is not None:
        experiment.name = update_data.name

    if update_data.description is not None:
        experiment.description = update_data.description

    if update_data.is_active is not None:
        experiment.is_active = update_data.is_active

    if update_data.variants is not None:
        experiment.variants = update_data.variants

    if update_data.experiment_metadata is not None:
        experiment.experiment_metadata = update_data.experiment_metadata

    db.commit()
    db.refresh(experiment)

    return experiment


@router.post("/{experiment_id}/complete", response_model=ExperimentResponse)
async def complete_experiment(
    experiment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Mark an A/B test experiment as completed.

    This will set ended_at and deactivate the experiment.
    The experiment's results can still be viewed after completion.
    """
    experiment = db.query(ABTest).filter(ABTest.id == experiment_id).first()

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    # Check ownership (owner or admin)
    if experiment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this experiment",
        )

    manager = ExperimentManager(db)
    experiment = manager.complete_experiment(experiment_id)

    return experiment


@router.get("/{experiment_id}/results", response_model=ExperimentResultsResponse)
async def get_experiment_results(
    experiment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed results and analytics for an A/B test experiment.

    Returns metrics for each variant including:
    - Number of campaigns (sample size)
    - Open rate, click rate, payment rate
    - Total revenue
    """
    experiment = db.query(ABTest).filter(ABTest.id == experiment_id).first()

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    # Check access (owner or admin)
    if experiment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this experiment's results",
        )

    manager = ExperimentManager(db)
    results = manager.get_experiment_results(experiment_id)

    # Check if there's a winning variant
    winning = None
    if experiment.is_active:
        winning = manager.get_winning_variant(
            experiment_id=experiment_id,
            metric="payment_rate",
            min_sample_size=30,
            confidence_level=0.95,
        )

    return ExperimentResultsResponse(
        experiment_id=experiment.id,
        experiment_name=experiment.name,
        test_type=experiment.test_type,
        is_active=experiment.is_active,
        variants=results,
        winning_variant=winning,
        analysis_date=datetime.utcnow(),
    )


@router.get("/{experiment_id}/winning-variant")
async def get_winning_variant(
    experiment_id: str,
    metric: str = Query(
        "payment_rate",
        description="Metric to use for comparison: open_rate, click_rate, payment_rate, revenue",
    ),
    min_sample_size: int = Query(
        30, ge=10, description="Minimum campaigns per variant to consider"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get the winning variant for an experiment based on statistical analysis.

    Args:
        metric: The metric to compare (default: payment_rate)
        min_sample_size: Minimum sample size per variant (default: 30)

    Returns:
        Dict with variant_id and metrics, or null if no clear winner yet.
    """
    experiment = db.query(ABTest).filter(ABTest.id == experiment_id).first()

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    # Check access (owner or admin)
    if experiment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this experiment's results",
        )

    manager = ExperimentManager(db)
    winning = manager.get_winning_variant(
        experiment_id=experiment_id,
        metric=metric,
        min_sample_size=min_sample_size,
        confidence_level=0.95,
    )

    if winning:
        variant_id, metrics = winning
        return {
            "variant_id": variant_id,
            "metric": metric,
            "metrics": metrics,
            "message": f"Variant {variant_id} is winning with {metric} of {metrics.get(metric, 0):.2%}",
        }
    else:
        return {
            "variant_id": None,
            "metric": metric,
            "message": f"No clear winner yet. Need at least {min_sample_size} campaigns per variant with sufficient data.",
        }


@router.post("/campaigns/{campaign_id}/assign-variant")
async def assign_campaign_variant(
    campaign_id: str,
    assignment: CampaignVariantAssign,
    experiment_id: Optional[str] = Query(
        None, description="Optional: experiment ID (auto-detected if not provided)"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Manually assign an A/B test variant to a campaign.

    If experiment_id is not provided, will look for active experiments of 'template' type
    for the user and assign a variant from that experiment.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    # Check ownership
    if campaign.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this campaign",
        )

    # If experiment_id not provided, find an active template experiment for this user
    if experiment_id is None:
        active_experiment = (
            db.query(ABTest)
            .filter(
                ABTest.user_id == current_user.id,
                ABTest.is_active == True,
                ABTest.test_type == "template",
            )
            .order_by(ABTest.created_at.desc())
            .first()
        )

        if active_experiment:
            experiment_id = active_experiment.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active experiment found. Please provide experiment_id parameter.",
            )

    manager = ExperimentManager(db)
    variant = manager.assign_variant(
        experiment_id=experiment_id,
        user_id=campaign.user_id,
        campaign_id=campaign.id,
    )

    # Update campaign with assigned variant
    campaign.ab_test_variant = variant
    db.commit()

    return {
        "campaign_id": campaign_id,
        "experiment_id": experiment_id,
        "assigned_variant": variant,
        "message": f"Variant {variant} assigned to campaign {campaign_id}",
    }


# ========== Tracking Endpoints ==========


@router.get("/track/open/{campaign_id}", include_in_schema=True)
async def track_email_open_pixel(
    campaign_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Pixel tracking endpoint for email opens.

    This endpoint is called by email clients when they load images.
    It tracks the open event and returns a 1x1 transparent GIF pixel.

    Query params:
    - uid: User identifier (optional, for unique open tracking)
    - t: Timestamp (optional)
    """
    try:
        # Get client IP and user agent
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")

        # Track the open event
        manager = ExperimentManager(db)
        event = manager.track_event(
            campaign_id=campaign_id,
            event_type="opened",
            event_data={
                "tracking_type": "pixel",
                "user_agent": user_agent,
                "query_params": dict(request.query_params),
            },
            ip_address=client_ip,
            user_agent=user_agent,
        )

        # Return a 1x1 transparent GIF pixel
        # GIF89a 1x1 transparent pixel
        pixel_bytes = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02L\x01\x00;"

        from fastapi.responses import Response

        return Response(
            content=pixel_bytes,
            media_type="image/gif",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Content-Disposition": "inline; filename=pixel.gif",
            },
        )

    except ValueError as e:
        # Campaign not found or other validation error
        # Still return pixel to avoid breaking email display
        from fastapi.responses import Response

        return Response(
            content=b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02L\x01\x00;",
            media_type="image/gif",
        )


# Admin-only endpoint for system-wide experiment overview
@router.get("/admin/overview")
async def get_admin_experiment_overview(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    [ADMIN ONLY] Get overview of all experiments across all users.

    Returns aggregate statistics for all active experiments.
    """
    # Get all active experiments
    active_experiments = db.query(ABTest).filter(ABTest.is_active == True).all()

    overview = {
        "total_experiments": len(active_experiments),
        "by_type": {},
        "by_user": {},
        "experiments": [],
    }

    for exp in active_experiments:
        # Count by type
        if exp.test_type not in overview["by_type"]:
            overview["by_type"][exp.test_type] = 0
        overview["by_type"][exp.test_type] += 1

        # Count by user
        user_id = exp.user_id
        if user_id not in overview["by_user"]:
            overview["by_user"][user_id] = 0
        overview["by_user"][user_id] += 1

        # Get results for this experiment
        manager = ExperimentManager(db)
        results = manager.get_experiment_results(exp.id)

        overview["experiments"].append(
            {
                "id": exp.id,
                "user_id": exp.user_id,
                "name": exp.name,
                "test_type": exp.test_type,
                "started_at": exp.started_at,
                "variants_count": len(exp.variants),
                "results_summary": results,
            }
        )

    return overview
