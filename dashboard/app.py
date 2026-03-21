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
                            st.session_state.authenticated = True
                            st.session_state.access_token = tokens["access_token"]
                            st.session_state.refresh_token = tokens["refresh_token"]
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

    # Authenticated: Show main app with sidebar navigation
    with st.sidebar:
        st.title("📋 Invoice AI")
        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigation",
            options=["📊 Overview", "📋 Invoices", "📈 Campaigns", "⚙️ Settings"],
            label_visibility="collapsed",
        )

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.rerun()

        # User info in sidebar
        st.markdown("---")
        st.caption("Invoice Resolver AI v0.1.0")

    # Render selected page
    access_token = st.session_state.access_token
    if page == "📊 Overview":
        render_overview_page(access_token)
    elif page == "📋 Invoices":
        render_invoices_page(access_token)
    elif page == "📈 Campaigns":
        render_campaigns_page(access_token)
    elif page == "⚙️ Settings":
        render_settings_page(access_token)


if __name__ == "__main__":
    main()
