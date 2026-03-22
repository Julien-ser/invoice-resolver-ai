"""
Admin panel API routes.

Provides administrative controls for user management,
system monitoring, and application oversight.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, text
from pydantic import BaseModel

from src.api.deps import get_current_admin_user, get_db
from src.models import (
    User,
    PaymentConnection,
    WebhookEvent,
    SystemMetric,
    Invoice,
    Template,
    Campaign,
)
from src.core.config import settings
from .schemas import (
    UserSummary,
    UserDetail,
    UserTierUpdate,
    DashboardStats,
    SystemHealth,
    PaymentConnectionInfo,
    WebhookEventInfo,
)

router = APIRouter(
    prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin_user)]
)


@router.get("/", response_model=DashboardStats)
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """
    Get admin dashboard overview with key statistics.
    """
    # User stats
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = (
        db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    )
    inactive_users = total_users - active_users

    # Tier distribution
    tier_counts = (
        db.query(User.subscription_tier, func.count(User.id))
        .group_by(User.subscription_tier)
        .all()
    )
    tier_distribution = {tier: count for tier, count in tier_counts}

    # Invoice stats
    total_invoices = db.query(func.count(Invoice.id)).scalar() or 0
    invoices_by_status = (
        db.query(Invoice.status, func.count(Invoice.id)).group_by(Invoice.status).all()
    )
    invoice_status_dict = {
        status or "unknown": count for status, count in invoices_by_status
    }

    # Payment connection stats
    total_connections = db.query(func.count(PaymentConnection.id)).scalar() or 0
    active_connections = (
        db.query(PaymentConnection.provider, func.count(PaymentConnection.id))
        .filter(PaymentConnection.is_active == True)
        .group_by(PaymentConnection.provider)
        .all()
    )
    connections_by_provider = {
        provider: count for provider, count in active_connections
    }

    # Recent webhook events (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_webhook_count = (
        db.query(func.count(WebhookEvent.id))
        .filter(WebhookEvent.created_at >= yesterday)
        .scalar()
        or 0
    )

    # System health basic info
    system_health = {
        "uptime": "unknown",  # Would need process start time tracking
        "database_status": "connected",
        "redis_status": "unknown",  # Could check via Celery
        "last_metric_update": None,
    }

    # Get latest system metric timestamp
    latest_metric = (
        db.query(SystemMetric.recorded_at)
        .order_by(desc(SystemMetric.recorded_at))
        .first()
    )
    if latest_metric:
        system_health["last_metric_update"] = latest_metric[0].isoformat()

    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        inactive_users=inactive_users,
        tier_distribution=tier_distribution,
        total_invoices=total_invoices,
        invoices_by_status=invoice_status_dict,
        total_payment_connections=total_connections,
        connections_by_provider=connections_by_provider,
        recent_webhook_count=recent_webhook_count,
        system_health=system_health,
    )


@router.get("/users", response_model=List[UserSummary])
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    tier: Optional[str] = Query(None, description="Filter by subscription tier"),
    status: Optional[str] = Query(None, description="Filter by active/inactive"),
    search: Optional[str] = Query(None, description="Search by email or name"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
):
    """
    List all users with optional filters and pagination.
    """
    query = db.query(User)

    # Apply filters
    if tier:
        query = query.filter(User.subscription_tier == tier)
    if status:
        is_active = status.lower() == "active"
        query = query.filter(User.is_active == is_active)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_pattern)) | (User.full_name.ilike(search_pattern))
        )

    # Apply sorting
    sort_column = getattr(User, sort_by, User.created_at)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # Apply pagination
    offset = (page - 1) * limit
    users = query.offset(offset).limit(limit).all()

    return users


@router.get("/users/{user_id}", response_model=UserDetail)
async def get_user_detail(user_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Count related entities
    payment_connections_count = (
        db.query(func.count(PaymentConnection.id))
        .filter(PaymentConnection.user_id == user_id)
        .scalar()
        or 0
    )
    invoices_count = (
        db.query(func.count(Invoice.id)).filter(Invoice.user_id == user_id).scalar()
        or 0
    )
    templates_count = (
        db.query(func.count(Template.id)).filter(Template.user_id == user_id).scalar()
        or 0
    )
    campaigns_count = (
        db.query(func.count(Campaign.id)).filter(Campaign.user_id == user_id).scalar()
        or 0
    )

    return UserDetail(
        **user.__dict__,
        payment_connections_count=payment_connections_count,
        invoices_count=invoices_count,
        templates_count=templates_count,
        campaigns_count=campaigns_count,
    )


@router.post("/users/{user_id}/tier")
async def update_user_tier(
    user_id: str,
    tier_update: UserTierUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a user's subscription tier and optionally invoice limit.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Validate tier value
    valid_tiers = ["free", "pro", "enterprise"]
    if tier_update.subscription_tier not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid subscription tier. Must be one of: {', '.join(valid_tiers)}",
        )

    old_tier = user.subscription_tier
    user.subscription_tier = tier_update.subscription_tier

    if tier_update.invoice_limit is not None:
        if tier_update.invoice_limit < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice limit cannot be negative",
            )
        user.invoice_limit = tier_update.invoice_limit
    else:
        # Set default limits based on tier
        default_limits = {"free": 5, "pro": 999, "enterprise": 999}
        user.invoice_limit = default_limits.get(tier_update.subscription_tier, 5)

    try:
        db.commit()
        db.refresh(user)
        return {
            "message": "User tier updated successfully",
            "user_id": user_id,
            "old_tier": old_tier,
            "new_tier": user.subscription_tier,
            "invoice_limit": user.invoice_limit,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}",
        )


@router.get("/metrics", response_model=SystemHealth)
async def get_system_metrics(
    hours: int = Query(24, ge=1, le=168, description="Lookback period in hours"),
    db: Session = Depends(get_db),
):
    """
    Get system health metrics including Celery workers, errors, and performance.
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    # Count Celery tasks by state (from SystemMetric with labels containing task info)
    # This is a simplified approach - could be enhanced with actual worker monitoring
    celery_metrics = (
        db.query(SystemMetric)
        .filter(
            SystemMetric.metric_name.like("celery_%"),
            SystemMetric.recorded_at >= cutoff_time,
        )
        .all()
    )

    # For now, provide basic structure
    celery_workers = {
        "active": len(celery_metrics),
        "total": settings.worker_count if hasattr(settings, "worker_count") else 1,
        "details": [
            {"name": "worker-1", "status": "unknown", "last_heartbeat": None}
        ],  # TODO: Implement actual worker monitoring
    }

    # Get recent errors from SystemMetric with high error counts or failures
    recent_errors = []
    error_metric_names = ["task_failed", "webhook_failed", "sync_error"]
    for metric_name in error_metric_names:
        errors = (
            db.query(SystemMetric)
            .filter(
                SystemMetric.metric_name == metric_name,
                SystemMetric.recorded_at >= cutoff_time,
            )
            .order_by(desc(SystemMetric.recorded_at))
            .limit(10)
            .all()
        )
        for error in errors:
            recent_errors.append(
                {
                    "metric": metric_name,
                    "value": float(error.metric_value),
                    "labels": error.labels or {},
                    "recorded_at": error.recorded_at.isoformat(),
                }
            )

    # Get API latency from SystemMetric if tracked
    latency_metric = (
        db.query(SystemMetric)
        .filter(
            SystemMetric.metric_name == "api_latency_p95",
            SystemMetric.recorded_at >= cutoff_time,
        )
        .order_by(desc(SystemMetric.recorded_at))
        .first()
    )
    api_latency_p95 = float(latency_metric.metric_value) if latency_metric else None

    # Last sync status from invoice sync tasks
    last_sync = (
        db.query(SystemMetric)
        .filter(SystemMetric.metric_name == "invoice_sync_completed")
        .order_by(desc(SystemMetric.recorded_at))
        .first()
    )
    last_sync_status = None
    if last_sync:
        last_sync_status = {
            "completed_at": last_sync.recorded_at.isoformat(),
            "metrics": last_sync.labels or {},
        }

    # Calculate uptime (would need application start time)
    uptime_days = hours / 24.0  # Simplified

    return SystemHealth(
        celery_workers=celery_workers,
        recent_errors=recent_errors,
        api_latency_p95=api_latency_p95,
        last_sync_status=last_sync_status,
        uptime_days=uptime_days,
    )


