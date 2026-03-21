"""
Invoice Management API module.

This module provides CRUD operations for invoices, including:
- Create invoice (manual import)
- List invoices with filters (status, due_date range)
- Get single invoice
- Update invoice status and metadata
- Soft delete (cancel) invoice
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr

from src.api.deps import get_db
from src.api.deps import get_current_active_user
from src.models import Invoice, User

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


# ========== Schemas ==========


class InvoiceCreate(BaseModel):
    """Schema for creating a new invoice."""

    invoice_number: Optional[str] = None
    client_name: str = Field(..., max_length=500)
    client_email: Optional[EmailStr] = None
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    due_date: datetime
    description: Optional[str] = None
    notes: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    stripe_invoice_id: Optional[str] = None
    paypal_txn_id: Optional[str] = None
    paypal_invoice_id: Optional[str] = None
    plaid_account_id: Optional[str] = None
    plaid_transaction_id: Optional[str] = None
    extra_data: Optional[dict] = None


class InvoiceUpdate(BaseModel):
    """Schema for updating invoice status and metadata."""

    status: Optional[str] = None  # draft, sent, paid, overdue, disputed, canceled
    paid_date: Optional[datetime] = None
    notes: Optional[str] = None
    description: Optional[str] = None
    client_name: Optional[str] = Field(None, max_length=500)
    client_email: Optional[EmailStr] = None
    due_date: Optional[datetime] = None


class InvoiceResponse(BaseModel):
    """Schema for invoice response."""

    id: str
    user_id: str
    invoice_number: Optional[str]
    client_name: str
    client_email: Optional[str]
    amount: float
    currency: str
    status: str
    due_date: datetime
    issue_date: datetime
    paid_date: Optional[datetime]
    stripe_payment_intent_id: Optional[str]
    stripe_invoice_id: Optional[str]
    paypal_txn_id: Optional[str]
    paypal_invoice_id: Optional[str]
    plaid_account_id: Optional[str]
    plaid_transaction_id: Optional[str]
    description: Optional[str]
    notes: Optional[str]
    extra_data: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== Utility Functions ==========


def validate_status_transition(current_status: str, new_status: str) -> bool:
    """Validate if a status transition is allowed."""
    # All transitions are allowed in MVP for flexibility
    # Could add business rules later (e.g., can't unmark paid)
    allowed_statuses = {"draft", "sent", "paid", "overdue", "disputed", "canceled"}
    if new_status not in allowed_statuses:
        return False
    return True


# ========== API Endpoints ==========


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new invoice.

    The invoice is automatically associated with the authenticated user.
    Freemium users are limited to a maximum number of active invoices.
    """
    # Create Invoice model instance
    invoice = Invoice(
        user_id=current_user.id,
        invoice_number=invoice_data.invoice_number,
        client_name=invoice_data.client_name,
        client_email=invoice_data.client_email,
        amount=invoice_data.amount,
        currency=invoice_data.currency,
        due_date=invoice_data.due_date,
        description=invoice_data.description,
        notes=invoice_data.notes,
        stripe_payment_intent_id=invoice_data.stripe_payment_intent_id,
        stripe_invoice_id=invoice_data.stripe_invoice_id,
        paypal_txn_id=invoice_data.paypal_txn_id,
        paypal_invoice_id=invoice_data.paypal_invoice_id,
        plaid_account_id=invoice_data.plaid_account_id,
        plaid_transaction_id=invoice_data.plaid_transaction_id,
        extra_data=invoice_data.extra_data,
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return invoice


@router.get("/", response_model=List[InvoiceResponse])
async def list_invoices(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by invoice status"),
    due_date_start: Optional[datetime] = Query(
        None, description="Filter invoices due after this date"
    ),
    due_date_end: Optional[datetime] = Query(
        None, description="Filter invoices due before this date"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
):
    """
    List invoices with optional filters.

    Regular users can only see their own invoices.
    Admin users can see all invoices.
    """
    query = db.query(Invoice)

    # Filter by user (unless admin)
    if not current_user.is_admin:
        query = query.filter(Invoice.user_id == current_user.id)
    # Admin users can optionally filter by user_id if needed
    # Could add user_id filter later

    # Apply status filter
    if status:
        query = query.filter(Invoice.status == status)

    # Apply due date range filters
    if due_date_start:
        query = query.filter(Invoice.due_date >= due_date_start)
    if due_date_end:
        query = query.filter(Invoice.due_date <= due_date_end)

    # Order by created_at descending (newest first)
    query = query.order_by(Invoice.created_at.desc())

    # Apply pagination
    invoices = query.offset(skip).limit(limit).all()

    return invoices


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a single invoice by ID.

    Users can only access their own invoices unless they are admins.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )

    # Check ownership (unless admin)
    if not current_user.is_admin and invoice.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this invoice",
        )

    return invoice


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    update_data: InvoiceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update invoice status and metadata.

    Allowed operations:
    - Change status (to paid, overdue, disputed, canceled, etc.)
    - Update notes, description, client info
    - Record payment date when marking as paid
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )

    # Check ownership (unless admin)
    if not current_user.is_admin and invoice.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this invoice",
        )

    # Update fields if provided
    if update_data.status is not None:
        # Validate status value
        if not validate_status_transition(invoice.status, update_data.status):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {update_data.status}",
            )
        invoice.status = update_data.status

        # Auto-set paid_date when marking as paid
        if update_data.status == "paid" and update_data.paid_date is None:
            invoice.paid_date = datetime.utcnow()
        # If status changed away from paid, we keep paid_date as historical record

    if update_data.paid_date is not None:
        invoice.paid_date = update_data.paid_date

    if update_data.notes is not None:
        invoice.notes = update_data.notes

    if update_data.description is not None:
        invoice.description = update_data.description

    if update_data.client_name is not None:
        invoice.client_name = update_data.client_name

    if update_data.client_email is not None:
        invoice.client_email = update_data.client_email

    if update_data.due_date is not None:
        invoice.due_date = update_data.due_date

    db.commit()
    db.refresh(invoice)

    return invoice


@router.delete("/{invoice_id}", response_model=InvoiceResponse)
async def soft_delete_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Soft delete an invoice by setting its status to 'canceled'.

    Invoices that are already 'paid' cannot be canceled.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )

    # Check ownership (unless admin)
    if not current_user.is_admin and invoice.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this invoice",
        )

    # Can't cancel a paid invoice (payment already received)
    if invoice.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel an already paid invoice",
        )

    # If already canceled, just return
    if invoice.status == "canceled":
        return invoice

    # Set status to canceled (soft delete)
    invoice.status = "canceled"
    db.commit()
    db.refresh(invoice)

    return invoice
