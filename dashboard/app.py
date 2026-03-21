"""
Invoice Resolver AI - Streamlit Dashboard

This dashboard provides user interface for managing invoices, tracking campaigns,
and monitoring payment connections.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

import streamlit as st
import plotly.express as px
import pandas as pd

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


# ========== Authentication utilities ==========


def login_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user via API and return tokens."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"email": username, "password": password},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        st.error(f"Connection error: {e}")
    return None


def refresh_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """Refresh access token using refresh token."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/refresh",
            json={"refresh_token": refresh_token},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return None


def get_headers(access_token: str) -> Dict[str, str]:
    """Get headers with bearer token."""
    return {"Authorization": f"Bearer {access_token}"}


# ========== API Client Functions ==========


def fetch_invoices(
    access_token: str,
    status: Optional[str] = None,
    due_date_start: Optional[str] = None,
    due_date_end: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Fetch invoices with optional filters."""
    params = {"skip": skip, "limit": limit}
    if status:
        params["status"] = status
    if due_date_start:
        params["due_date_start"] = due_date_start
    if due_date_end:
        params["due_date_end"] = due_date_end

    try:
        response = requests.get(
            f"{API_BASE_URL}/api/invoices",
            headers=get_headers(access_token),
            params=params,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch invoices: {e}")
    return []


def fetch_invoice(access_token: str, invoice_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single invoice by ID."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/invoices/{invoice_id}",
            headers=get_headers(access_token),
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return None


def update_invoice_status(
    access_token: str, invoice_id: str, status: str, notes: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Update invoice status."""
    try:
        response = requests.patch(
            f"{API_BASE_URL}/api/invoices/{invoice_id}",
            headers=get_headers(access_token),
            json={"status": status, "notes": notes},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return None


def fetch_payment_connections(access_token: str) -> List[Dict[str, Any]]:
    """Fetch user's payment connections."""
    # This endpoint doesn't exist yet, but will be implemented in a future task
    # For now, return mock data or fetch from User model
    return []


def fetch_campaigns(access_token: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch campaigns with A/B test results."""
    # This endpoint doesn't exist yet, will be implemented in Task 4.2
    # For now, we can fetch from campaigns table if it exists
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/campaigns",
            headers=get_headers(access_token),
            params={"limit": limit},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return []


# ========== Admin API Client Functions ==========


def fetch_current_user(access_token: str) -> Optional[Dict[str, Any]]:
    """Fetch current user info including admin status."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/auth/me",
            headers=get_headers(access_token),
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch user info: {e}")
    return None


def fetch_admin_dashboard(access_token: str) -> Optional[Dict[str, Any]]:
    """Fetch admin dashboard overview stats."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/admin/",
            headers=get_headers(access_token),
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch admin dashboard: {e}")
    return None


def fetch_admin_users(
    access_token: str,
    page: int = 1,
    limit: int = 20,
    tier: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> List[Dict[str, Any]]:
    """Fetch all users with filters."""
    params = {
        "page": page,
        "limit": limit,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }
    if tier:
        params["tier"] = tier
    if status:
        params["status"] = status
    if search:
        params["search"] = search

    try:
        response = requests.get(
            f"{API_BASE_URL}/admin/users",
            headers=get_headers(access_token),
            params=params,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch users: {e}")
    return []


def fetch_admin_user_detail(
    access_token: str, user_id: str
) -> Optional[Dict[str, Any]]:
    """Fetch detailed information about a specific user."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/admin/users/{user_id}",
            headers=get_headers(access_token),
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch user detail: {e}")
    return None


def update_user_tier(
    access_token: str,
    user_id: str,
    subscription_tier: str,
    invoice_limit: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Update a user's subscription tier."""
    try:
        payload = {"subscription_tier": subscription_tier}
        if invoice_limit is not None:
            payload["invoice_limit"] = invoice_limit

        response = requests.post(
            f"{API_BASE_URL}/admin/users/{user_id}/tier",
            headers=get_headers(access_token),
            json=payload,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Unknown error")
            st.error(f"Failed to update tier: {error_detail}")
    except requests.RequestException as e:
        st.error(f"Connection error: {e}")
    return None


def fetch_system_metrics(
    access_token: str, hours: int = 24
) -> Optional[Dict[str, Any]]:
    """Fetch system health metrics."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/admin/metrics",
            headers=get_headers(access_token),
            params={"hours": hours},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch system metrics: {e}")
    return None


def fetch_webhook_events(
    access_token: str,
    limit: int = 50,
    status: Optional[str] = None,
    provider: Optional[str] = None,
    hours: int = 24,
) -> List[Dict[str, Any]]:
    """Fetch recent webhook events."""
    params = {"limit": limit, "hours": hours}
    if status:
        params["status"] = status
    if provider:
        params["provider"] = provider

    try:
        response = requests.get(
            f"{API_BASE_URL}/admin/webhooks",
            headers=get_headers(access_token),
            params=params,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch webhook events: {e}")
    return []


def fetch_payment_connections_admin(
    access_token: str, active_only: bool = True, provider: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Fetch all payment connections (admin view)."""
    params = {"active_only": active_only}
    if provider:
        params["provider"] = provider

    try:
        response = requests.get(
            f"{API_BASE_URL}/admin/connections",
            headers=get_headers(access_token),
            params=params,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch payment connections: {e}")
    return []


# ========== Page Components ==========


def render_overview_page(access_token: str):
    """Render the Overview/KPI page."""
    st.title("📊 Overview")
    st.markdown("Welcome to your invoice dashboard!")

    # Fetch invoices for KPI calculations
    invoices = fetch_invoices(access_token, limit=1000)

    if not invoices:
        st.info("No invoices yet. Create your first invoice to get started!")
        return

    df = pd.DataFrame(invoices)

    # Convert date columns
    date_cols = ["due_date", "created_at", "paid_date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Calculate KPIs
    total_invoices = len(df)
    total_amount = float(df["amount"].sum()) if "amount" in df.columns else 0.0
    overdue_count = (
        int(len(df[df["status"] == "overdue"])) if "status" in df.columns else 0
    )
    paid_count = int(len(df[df["status"] == "paid"])) if "status" in df.columns else 0
    recovery_rate = (paid_count / total_invoices * 100) if total_invoices > 0 else 0.0

    # Display KPI cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Invoices", total_invoices)
    with col2:
        st.metric("Total Amount", f"${total_amount:,.2f}")
    with col3:
        st.metric("Overdue", overdue_count, delta_color="inverse")
    with col4:
        st.metric("Recovery Rate", f"{recovery_rate:.1f}%")

    st.divider()

    # Invoice status distribution chart
    if "status" in df.columns and not df["status"].empty:
        st.subheader("Invoice Status Distribution")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]

        fig = px.pie(
            status_counts,
            values="count",
            names="status",
            title="Invoices by Status",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Recent invoices table
    st.subheader("Recent Invoices")
    if "created_at" in df.columns and not df.empty:
        df_sorted = df.sort_values("created_at", ascending=False).head(10)
        display_cols = [
            "invoice_number",
            "client_name",
            "amount",
            "status",
            "due_date",
        ]
        existing_cols = [col for col in display_cols if col in df_sorted.columns]
        if existing_cols:
            display_df = df_sorted[existing_cols].copy()

            # Format dates
            for col in ["due_date", "paid_date"]:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(
                        lambda x: x.strftime("%Y-%m-%d") if pd.notna(x) else ""
                    )

            # Format amount
            if "amount" in display_df.columns and "currency" in display_df.columns:
                display_df["amount"] = display_df.apply(
                    lambda row: f"{row['amount']:,.2f} {row['currency']}", axis=1
                )

            st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_invoices_page(access_token: str):
    """Render the Invoices management page."""
    st.title("📋 Invoices")
    st.markdown("Manage and track your invoices")

    # Filters
    with st.expander("🔍 Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox(
                "Status",
                options=[
                    "",
                    "draft",
                    "sent",
                    "paid",
                    "overdue",
                    "disputed",
                    "canceled",
                ],
                help="Filter by invoice status",
            )
        with col2:
            due_date_start = st.date_input(
                "Due Date From",
                value=None,
                help="Filter invoices due after this date",
            )
        with col3:
            due_date_end = st.date_input(
                "Due Date To",
                value=None,
                help="Filter invoices due before this date",
            )

        # Convert date inputs to strings
        due_start_str = due_date_start.strftime("%Y-%m-%d") if due_date_start else None
        due_end_str = due_date_end.strftime("%Y-%m-%d") if due_date_end else None

        fetch_button = st.button("Apply Filters", type="primary")

    # Fetch invoices
    if fetch_button or "invoices_data" not in st.session_state:
        with st.spinner("Loading invoices..."):
            invoices = fetch_invoices(
                access_token,
                status=status_filter if status_filter else None,
                due_date_start=due_start_str,
                due_date_end=due_end_str,
                limit=200,
            )
            st.session_state.invoices_data = invoices
            st.session_state.invoices_filters = {
                "status": status_filter if status_filter else "",
                "due_start": due_start_str if due_start_str else "",
                "due_end": due_end_str if due_end_str else "",
            }

    # Display invoices
    if "invoices_data" in st.session_state:
        invoices = st.session_state.invoices_data

        if not invoices:
            st.info("No invoices match the current filters.")
        else:
            st.success(f"Found {len(invoices)} invoices")

            # Convert to DataFrame for display
            df = pd.DataFrame(invoices)

            # Format columns
            display_columns = [
                "invoice_number",
                "client_name",
                "client_email",
                "amount",
                "currency",
                "status",
                "due_date",
                "paid_date",
            ]

            existing_cols = [col for col in display_columns if col in df.columns]
            display_df = df[existing_cols].copy()

            # Format dates
            for col in ["due_date", "paid_date"]:
                if col in display_df.columns:
                    display_df[col] = pd.to_datetime(
                        display_df[col], errors="coerce"
                    ).apply(lambda x: x.strftime("%Y-%m-%d") if pd.notna(x) else "")

            # Format amount
            if "amount" in display_df.columns and "currency" in display_df.columns:
                display_df["amount"] = display_df.apply(
                    lambda row: f"{row['amount']:,.2f} {row['currency']}", axis=1
                )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "status": st.column_config.TextColumn(
                        "Status", help="Invoice status"
                    )
                },
            )

            # Quick actions: Update status
            st.divider()
            st.subheader("Quick Actions")

            if "id" in df.columns and "status" in df.columns:
                invoice_options: Dict[str, str] = {}
                for _, row in df.iterrows():
                    inv_id = str(row["id"])
                    inv_num = str(row.get("invoice_number", "N/A"))
                    client = str(row.get("client_name", "Unknown"))
                    key = f"{inv_num} - {client} ({inv_id})"
                    invoice_options[key] = inv_id

                selected_invoice = st.selectbox(
                    "Select invoice to update",
                    options=list(invoice_options.keys()),
                    key="update_invoice_select",
                )

                if selected_invoice:
                    invoice_id = invoice_options[selected_invoice]
                    status_series = df.loc[df["id"] == invoice_id, "status"]
                    if len(status_series) > 0:
                        current_status = str(status_series.iloc[0])
                    else:
                        current_status = "draft"

                    col1, col2 = st.columns(2)
                    with col1:
                        status_list = [
                            "draft",
                            "sent",
                            "paid",
                            "overdue",
                            "disputed",
                            "canceled",
                        ]
                        try:
                            status_index = status_list.index(current_status)
                        except ValueError:
                            status_index = 0
                        new_status = st.selectbox(
                            "New Status",
                            options=status_list,
                            index=status_index,
                        )
                    with col2:
                        notes = st.text_area("Notes (optional)")

                    if st.button("Update Status", type="primary"):
                        result = update_invoice_status(
                            access_token,
                            invoice_id,
                            new_status,
                            notes if notes else None,
                        )
                        if result:
                            st.success("Invoice updated successfully!")
                            # Clear cache to refresh list
                            if "invoices_data" in st.session_state:
                                del st.session_state.invoices_data
                            st.rerun()
                        else:
                            st.error("Failed to update invoice")


def render_campaigns_page(access_token: str):
    """Render the Campaigns and A/B testing page."""
    st.title("📈 Campaigns & A/B Tests")
    st.markdown("Track email campaign performance and A/B test results")

    campaigns = fetch_campaigns(access_token)

    if not campaigns:
        st.info(
            "No campaigns yet. Campaigns will appear here once you start sending follow-up emails."
        )
        return

    df = pd.DataFrame(campaigns)

    # Display campaigns
    st.subheader("Campaign History")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # A/B test analysis (placeholder - will be enhanced when Task 4.2 is complete)
    st.divider()
    st.subheader("A/B Test Analysis")
    st.info("A/B testing framework coming soon!")


def render_settings_page(access_token: str):
    """Render the Settings page with payment connections."""
    st.title("⚙️ Settings")
    st.markdown("Manage your account and payment connections")

    # Payment Connections
    st.subheader("💳 Payment Connections")
    connections = fetch_payment_connections(access_token)

    col1, col2 = st.columns(2)
    with col1:
        active_count = len([c for c in connections if c.get("is_active")])
        st.metric("Active Connections", active_count)

    st.divider()

    # Display existing connections
    if connections:
        for conn in connections:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{conn.get('provider', 'Unknown')}**")
                    if conn.get("connection_name"):
                        st.caption(conn["connection_name"])
                    else:
                        st.caption("Unnamed connection")
                with col2:
                    st.write("Status:")
                    if conn.get("is_active"):
                        st.success("Active")
                    else:
                        st.error("Inactive")
                with col3:
                    conn_id = str(conn.get("id", ""))
                    if st.button("Disconnect", key=f"disconnect_{conn_id}"):
                        st.warning("Disconnect functionality coming soon!")
                st.divider()
    else:
        st.info("No payment connections configured yet.")

    # Add new connection buttons
    st.subheader("Add Connection")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add Stripe", type="secondary", use_container_width=True):
            st.info("Stripe OAuth flow coming soon!")
    with col2:
        if st.button("➕ Add PayPal", type="secondary", use_container_width=True):
            st.info("PayPal OAuth flow coming soon!")
    with col3:
        if st.button("➕ Add Plaid", type="secondary", use_container_width=True):
            st.info("Plaid Link flow coming soon!")

    st.divider()

    # User info
    st.subheader("👤 Account Information")
    st.write(f"**Subscription Tier:** Free")
    st.write(f"**Invoice Limit:** 5 / month")
    st.write("**Upgrade to Pro** for unlimited invoices and AI dispute drafting!")


# ========== Admin Page Components ==========


def render_admin_dashboard_page(access_token: str):
    """Render the Admin Dashboard overview page."""
    st.title("🛡️ Admin Dashboard")
    st.markdown("System overview and management")

    # Fetch admin dashboard stats
    with st.spinner("Loading dashboard data..."):
        dashboard_data = fetch_admin_dashboard(access_token)

    if not dashboard_data:
        st.error("Failed to load admin dashboard data")
        return

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", dashboard_data.get("total_users", 0))
    with col2:
        st.metric("Active Users", dashboard_data.get("active_users", 0))
    with col3:
        st.metric("Total Invoices", dashboard_data.get("total_invoices", 0))
    with col4:
        st.metric(
            "Payment Connections", dashboard_data.get("total_payment_connections", 0)
        )

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Recent Webhook Events (24h)", dashboard_data.get("recent_webhook_count", 0)
        )
    with col2:
        st.metric("Inactive Users", dashboard_data.get("inactive_users", 0))

    st.divider()

    # Tier distribution
    st.subheader("📊 Subscription Tier Distribution")
    tier_dist = dashboard_data.get("tier_distribution", {})
    if tier_dist:
        tier_df = pd.DataFrame(list(tier_dist.items()), columns=["Tier", "Count"])
        fig = px.bar(
            tier_df,
            x="Tier",
            y="Count",
            title="Users by Subscription Tier",
            color="Tier",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No tier distribution data available")

    st.divider()

    # Invoice status distribution
    st.subheader("📋 Invoice Status Overview")
    invoice_status = dashboard_data.get("invoices_by_status", {})
    if invoice_status:
        status_df = pd.DataFrame(
            list(invoice_status.items()), columns=["Status", "Count"]
        )
        fig = px.pie(
            status_df, values="Count", names="Status", title="Invoices by Status"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No invoice data available")

    st.divider()

    # Connections by provider
    st.subheader("💳 Payment Connections by Provider")
    connections_provider = dashboard_data.get("connections_by_provider", {})
    if connections_provider:
        conn_df = pd.DataFrame(
            list(connections_provider.items()), columns=["Provider", "Count"]
        )
        fig = px.bar(
            conn_df,
            x="Provider",
            y="Count",
            title="Connections by Provider",
            color="Provider",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No payment connections data available")

    st.divider()

    # Recent webhook events preview
    st.subheader("🔄 Recent Webhook Events (Last 24h)")
    st.info("View detailed webhook logs in the Webhooks tab")


def render_admin_users_page(access_token: str):
    """Render the Admin Users management page."""
    st.title("👥 User Management")
    st.markdown("View and manage user accounts and subscriptions")

    # Initialize session state variables
    if "admin_users_page" not in st.session_state:
        st.session_state.admin_users_page = 1
    if "admin_users_data" not in st.session_state:
        st.session_state.admin_users_data = None
    if "admin_users_filters" not in st.session_state:
        st.session_state.admin_users_filters = {}
    if "selected_user_detail" not in st.session_state:
        st.session_state.selected_user_detail = None
    if "selected_user_id" not in st.session_state:
        st.session_state.selected_user_id = None

    # Filters
    with st.expander("🔍 Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            tier_filter = st.selectbox(
                "Subscription Tier",
                options=["", "free", "pro", "enterprise"],
                help="Filter by subscription tier",
            )
        with col2:
            status_filter = st.selectbox(
                "Status",
                options=["", "active", "inactive"],
                help="Filter by user status",
            )
        with col3:
            search_query = st.text_input(
                "Search",
                placeholder="Email or name...",
                help="Search by email or name",
            )

        col4, col5, col6 = st.columns(3)
        with col4:
            sort_by = st.selectbox(
                "Sort By", options=["created_at", "email", "subscription_tier"], index=0
            )
        with col5:
            sort_order = st.selectbox("Sort Order", options=["desc", "asc"], index=0)
        with col6:
            page_size = st.selectbox("Page Size", options=[10, 20, 50, 100], index=1)

        fetch_users_btn = st.button("Apply Filters", type="primary")

    # Fetch users
    if "admin_users_page" not in st.session_state:
        st.session_state.admin_users_page = 1

    if fetch_users_btn or "admin_users_data" not in st.session_state:
        st.session_state.admin_users_page = 1
        with st.spinner("Loading users..."):
            users = fetch_admin_users(
                access_token,
                page=1,
                limit=page_size,
                tier=tier_filter if tier_filter else None,
                status=status_filter if status_filter else None,
                search=search_query if search_query else None,
                sort_by=sort_by,
                sort_order=sort_order,
            )
            st.session_state.admin_users_data = users
            st.session_state.admin_users_filters = {
                "tier": tier_filter,
                "status": status_filter,
                "search": search_query,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "page_size": page_size,
            }

    # Display users
    if "admin_users_data" in st.session_state:
        users = st.session_state.admin_users_data
        filters = st.session_state.get("admin_users_filters", {})

        if not users:
            st.info("No users match the current filters.")
        else:
            st.success(f"Found {len(users)} users")

            # Users table
            user_df = pd.DataFrame(users)

            # Format for display
            display_cols = [
                "id",
                "email",
                "full_name",
                "subscription_tier",
                "invoice_limit",
                "is_active",
                "created_at",
            ]
            existing_cols = [col for col in display_cols if col in user_df.columns]
            display_df = user_df[existing_cols].copy()

            # Format dates
            if "created_at" in display_df.columns:
                display_df["created_at"] = pd.to_datetime(
                    display_df["created_at"], errors="coerce"
                ).apply(lambda x: x.strftime("%Y-%m-%d %H:%M") if pd.notna(x) else "")

            # Format boolean
            if "is_active" in display_df.columns:
                display_df["is_active"] = display_df["is_active"].apply(
                    lambda x: "✅" if x else "❌"
                )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": st.column_config.TextColumn(
                        "User ID", help="User unique identifier"
                    ),
                    "email": st.column_config.TextColumn("Email"),
                    "full_name": st.column_config.TextColumn("Full Name"),
                    "subscription_tier": st.column_config.TextColumn("Tier"),
                    "invoice_limit": st.column_config.NumberColumn("Invoice Limit"),
                    "is_active": st.column_config.TextColumn("Active"),
                },
            )

            # User detail & tier update section
            st.divider()
            st.subheader("🔧 Update User Subscription")

            col1, col2 = st.columns([2, 3])
            with col1:
                user_options = {}
                for _, row in user_df.iterrows():
                    user_id = str(row["id"])
                    display_name = f"{row.get('email', 'Unknown')} (Tier: {row.get('subscription_tier', 'N/A')})"
                    user_options[display_name] = user_id

                if user_options:
                    selected_user_display = st.selectbox(
                        "Select User",
                        options=list(user_options.keys()),
                        key="user_select",
                    )
                    selected_user_id = user_options[selected_user_display]

                    # Fetch user details
                    if st.button("Load User Details", type="secondary"):
                        with st.spinner("Loading user details..."):
                            user_detail = fetch_admin_user_detail(
                                access_token, selected_user_id
                            )
                            if user_detail:
                                st.session_state.selected_user_detail = user_detail
                            else:
                                st.error("Failed to load user details")

            with col2:
                if "selected_user_detail" in st.session_state:
                    detail = st.session_state.selected_user_detail
                    st.write(f"**Email:** {detail.get('email', 'N/A')}")
                    st.write(f"**Name:** {detail.get('full_name', 'N/A')}")
                    st.write(
                        f"**Current Tier:** `{detail.get('subscription_tier', 'N/A')}`"
                    )
                    st.write(f"**Invoice Limit:** {detail.get('invoice_limit', 0)}")
                    st.write(f"**Invoices Count:** {detail.get('invoices_count', 0)}")
                    st.write(
                        f"**Payment Connections:** {detail.get('payment_connections_count', 0)}"
                    )
                    st.write(f"**Active:** {'✅' if detail.get('is_active') else '❌'}")

            # Tier update form
            if "selected_user_detail" in st.session_state:
                st.divider()
                st.subheader("📝 Update Subscription Tier")
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_tier = st.selectbox(
                        "New Tier",
                        options=["free", "pro", "enterprise"],
                        index=["free", "pro", "enterprise"].index(
                            st.session_state.selected_user_detail.get(
                                "subscription_tier", "free"
                            )
                        ),
                    )
                with col2:
                    custom_limit = st.number_input(
                        "Custom Invoice Limit (optional)",
                        min_value=0,
                        value=st.session_state.selected_user_detail.get(
                            "invoice_limit", 5
                        ),
                        help="Leave empty for default tier limits",
                    )
                with col3:
                    st.write("")
                    st.write("")
                    update_btn = st.button("💾 Update Tier", type="primary")

                if update_btn:
                    with st.spinner("Updating user tier..."):
                        result = update_user_tier(
                            access_token,
                            selected_user_id,
                            new_tier,
                            custom_limit
                            if custom_limit
                            != st.session_state.selected_user_detail.get(
                                "invoice_limit", 5
                            )
                            else None,
                        )
                        if result:
                            st.success(
                                f"✅ User tier updated: {result.get('old_tier')} → {result.get('new_tier')}"
                            )
                            # Refresh user details
                            fresh_detail = fetch_admin_user_detail(
                                access_token, selected_user_id
                            )
                            if fresh_detail:
                                st.session_state.selected_user_detail = fresh_detail
                            st.rerun()
                        else:
                            st.error("Failed to update user tier")

            # Pagination
            st.divider()
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                total_users = len(users)
                page_size = filters.get("page_size", 20)
                total_pages = (total_users + page_size - 1) // page_size
                current_page = st.session_state.get("admin_users_page", 1)
                st.write(f"Page {current_page} of {total_pages}")

                col_prev, col_next = st.columns(2)
                with col_prev:
                    if st.button("◀️ Previous", disabled=current_page <= 1):
                        st.session_state.admin_users_page = current_page - 1
                        st.rerun()
                with col_next:
                    if st.button("Next ▶️", disabled=current_page >= total_pages):
                        st.session_state.admin_users_page = current_page + 1
                        st.rerun()


def render_admin_metrics_page(access_token: str):
    """Render the System Metrics page."""
    st.title("📈 System Health")
    st.markdown("Monitor system performance and Celery workers")

    # Time range selector
    hours = st.slider(
        "Lookback Period (hours)",
        min_value=1,
        max_value=168,
        value=24,
        step=1,
        help="How many hours of historical data to display",
    )

    with st.spinner("Loading system metrics..."):
        metrics = fetch_system_metrics(access_token, hours=hours)

    if not metrics:
        st.error("Failed to load system metrics")
        return

    # Celery workers section
    st.subheader("🐝 Celery Workers")
    celery_data = metrics.get("celery_workers", {})
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Workers", celery_data.get("active", 0))
    with col2:
        st.metric("Total Workers", celery_data.get("total", 0))

    # Worker details (if available)
    worker_details = celery_data.get("details", [])
    if worker_details:
        st.write("Worker Details:")
        worker_df = pd.DataFrame(worker_details)
        st.dataframe(worker_df, use_container_width=True, hide_index=True)
    else:
        st.info("Worker detail monitoring not yet implemented - basic stats only")

    st.divider()

    # API Latency
    st.subheader("⚡ API Latency")
    latency_p95 = metrics.get("api_latency_p95")
    if latency_p95:
        st.metric("P95 Latency (ms)", f"{latency_p95:.2f}")
    else:
        st.info("No latency data available yet")

    st.divider()

    # Last sync status
    st.subheader("🔄 Data Synchronization")
    last_sync = metrics.get("last_sync_status")
    if last_sync:
        st.write(f"**Last Sync Completed:** {last_sync.get('completed_at', 'Unknown')}")
        sync_metrics = last_sync.get("metrics", {})
        if sync_metrics:
            st.json(sync_metrics)
    else:
        st.info("No sync jobs completed yet")

    st.divider()

    # Recent errors
    st.subheader("⚠️ Recent Errors")
    errors = metrics.get("recent_errors", [])
    if errors:
        error_df = pd.DataFrame(errors)
        st.dataframe(error_df, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No recent errors!")

    st.divider()

    # Uptime
    st.subheader("⏱️ Uptime")
    uptime_days = metrics.get("uptime_days", 0)
    st.metric("Uptime (days)", f"{uptime_days:.2f}")
    st.caption(
        "Note: Uptime is based on lookback period, not actual process start time"
    )


def render_admin_webhooks_page(access_token: str):
    """Render the Webhook Events page."""
    st.title("🔄 Webhook Events")
    st.markdown("View recent webhook processing logs")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        webhook_hours = st.slider(
            "Last N hours",
            min_value=1,
            max_value=720,
            value=24,
            key="webhook_hours",
        )
    with col2:
        provider_filter = st.selectbox(
            "Provider",
            options=["", "stripe", "paypal", "plaid"],
            help="Filter by payment provider",
        )
    with col3:
        status_filter = st.selectbox(
            "Status",
            options=["", "pending", "processed", "failed"],
            help="Filter by processing status",
        )

    with st.spinner("Loading webhook events..."):
        events = fetch_webhook_events(
            access_token,
            limit=100,
            hours=webhook_hours,
            provider=provider_filter if provider_filter else None,
            status=status_filter if status_filter else None,
        )

    if not events:
        st.info("No webhook events found matching the criteria")
        return

    st.success(f"Found {len(events)} events")

    # Convert to DataFrame
    events_df = pd.DataFrame(events)

    # Display table
    display_cols = [
        "id",
        "provider",
        "event_type",
        "processing_status",
        "processing_error",
        "created_at",
    ]
    existing_cols = [col for col in display_cols if col in events_df.columns]
    display_df = events_df[existing_cols].copy()

    # Format datetime
    if "created_at" in display_df.columns:
        display_df["created_at"] = pd.to_datetime(
            display_df["created_at"], errors="coerce"
        ).apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(x) else "")

    # Highlight errors
    if "processing_status" in display_df.columns:

        def color_status(val):
            if val == "failed":
                return "background-color: #ffcdd2"
            elif val == "processed":
                return "background-color: #c8e6c9"
            return ""

        styled_df = display_df.style.applymap(
            color_status, subset=["processing_status"]
        )
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_admin_connections_page(access_token: str):
    """Render the Payment Connections admin page."""
    st.title("🔗 Payment Connections")
    st.markdown("View all payment provider connections across users")

    col1, col2 = st.columns(2)
    with col1:
        active_only = st.checkbox("Show active only", value=True)
    with col2:
        provider_filter = st.selectbox(
            "Filter by Provider",
            options=["", "stripe", "paypal", "plaid"],
            help="Filter connections by provider",
        )

    with st.spinner("Loading connections..."):
        connections = fetch_payment_connections_admin(
            access_token,
            active_only=active_only,
            provider=provider_filter if provider_filter else None,
        )

    if not connections:
        st.info("No payment connections found")
        return

    st.success(f"Found {len(connections)} connections")

    conn_df = pd.DataFrame(connections)

    display_cols = [
        "id",
        "user_email",
        "user_full_name",
        "provider",
        "connection_name",
        "is_active",
        "last_sync_at",
        "created_at",
    ]
    existing_cols = [col for col in display_cols if col in conn_df.columns]
    display_df = conn_df[existing_cols].copy()

    # Format dates
    date_cols = ["last_sync_at", "created_at"]
    for col in date_cols:
        if col in display_df.columns:
            display_df[col] = pd.to_datetime(display_df[col], errors="coerce").apply(
                lambda x: x.strftime("%Y-%m-%d %H:%M") if pd.notna(x) else "Never"
            )

    # Format boolean
    if "is_active" in display_df.columns:
        display_df["is_active"] = display_df["is_active"].apply(
            lambda x: "✅" if x else "❌"
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "user_email": st.column_config.TextColumn("User Email"),
            "user_full_name": st.column_config.TextColumn("User Name"),
            "provider": st.column_config.TextColumn("Provider"),
            "connection_name": st.column_config.TextColumn("Connection Name"),
        },
    )

    st.divider()
    st.markdown("**Summary:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Connections", len(connections))
    with col2:
        active_conns = len([c for c in connections if c.get("is_active")])
        st.metric("Active Connections", active_conns)
    with col3:
        providers = (
            conn_df["provider"].unique() if "provider" in conn_df.columns else []
        )
        st.metric("Unique Providers", len(providers))


# ========== Main App ==========


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Invoice Resolver AI",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state for authentication
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "refresh_token" not in st.session_state:
        st.session_state.refresh_token = None
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

    # Check for token refresh
    if st.session_state.authenticated and st.session_state.refresh_token:
        new_tokens = refresh_access_token(st.session_state.refresh_token)
        if new_tokens:
            st.session_state.access_token = new_tokens["access_token"]
            st.session_state.refresh_token = new_tokens["refresh_token"]
        else:
            # Refresh failed, force logout
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.rerun()

    # If not authenticated, show login form
    if not st.session_state.authenticated:
        st.title("📋 Invoice Resolver AI")
        st.markdown("---")
        st.subheader("Login")

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="You@example.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    with st.spinner("Signing in..."):
                        tokens = login_user(email, password)
                        if tokens:
                            # Fetch user info to get admin status
                            user_info = fetch_current_user(tokens["access_token"])
                            is_admin = (
                                user_info.get("is_admin", False) if user_info else False
                            )

                            st.session_state.authenticated = True
                            st.session_state.access_token = tokens["access_token"]
                            st.session_state.refresh_token = tokens["refresh_token"]
                            st.session_state.user_info = user_info
                            st.session_state.is_admin = is_admin
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password")

        st.markdown("---")
        st.markdown("Don't have an account?")
        if st.button("Sign Up", key="signup_button"):
            st.info(
                "Registration via API. Use /api/auth/register endpoint or create an account through the API."
            )
        return

    # Ensure access token exists
    if not st.session_state.access_token:
        st.error("Authentication error. Please log in again.")
        st.session_state.authenticated = False
        st.rerun()
        return

    # Fetch user info if not already loaded (for admin check)
    if not st.session_state.user_info:
        user_info = fetch_current_user(st.session_state.access_token)
        if user_info:
            st.session_state.user_info = user_info
            st.session_state.is_admin = user_info.get("is_admin", False)
        else:
            st.error("Failed to fetch user information")
            st.session_state.authenticated = False
            st.rerun()
            return

    is_admin = st.session_state.is_admin

    # Build navigation options based on user role
    nav_options = ["📊 Overview", "📋 Invoices", "⚙️ Settings"]
    if is_admin:
        nav_options.insert(1, "📈 Campaigns")  # Keep Campaigns for admins too
        nav_options.append("🛡️ Admin")

    # Authenticated: Show main app with sidebar navigation
    with st.sidebar:
        st.title("📋 Invoice AI")
        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigation",
            options=nav_options,
            label_visibility="collapsed",
        )

        # Show role badge
        if is_admin:
            st.markdown("---")
            st.markdown("🛡️ **Admin Mode**")

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.session_state.user_info = None
            st.session_state.is_admin = False
            st.rerun()

        # User info in sidebar
        st.markdown("---")
        if st.session_state.user_info:
            user = st.session_state.user_info
            st.caption(f"**{user.get('email', 'Unknown')}**")
            st.caption(f"Tier: {user.get('subscription_tier', 'free')}")
        st.caption("Invoice Resolver AI v0.2.0")

    # Render selected page
    access_token = st.session_state.access_token
    if page == "📊 Overview":
        render_overview_page(access_token)
    elif page == "📋 Invoices":
        render_invoices_page(access_token)
    elif page == "⚙️ Settings":
        render_settings_page(access_token)
    elif page == "📈 Campaigns":
        render_campaigns_page(access_token)
    elif page == "🛡️ Admin":
        # Admin sub-navigation
        admin_pages = {
            "📊 Dashboard": render_admin_dashboard_page,
            "👥 Users": render_admin_users_page,
            "📈 Metrics": render_admin_metrics_page,
            "🔄 Webhooks": render_admin_webhooks_page,
            "🔗 Connections": render_admin_connections_page,
        }

        admin_page = st.radio(
            "Admin Sections",
            options=list(admin_pages.keys()),
            label_visibility="collapsed",
        )

        st.divider()
        admin_pages[admin_page](access_token)


if __name__ == "__main__":
    main()
