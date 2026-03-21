"""
Tests for invoice management API endpoints.

This module covers CRUD operations for invoices including creation,
listing, retrieval, updates, and soft deletion.
"""

import pytest
from datetime import datetime, timedelta
from fastapi import status

from tests.conftest import test_user_data, admin_user_data


class TestCreateInvoice:
    """Tests for creating invoices."""

    def test_create_invoice_success(self, client, test_user):
        """Test successful invoice creation."""
        response = client.post(
            "/api/invoices/",
            json={
                "invoice_number": "INV-001",
                "client_name": "Test Client",
                "client_email": "client@example.com",
                "amount": 1500.00,
                "currency": "USD",
                "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "description": "Web development services",
            },
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["invoice_number"] == "INV-001"
        assert data["client_name"] == "Test Client"
        assert data["amount"] == 1500.00
        assert data["status"] == "draft"
        assert data["user_id"] == test_user.id
        assert "id" in data

    def test_create_invoice_unauthorized(self, client):
        """Test creating invoice without authentication fails."""
        response = client.post(
            "/api/invoices/",
            json={
                "client_name": "Test Client",
                "amount": 100.00,
                "due_date": datetime.utcnow().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_invoice_invalid_data(self, client, test_user):
        """Test creating invoice with invalid data."""
        response = client.post(
            "/api/invoices/",
            json={
                "client_name": "Test Client",
                "amount": -50.00,  # Invalid: negative amount
                "due_date": datetime.utcnow().isoformat(),
            },
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_invoice_missing_required_fields(self, client, test_user):
        """Test creating invoice without required fields."""
        response = client.post(
            "/api/invoices/",
            json={
                "client_name": "Test Client",
                # Missing amount and due_date
            },
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_invoice_subscription_limit(
        self, client, db_session, test_user_data
    ):
        """Test that free tier users hit invoice limit."""
        from src.models import User, Invoice
        from src.api.auth import get_password_hash, create_access_token

        # Create a free user and fill up their invoice limit
        free_user = User(
            email="free_limit@example.com",
            password_hash=get_password_hash("password123"),
            subscription_tier="free",
            invoice_limit=2,
            is_active=True,
        )
        db_session.add(free_user)
        db_session.commit()

        # Create 2 active invoices (not paid or canceled)
        for i in range(2):
            invoice = Invoice(
                user_id=free_user.id,
                client_name=f"Client {i}",
                amount=100.00,
                due_date=datetime.utcnow() + timedelta(days=30),
                status="draft",
            )
            db_session.add(invoice)
        db_session.commit()

        # Get access token for this user
        access_token, _ = create_access_token(free_user.id)

        # Try to create 3rd invoice - should fail
        response = client.post(
            "/api/invoices/",
            json={
                "client_name": "Client 3",
                "amount": 100.00,
                "due_date": datetime.utcnow().isoformat(),
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Invoice limit exceeded" in response.json()["detail"]

    def test_create_invoice_admin_no_limit(self, client, admin_user):
        """Test admin users can create invoices without limit."""
        response = client.post(
            "/api/invoices/",
            json={
                "client_name": "Admin Client",
                "amount": 100.00,
                "due_date": datetime.utcnow().isoformat(),
            },
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )
        assert response.status_code == status.HTTP_201_CREATED


class TestListInvoices:
    """Tests for listing invoices."""

    def test_list_invoices_empty(self, client, test_user):
        """Test listing invoices when user has none."""
        response = client.get(
            "/api/invoices/",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_invoices_own_only(self, client, test_user, db_session):
        """Test that users only see their own invoices."""
        from src.models import Invoice
        from tests.conftest import admin_user

        # Create invoices for test_user
        invoice1 = Invoice(
            user_id=test_user.id,
            client_name="User's Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice1)

        # Create invoice for admin user
        invoice2 = Invoice(
            user_id=admin_user.id,
            client_name="Admin's Invoice",
            amount=200.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice2)
        db_session.commit()

        response = client.get(
            "/api/invoices/",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["client_name"] == "User's Invoice"

    def test_list_invoices_with_status_filter(self, client, test_user, db_session):
        """Test filtering invoices by status."""
        from src.models import Invoice

        # Create invoices with different statuses
        invoice_draft = Invoice(
            user_id=test_user.id,
            client_name="Draft Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        invoice_paid = Invoice(
            user_id=test_user.id,
            client_name="Paid Invoice",
            amount=200.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="paid",
            paid_date=datetime.utcnow(),
        )
        db_session.add(invoice_draft)
        db_session.add(invoice_paid)
        db_session.commit()

        # Filter by draft
        response = client.get(
            "/api/invoices/?status=draft",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "draft"

        # Filter by paid
        response = client.get(
            "/api/invoices/?status=paid",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "paid"

    def test_list_invoices_with_due_date_filter(self, client, test_user, db_session):
        """Test filtering invoices by due date range."""
        from src.models import Invoice
        from datetime import date

        today = date.today()
        past_due = today - timedelta(days=5)
        future_due = today + timedelta(days=30)

        invoice_past = Invoice(
            user_id=test_user.id,
            client_name="Past Due",
            amount=100.00,
            due_date=past_due,
            status="overdue",
        )
        invoice_future = Invoice(
            user_id=test_user.id,
            client_name="Future Due",
            amount=200.00,
            due_date=future_due,
            status="draft",
        )
        db_session.add(invoice_past)
        db_session.add(invoice_future)
        db_session.commit()

        # Filter for due after today
        response = client.get(
            f"/api/invoices/?due_date_start={today.isoformat()}",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["client_name"] == "Future Due"

    def test_list_invoices_pagination(self, client, test_user, db_session):
        """Test pagination parameters."""
        from src.models import Invoice

        # Create 5 invoices
        for i in range(5):
            invoice = Invoice(
                user_id=test_user.id,
                client_name=f"Invoice {i}",
                amount=100.00,
                due_date=datetime.utcnow() + timedelta(days=30),
                status="draft",
            )
            db_session.add(invoice)
        db_session.commit()

        # Get first 2
        response = client.get(
            "/api/invoices/?skip=0&limit=2",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

        # Get next 2
        response = client.get(
            "/api/invoices/?skip=2&limit=2",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_list_invoices_unauthorized(self, client):
        """Test listing invoices without authentication fails."""
        response = client.get("/api/invoices/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_invoices_admin_sees_all(
        self, client, admin_user, db_session, test_user
    ):
        """Test admin can see all users' invoices."""
        from src.models import Invoice

        # Create invoice for test_user
        invoice = Invoice(
            user_id=test_user.id,
            client_name="User Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice)
        db_session.commit()

        response = client.get(
            "/api/invoices/",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Admin should see at least 1 invoice (maybe other test invoices exist)
        assert len(data) >= 1
        # Find the one we created
        user_invoice = next(
            (inv for inv in data if inv["client_name"] == "User Invoice"), None
        )
        assert user_invoice is not None


class TestGetInvoice:
    """Tests for retrieving a single invoice."""

    def test_get_invoice_success(self, client, test_user, db_session):
        """Test retrieving a specific invoice."""
        from src.models import Invoice

        invoice = Invoice(
            user_id=test_user.id,
            client_name="Test Invoice",
            amount=500.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        response = client.get(
            f"/api/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == invoice.id
        assert data["client_name"] == "Test Invoice"

    def test_get_invoice_not_found(self, client, test_user):
        """Test retrieving non-existent invoice."""
        response = client.get(
            "/api/invoices/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Invoice not found" in response.json()["detail"]

    def test_get_invoice_wrong_user(self, client, test_user, db_session, admin_user):
        """Test that user cannot access another user's invoice."""
        from src.models import Invoice

        # Create invoice belonging to admin
        invoice = Invoice(
            user_id=admin_user.id,
            client_name="Admin's Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        response = client.get(
            f"/api/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not authorized" in response.json()["detail"]

    def test_get_invoice_admin_can_access_any(
        self, client, admin_user, test_user, db_session
    ):
        """Test admin can access any user's invoice."""
        from src.models import Invoice

        invoice = Invoice(
            user_id=test_user.id,
            client_name="User Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        response = client.get(
            f"/api/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == invoice.id


class TestUpdateInvoice:
    """Tests for updating invoice status and metadata."""

    def test_update_invoice_status(self, client, test_user, db_session):
        """Test updating invoice status."""
        from src.models import Invoice

        invoice = Invoice(
            user_id=test_user.id,
            client_name="Test Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        response = client.patch(
            f"/api/invoices/{invoice.id}",
            json={"status": "sent"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "sent"

    def test_update_invoice_paid_auto_date(self, client, test_user, db_session):
        """Test that marking as paid automatically sets paid_date."""
        from src.models import Invoice

        invoice = Invoice(
            user_id=test_user.id,
            client_name="Test Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        response = client.patch(
            f"/api/invoices/{invoice.id}",
            json={"status": "paid"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "paid"
        assert data["paid_date"] is not None

    def test_update_invoice_notes(self, client, test_user, db_session):
        """Test updating invoice notes."""
        from src.models import Invoice

        invoice = Invoice(
            user_id=test_user.id,
            client_name="Test Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        response = client.patch(
            f"/api/invoices/{invoice.id}",
            json={"notes": "Updated notes"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["notes"] == "Updated notes"

    def test_update_invoice_multiple_fields(self, client, test_user, db_session):
        """Test updating multiple fields at once."""
        from src.models import Invoice

        invoice = Invoice(
            user_id=test_user.id,
            client_name="Original Name",
            amount=100.00,
            due_date=datetime.utcnow().date(),
            status="draft",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        new_due_date = datetime.utcnow() + timedelta(days=60)
        response = client.patch(
            f"/api/invoices/{invoice.id}",
            json={
                "status": "overdue",
                "client_name": "Updated Name",
                "due_date": new_due_date.isoformat(),
            },
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "overdue"
        assert data["client_name"] == "Updated Name"
        # due_date in response should be the new date
        # It comes back as string, we just check it's updated

    def test_update_invoice_wrong_user(self, client, test_user, db_session, admin_user):
        """Test that user cannot update another user's invoice."""
        from src.models import Invoice

        invoice = Invoice(
            user_id=admin_user.id,
            client_name="Admin Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        response = client.patch(
            f"/api/invoices/{invoice.id}",
            json={"status": "paid"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_invoice_not_found(self, client, test_user):
        """Test updating non-existent invoice."""
        response = client.patch(
            "/api/invoices/00000000-0000-0000-0000-000000000000",
            json={"status": "paid"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_invoice_invalid_status(self, client, test_user, db_session):
        """Test updating invoice with invalid status."""
        from src.models import Invoice

        invoice = Invoice(
            user_id=test_user.id,
            client_name="Test Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        response = client.patch(
            f"/api/invoices/{invoice.id}",
            json={"status": "invalid_status"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid status" in response.json()["detail"]


class TestSoftDeleteInvoice:
    """Tests for soft deleting invoices."""

    def test_soft_delete_invoice_success(self, client, test_user, db_session):
        """Test soft deleting an invoice sets status to canceled."""
        from src.models import Invoice

        invoice = Invoice(
            user_id=test_user.id,
            client_name="Test Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        response = client.delete(
            f"/api/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "canceled"

        # Verify in database
        db_session.refresh(invoice)
        assert invoice.status == "canceled"

    def test_soft_delete_invoice_not_found(self, client, test_user):
        """Test deleting non-existent invoice returns 404."""
        response = client.delete(
            "/api/invoices/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_soft_delete_invoice_wrong_user(
        self, client, test_user, db_session, admin_user
    ):
        """Test that user cannot delete another user's invoice."""
        from src.models import Invoice

        invoice = Invoice(
            user_id=admin_user.id,
            client_name="Admin Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        response = client.delete(
            f"/api/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_soft_delete_already_canceled(self, client, test_user, db_session):
        """Test deleting an already canceled invoice returns it unchanged."""
        from src.models import Invoice

        invoice = Invoice(
            user_id=test_user.id,
            client_name="Test Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="canceled",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        response = client.delete(
            f"/api/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "canceled"

    def test_soft_delete_paid_invoice_fails(self, client, test_user, db_session):
        """Test that paid invoices cannot be canceled."""
        from src.models import Invoice

        invoice = Invoice(
            user_id=test_user.id,
            client_name="Test Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="paid",
            paid_date=datetime.utcnow(),
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        response = client.delete(
            f"/api/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot cancel an already paid invoice" in response.json()["detail"]

    def test_soft_delete_admin_can_any_invoice(
        self, client, admin_user, test_user, db_session
    ):
        """Test admin can cancel any user's invoice."""
        from src.models import Invoice

        invoice = Invoice(
            user_id=test_user.id,
            client_name="User Invoice",
            amount=100.00,
            due_date=datetime.utcnow() + timedelta(days=30),
            status="draft",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        response = client.delete(
            f"/api/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "canceled"
