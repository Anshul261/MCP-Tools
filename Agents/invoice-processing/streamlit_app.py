"""
Streamlit UI for Invoice Processing API
Simple interface to test and interact with the REST API
"""

import streamlit as st
import requests
import time
import json
from datetime import datetime
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

API_BASE = "http://localhost:8000/api/v1"
UPLOAD_FOLDER = "uploads"

# Page config
st.set_page_config(
    page_title="Invoice Processing System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# Sidebar Navigation
# ============================================================================

st.sidebar.title("📄 Invoice Processor")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🚀 Upload Invoice", "📊 Monitor Workflow", "📈 View Results", "⚙️ Settings"],
    label_visibility="collapsed",
)

# Add session ID input in sidebar for easy navigation
st.sidebar.markdown("---")
st.sidebar.subheader("Quick Access")
session_id_input = st.sidebar.text_input("Enter Session ID to check status:")

# ============================================================================
# Helper Functions
# ============================================================================


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=2)
        return response.status_code == 200
    except Exception as e:
        return False


def get_workflow_status(session_id: str) -> dict:
    """Get workflow status from API"""
    try:
        response = requests.get(f"{API_BASE}/workflow/{session_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None


def get_workflow_state(session_id: str) -> dict:
    """Get detailed workflow state from API"""
    try:
        response = requests.get(f"{API_BASE}/workflow/{session_id}/state")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None


def submit_review(session_id: str, approved: bool, notes: str, reviewer_id: str):
    """Submit human review response"""
    try:
        response = requests.post(
            f"{API_BASE}/workflow/{session_id}/review-response",
            json={
                "approved": approved,
                "notes": notes,
                "reviewer_id": reviewer_id,
            },
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error submitting review: {str(e)}")
        return False


def get_invoices(limit: int = 20, offset: int = 0) -> dict:
    """Query saved invoices"""
    try:
        response = requests.get(
            f"{API_BASE}/invoices",
            params={"limit": limit, "offset": offset},
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error querying invoices: {str(e)}")
        return None


def get_stats() -> dict:
    """Get API statistics"""
    try:
        response = requests.get(f"{API_BASE}/stats")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None


def render_progress_bar(step: int, total_steps: int = 5):
    """Render a custom progress bar"""
    steps = ["Extract", "Analyze", "Validate", "Review", "Persist"]
    cols = st.columns(total_steps)

    for i, col in enumerate(cols):
        with col:
            if i < step:
                st.success(f"✓ {steps[i]}")
            elif i == step:
                st.info(f"⏳ {steps[i]}")
            else:
                st.write(f"◯ {steps[i]}")


def render_invoice_data(invoice_data: dict):
    """Render invoice data in a nice format"""
    if not invoice_data:
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Invoice Information**")
        st.write(f"Invoice #: {invoice_data.get('invoice_no', 'N/A')}")
        st.write(f"Date: {invoice_data.get('date_of_issue', 'N/A')}")
        st.write(f"Total: ${invoice_data.get('gross_worth_total', 'N/A')}")

    with col2:
        st.write("**Parties**")
        st.write(f"Seller: {invoice_data.get('seller_name', 'N/A')}")
        st.write(f"Client: {invoice_data.get('client_name', 'N/A')}")

    # Line items preview
    st.write("**Line Items**")
    line_items = invoice_data.get("line_items", [])
    if line_items:
        for i, item in enumerate(line_items[:5], 1):
            st.write(
                f"{i}. {item.get('description', 'N/A')} - "
                f"Qty: {item.get('qty', 0)} @ ${item.get('net_price', 0)}"
            )
        if len(line_items) > 5:
            st.write(f"... and {len(line_items) - 5} more items")
    else:
        st.write("No line items found")


# ============================================================================
# PAGE 1: Upload Invoice
# ============================================================================

if page == "🚀 Upload Invoice":
    st.title("📄 Upload Invoice")

    # Check API health
    if not check_api_health():
        st.error(
            "❌ API Server is not running! Start it with: `python server.py`"
        )
        st.stop()

    st.success("✅ API Server is running")

    st.markdown(
        "Upload an invoice image (JPG/PNG) to start processing. "
        "The system will extract data, validate it, and save it to the database."
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose invoice image",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
        )

    if uploaded_file is not None:
        # Show preview
        st.image(uploaded_file, caption="Uploaded Invoice", use_column_width=True)

        with st.spinner("Processing..."):
            # Upload to API
            files = {"file": uploaded_file.getvalue()}
            response = requests.post(f"{API_BASE}/workflow/start", files=files)

            if response.status_code == 202:
                result = response.json()
                session_id = result["session_id"]

                st.success(f"✅ Upload successful! Session ID: `{session_id}`")
                st.session_state.session_id = session_id

                # Store in session state for navigation
                st.write("### Next Steps:")
                st.write("1. Go to **📊 Monitor Workflow** tab to track progress")
                st.write("2. You can also use this session ID to check status later")
                st.write(f"\n**Session ID:** `{session_id}`")

                # Show quick status
                st.markdown("---")
                st.write("### Current Status:")

                status = get_workflow_status(session_id)
                if status:
                    st.write(f"State: **{status['state']}**")
                    st.write(f"Step: {status['current_step']}/5")

            else:
                st.error(f"Upload failed: {response.status_code}")
                st.write(response.text)


# ============================================================================
# PAGE 2: Monitor Workflow
# ============================================================================

elif page == "📊 Monitor Workflow":
    st.title("📊 Monitor Workflow")

    # Get session ID
    session_id = session_id_input or st.session_state.get("session_id")

    if not session_id:
        st.info(
            "📌 Enter a session ID in the left sidebar or upload an invoice first."
        )
        st.stop()

    # Check API health
    if not check_api_health():
        st.error("❌ API Server is not running!")
        st.stop()

    st.write(f"**Session ID:** `{session_id}`")

    # Polling button
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("📋 Full Details", use_container_width=True):
            state = get_workflow_state(session_id)
            if state:
                st.json(state)

    # Get current status
    status = get_workflow_status(session_id)

    if not status:
        st.error("Session not found or API error")
        st.stop()

    # Display status
    st.markdown("---")

    # Status badges
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        state_color = {
            "completed": "🟢",
            "processing": "🟡",
            "awaiting_human_input": "🔵",
            "failed": "🔴",
            "rejected": "⚫",
        }.get(status["state"], "⚪")
        st.metric("State", f"{state_color} {status['state'].replace('_', ' ').title()}")

    with col2:
        st.metric("Current Step", f"{status['current_step']}/5")

    with col3:
        if status["confidence_score"] is not None:
            confidence_color = "🟢" if status["confidence_score"] > 0.9 else "🟡"
            st.metric(
                "Confidence",
                f"{status['confidence_score']:.1%}",
            )
        else:
            st.metric("Confidence", "Pending")

    with col4:
        progress_pct = status["progress"]["percentage"] if status["progress"] else 0
        st.metric("Progress", f"{progress_pct}%")

    # Progress bar
    st.write("### Workflow Progress")
    render_progress_bar(status["current_step"])

    st.markdown("---")

    # Invoice data
    if status["invoice_data"]:
        st.write("### Invoice Data Preview")
        render_invoice_data(status["invoice_data"])
        st.markdown("---")

    # Validation errors
    if status["validation_errors"]:
        with st.expander("⚠️ Validation Errors", expanded=True):
            for error in status["validation_errors"]:
                st.write(f"• {error}")

    # Human Review Section
    if status["is_paused"]:
        st.markdown("---")
        st.warning(
            f"⏸️ **Workflow Paused** - Awaiting human review\n\n{status['paused_reason']}"
        )

        # Review form
        st.write("### Human Review")

        col1, col2 = st.columns(2)

        with col1:
            review_notes = st.text_area(
                "Review Notes",
                placeholder="Any comments about this invoice?",
                height=100,
            )

        with col2:
            st.write("")  # spacing

            approved = st.radio(
                "Decision",
                ["Approve", "Reject"],
                horizontal=False,
            )

            reviewer_id = st.text_input(
                "Your ID / Email",
                placeholder="john.doe@company.com",
            )

        # Submit button
        if st.button(
            f"{'✅ Approve' if approved == 'Approve' else '❌ Reject'} Invoice",
            use_container_width=True,
            type="primary" if approved == "Approve" else "secondary",
        ):
            with st.spinner("Submitting review..."):
                success = submit_review(
                    session_id,
                    approved=(approved == "Approve"),
                    notes=review_notes,
                    reviewer_id=reviewer_id or "unknown",
                )

                if success:
                    st.success("✅ Review submitted successfully!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Failed to submit review")

    # Completion message
    if status["state"] == "completed":
        st.success(
            f"✅ **Completed!** Invoice saved with ID: {status.get('invoice_id')}"
        )

    if status["state"] == "rejected":
        st.error("❌ **Rejected** - Invoice was not approved")

    if status["state"] == "failed":
        st.error(f"❌ **Failed** - {status.get('error', 'Unknown error')}")

    # Auto-refresh if processing
    if status["state"] in ["processing", "initializing"]:
        time.sleep(2)
        st.rerun()


# ============================================================================
# PAGE 3: View Results
# ============================================================================

elif page == "📈 View Results":
    st.title("📈 View Results")

    # Check API health
    if not check_api_health():
        st.error("❌ API Server is not running!")
        st.stop()

    st.markdown("View all processed invoices saved in the database.")

    # Get statistics
    stats = get_stats()
    if stats and "statistics" in stats:
        st_data = stats["statistics"]

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Sessions", st_data.get("total_sessions", 0))

        with col2:
            st.metric("Completed", st_data.get("completed", 0))

        with col3:
            st.metric("Failed", st_data.get("failed", 0))

        with col4:
            st.metric("Paused", st_data.get("paused", 0))

        with col5:
            success_rate = st_data.get("success_rate", 0)
            st.metric(
                "Success Rate",
                f"{success_rate:.1f}%",
            )

    st.markdown("---")

    # Query invoices
    limit = st.select_slider("Results per page", options=[5, 10, 20, 50], value=20)
    offset = st.number_input("Page offset", min_value=0, value=0, step=1)

    with st.spinner("Loading invoices..."):
        result = get_invoices(limit=limit, offset=offset)

    if result and result["invoices"]:
        st.write(f"Showing {len(result['invoices'])} of {result['total']} invoices")

        # Create consolidated table with all invoices and line items
        all_rows = []

        for idx, inv in enumerate(result["invoices"]):
            try:
                # Convert numeric strings to floats/decimals
                net_total = float(inv.get("net_worth_total", 0)) if inv.get("net_worth_total") else 0
                vat_amt = float(inv.get("vat_total", 0)) if inv.get("vat_total") else 0
                gross_total = float(inv.get("gross_worth_total", 0)) if inv.get("gross_worth_total") else 0
                confidence = float(inv.get("confidence_score", 0)) if inv.get("confidence_score") else 0
                vat_pct = float(inv.get("vat_percent", 0)) if inv.get("vat_percent") else 0

                line_items = inv.get("line_items", [])

                # If no line items, add invoice summary row
                if not line_items:
                    all_rows.append({
                        "Invoice #": inv.get("invoice_no", "N/A"),
                        "Seller": inv.get("seller_name", "N/A")[:25],
                        "Client": inv.get("client_name", "N/A")[:25],
                        "Item #": "-",
                        "Item Description": "-",
                        "Qty": "-",
                        "Unit": "-",
                        "Net Price": "-",
                        "Net Worth": "-",
                        "Item VAT %": "-",
                        "Item Gross": "-",
                        "Invoice Total": f"${gross_total:.2f}",
                        "VAT %": f"{vat_pct:.1f}%",
                        "Confidence": f"{confidence:.1%}",
                        "Date": str(inv.get("date_of_issue", "N/A")),
                    })
                else:
                    # Add row for each line item
                    for item in line_items:
                        try:
                            qty = float(item.get("qty", 0)) if item.get("qty") else 0
                            net_price = float(item.get("net_price", 0)) if item.get("net_price") else 0
                            net_worth = float(item.get("net_worth", 0)) if item.get("net_worth") else 0
                            gross_worth = float(item.get("gross_worth", 0)) if item.get("gross_worth") else 0
                            item_vat = float(item.get("vat_percent", 0)) if item.get("vat_percent") else 0

                            all_rows.append({
                                "Invoice #": inv.get("invoice_no", "N/A"),
                                "Seller": inv.get("seller_name", "N/A")[:25],
                                "Client": inv.get("client_name", "N/A")[:25],
                                "Item #": item.get("item_no"),
                                "Item Description": item.get("description", "N/A")[:30],
                                "Qty": f"{qty:.2f}",
                                "Unit": item.get("unit_measure", ""),
                                "Net Price": f"${net_price:.2f}",
                                "Net Worth": f"${net_worth:.2f}",
                                "Item VAT %": f"{item_vat:.1f}%",
                                "Item Gross": f"${gross_worth:.2f}",
                                "Invoice Total": f"${gross_total:.2f}",
                                "VAT %": f"{vat_pct:.1f}%",
                                "Confidence": f"{confidence:.1%}",
                                "Date": str(inv.get("date_of_issue", "N/A")),
                            })
                        except (ValueError, TypeError):
                            continue

            except (ValueError, TypeError) as e:
                st.warning(f"Error processing invoice: {str(e)}")
                continue

        # Display consolidated table
        if all_rows:
            st.dataframe(all_rows, use_container_width=True, height=600)
        else:
            st.warning("No valid data to display")

        # Pagination
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col2:
            current_page = offset // limit + 1
            total_pages = (result["total"] + limit - 1) // limit
            st.write(f"Page {current_page} of {total_pages}")

    else:
        st.info("No invoices found in database")


# ============================================================================
# PAGE 4: Settings
# ============================================================================

elif page == "⚙️ Settings":
    st.title("⚙️ Settings")

    st.markdown("### API Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Current API Base URL:**")
        st.code(API_BASE)

    with col2:
        st.write("**Change API URL:**")
        new_api_url = st.text_input(
            "API URL",
            value=API_BASE,
            label_visibility="collapsed",
        )
        if new_api_url != API_BASE:
            st.info(f"Note: URL would be {new_api_url}")

    st.markdown("---")

    st.markdown("### API Health")

    if st.button("Check API Status", use_container_width=True):
        if check_api_health():
            st.success("✅ API is running and healthy")

            # Get stats
            stats = get_stats()
            if stats:
                st.json(stats)
        else:
            st.error("❌ API is not accessible")
            st.write("Make sure to start the API with: `python server.py`")

    st.markdown("---")

    st.markdown("### API Endpoints")

    endpoints = {
        "Start Workflow": "POST /api/v1/workflow/start",
        "Get Status": "GET /api/v1/workflow/{session_id}",
        "Get State": "GET /api/v1/workflow/{session_id}/state",
        "Submit Review": "POST /api/v1/workflow/{session_id}/review-response",
        "Query Invoices": "GET /api/v1/invoices",
        "Health Check": "GET /api/v1/health",
        "Statistics": "GET /api/v1/stats",
    }

    for name, endpoint in endpoints.items():
        st.write(f"**{name}**")
        st.code(endpoint, language="http")

    st.markdown("---")

    st.markdown("### Documentation")
    st.write(
        """
    - **API Docs:** http://localhost:8000/docs
    - **API Usage Guide:** See `API_USAGE.md` file
    - **Architecture:** See `ARCHITECTURE.md` file
    """
    )

    st.markdown("---")

    st.markdown("### Getting Started")
    st.write(
        """
    1. **Start the API:** `python server.py`
    2. **Upload an invoice:** Go to "Upload Invoice" tab
    3. **Monitor progress:** Go to "Monitor Workflow" tab
    4. **Approve if needed:** Review and approve/reject invoices
    5. **View results:** Go to "View Results" tab
    """
    )


# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #666; font-size: 12px;">
    Invoice Processing System • Powered by Agno + FastAPI • 2024
</div>
""",
    unsafe_allow_html=True,
)