@router.get("/webhooks", response_model=List[WebhookEventInfo])
async def list_webhook_events(
    limit: int = Query(50, ge=1, le=200, description="Number of events to return"),
    status: Optional[str] = Query(None, description="Filter by processing status"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    hours: int = Query(24, ge=1, le=720, description="Lookback period in hours"),
    db: Session = Depends(get_db),
):
    """
    List recent webhook events with optional filters.
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    query = db.query(WebhookEvent).filter(WebhookEvent.created_at >= cutoff_time)

    if status:
        query = query.filter(WebhookEvent.processing_status == status)
    if provider:
        query = query.filter(WebhookEvent.provider == provider)

    events = query.order_by(desc(WebhookEvent.created_at)).limit(limit).all()
    return events


@router.get("/connections", response_model=List[PaymentConnectionInfo])
async def list_payment_connections(
    active_only: bool = Query(True, description="Show only active connections"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    db: Session = Depends(get_db),
):
    """
    List all payment provider connections with user information.
    """
    query = (
        db.query(PaymentConnection)
        .join(User, PaymentConnection.user_id == User.id)
        .add_columns(
            User.email.label("user_email"),
            User.full_name.label("user_full_name"),
        )
    )

    if active_only:
        query = query.filter(PaymentConnection.is_active == True)

    if provider:
        query = query.filter(PaymentConnection.provider == provider)

    connections = query.order_by(desc(PaymentConnection.created_at)).all()

    result = []
    for conn, user_email in connections:
        result.append(
            PaymentConnectionInfo(
                id=conn.id,
                user_email=user_email,
                provider=conn.provider,
                connection_name=conn.connection_name,
                is_active=conn.is_active,
                last_sync_at=conn.last_sync_at,
                created_at=conn.created_at,
            )
        )

    return result
