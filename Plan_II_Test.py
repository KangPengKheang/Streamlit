# =========================
# UI-ONLY STREAMLIT APP (Deploy first)
# Later you can connect Google Sheets by filling the TODO functions
# =========================

import os
import base64
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

kh_time = datetime.now(ZoneInfo("Asia/Phnom_Penh"))

# -------------------------
# CONFIG (Keep for later)
# -------------------------
SHEET_ID = "YOUR_SHEET_ID_LATER"
WORKSHEET_NAME = "retail_data"   # later
USERS_SHEET_NAME = "Users"       # later

# === MUST BE FIRST STREAMLIT COMMAND ===
st.set_page_config(page_title="Sales Performance Dashboard", layout="wide", page_icon="📊")

# -------------------------
# CSS (Same style)
# -------------------------
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .function-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
        border-left: 5px solid #2E8B57;
    }
    .metric-card {
        background: linear-gradient(135deg, #f0f8ff 0%, #e0f0e0 100%);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .stButton>button {
        background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .highlight {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 10px 0;
    }
    .tab-content {
        padding: 20px;
        background: white;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .header-style {
        background: linear-gradient(90deg, #2E8B57 0%, #3CB371 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 15px 0;
        font-size: 1.3em;
        font-weight: bold;
    }

    /* Auth tabs look like top nav */
    div[data-baseweb="tab-list"] { gap: 12px; }
    button[data-baseweb="tab"] { font-size: 16px; font-weight: 700; padding: 10px 16px; }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------
# Helpers
# -------------------------
def get_base64_encoded_image(image_path: str) -> str:
    if not image_path or not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

LOGO_PATH = "Logo-CMCB_FA-15.png"
logo_data = get_base64_encoded_image(LOGO_PATH)

# -------------------------
# Session State
# -------------------------
def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}
    if "staff_id" not in st.session_state:
        st.session_state.staff_id = ""
    if "customers" not in st.session_state:
        st.session_state.customers = pd.DataFrame()

    # planning defaults (same idea as your structure)
    if "plan_date" not in st.session_state:
        st.session_state.plan_date = datetime.now().date()

    if "tasks" not in st.session_state:
        st.session_state.tasks = [
            {
                "start_time": datetime.strptime("08:00", "%H:%M").time(),
                "end_time": datetime.strptime("12:00", "%H:%M").time(),
                "plan_date": st.session_state.plan_date,
                "activity": "",
                "location": "",
                "num_customers": "",
                "customers": [],
            },
            {
                "start_time": datetime.strptime("12:00", "%H:%M").time(),
                "end_time": datetime.strptime("16:30", "%H:%M").time(),
                "plan_date": st.session_state.plan_date,
                "activity": "",
                "location": "",
                "num_customers": "",
                "customers": [],
            },
            {
                "start_time": datetime.strptime("16:30", "%H:%M").time(),
                "end_time": datetime.strptime("17:00", "%H:%M").time(),
                "plan_date": st.session_state.plan_date,
                "activity": "",
                "location": "",
                "num_customers": "",
                "customers": [],
            },
        ]

    if "needs_rerun" not in st.session_state:
        st.session_state.needs_rerun = False
    if "form_reset_needed" not in st.session_state:
        st.session_state.form_reset_needed = False


# ==========================================================
# PLACEHOLDER: SHEET CONNECTOR (Fill later, structure stays)
# ==========================================================
def connect_to_google_sheets():
    """
    TODO (later):
    - import gspread + Credentials
    - return gspread client
    """
    return None


def load_users_from_sheet():
    """
    TODO (later):
    - Read Users sheet
    - Return dict keyed by staff_id
    """
    # UI-only: fake users so you can test login
    return {
        "1001": {"staff_id": "1001", "username": "Demo User", "branch": "HO", "role": "rm", "allowed_sources": "all", "is_active": True},
        "admin": {"staff_id": "admin", "username": "Admin", "branch": "HO", "role": "admin", "allowed_sources": "all", "is_active": True},
    }


def append_user_to_sheet(new_user: dict) -> bool:
    """
    TODO (later):
    - Append to Users sheet
    """
    # UI-only: pretend success
    return True


def load_customer_data_for_user(user_data: dict) -> pd.DataFrame:
    """
    TODO (later):
    - Read retail_data from sheet
    - Apply filtering (allowed_sources, etc.)
    """
    # UI-only: return a small dummy dataset to render UI
    df = pd.DataFrame(
        [
            {"Sender_Name": "RM A", "Name": "Customer 1", "Tel": "012345678", "Bank": "ABC", "Business": "Shop", "Amount": "5000", "Potential_Level": "H", "Message_Date": "2026-02-20"},
            {"Sender_Name": "RM B", "Name": "Customer 2", "Tel": "098765432", "Bank": "XYZ", "Business": "Restaurant", "Amount": "8000", "Potential_Level": "M", "Message_Date": "2026-02-19"},
        ]
    )
    return df


# -------------------------
# AUTH LOGIC (UI-only)
# -------------------------
def authenticate_by_staff_id(staff_id: str):
    staff_id = str(staff_id).strip()
    users = load_users_from_sheet()
    u = users.get(staff_id)
    if not u:
        return None
    if str(u.get("is_active", True)).upper() != "TRUE" and u.get("is_active") is not True:
        return None
    return u


# -------------------------
# AUTH UI
# -------------------------
def render_logo_header():
    if logo_data:
        st.markdown(
            f"""
            <div style='display:flex; justify-content:center; align-items:center; margin-bottom:5px;'>
                <img src='data:image/png;base64,{logo_data}' width='120' alt='Bank Logo'>
            </div>
            """,
            unsafe_allow_html=True,
        )


def login_form():
    st.markdown(
        """
        <h3 style="color:#038C3E; margin-bottom:5px; font-size:18px;">CUSTOMER MANAGEMENT SYSTEM</h3>
        <p style="font-size:13px; color:#666; margin-bottom:20px; line-height:1.4;">
            Enter your Staff ID to access the system
        </p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        staff_id = st.text_input(
            "🆔 Staff ID",
            max_chars=50,
            placeholder="Enter your Staff ID (Demo: 1001 or admin)",
        )
        submitted = st.form_submit_button("Login →", use_container_width=True)

        if submitted:
            if not staff_id.strip():
                st.error("❌ Please enter your Staff ID")
                return

            user_data = authenticate_by_staff_id(staff_id)
            if not user_data:
                st.error("❌ Staff ID not found or inactive account")
                return

            st.success(f"✅ Welcome, {user_data.get('username','User')}!")
            st.session_state.logged_in = True
            st.session_state.user_data = user_data
            st.session_state.staff_id = str(staff_id).strip()

            # Load dummy customer data now (later replace with Google Sheet)
            st.session_state.customers = load_customer_data_for_user(user_data)

            st.rerun()


def register_form():
    st.markdown(
        """
        <div class="function-card">
            <h2 style="margin:0;">📝 Register New Account</h2>
            <p style="margin:6px 0 0 0; color:#666;">
                UI-only mode: Registration will show success, later we connect to Google Sheets.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("register_form", clear_on_submit=False):
        staff_id = st.text_input("🆔 Staff ID", max_chars=50, placeholder="e.g., 102938")
        username = st.text_input("👤 Username (Full Name)", max_chars=60, placeholder="e.g., Sok Dara")
        branch = st.text_input("🏢 Branch", max_chars=50, placeholder="e.g., Head Office")
        role = st.selectbox("🎭 Role", ["rm", "bm", "admin"], index=0)

        allowed_mode = st.selectbox("🔐 Allowed Sources", ["all", "custom"], index=0)
        allowed_sources = "all"
        if allowed_mode == "custom":
            allowed_list = st.multiselect(
                "Select sources",
                options=["Telegram", "Facebook", "Website", "Walk-in", "Referral"],
                default=["Telegram"],
            )
            allowed_sources = ",".join(allowed_list) if allowed_list else ""

        submitted = st.form_submit_button("✅ Create Account", use_container_width=True)

        if submitted:
            if not staff_id.strip() or not username.strip() or not branch.strip():
                st.error("❌ Staff ID, Username, and Branch are required")
                return

            new_user = {
                "staff_id": str(staff_id).strip(),
                "username": str(username).strip(),
                "branch": str(branch).strip(),
                "role": str(role).strip(),
                "allowed_sources": allowed_sources if allowed_sources else "all",
                "is_active": True,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            ok = append_user_to_sheet(new_user)
            if ok:
                st.success("✅ Account created (UI-only). Go to Login tab to sign in.")
            else:
                st.error("❌ Failed to create account (UI-only placeholder)")


# -------------------------
# Main UI (same structure)
# -------------------------
def render_app_header():
    header_col1, header_col2, header_col3 = st.columns([1, 3, 1])

    with header_col1:
        if logo_data:
            st.markdown(
                f"""
                <div style="background:white; padding:10px; border-radius:12px; 
                            box-shadow:0 2px 8px rgba(0,0,0,0.1); 
                            display:flex; align-items:center; justify-content:center;">
                    <img src="data:image/png;base64,{logo_data}" width="100" style="border-radius:8px;">
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background:#f0f0f0; padding:20px; border-radius:12px; 
                            text-align:center; color:#666;">
                    <p style="margin:0;">🏦<br>Logo</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with header_col2:
        st.markdown(
            """
            <div style="text-align:center; padding:15px;">
                <h1 style="color:#004A08; margin:0; font-size:2.2rem; font-weight:700;">
                    Customer Data Management and Analysis
                </h1>
                <p style="color:#2E8B57; margin:5px 0 0 0; font-size:1.1rem; font-weight:500;">
                    Performance & Execution Management System
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with header_col3:
        st.markdown("")


def tab_daily_planning():
    st.markdown(
        """
        <div class="function-card">
            <h2>📋 Daily Planning</h2>
            <p>Submit your daily plan (UI-only)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Header row
    c1, c2, c3 = st.columns([30, 6, 1])
    with c1:
        st.subheader("📅 Daily Planning")
    with c2:
        master_plan_date = st.date_input(
            "Plan Date",
            value=st.session_state.plan_date,
            key="master_plan_date",
            label_visibility="collapsed",
        )
        if master_plan_date != st.session_state.plan_date:
            st.session_state.plan_date = master_plan_date
            for task in st.session_state.tasks:
                task["plan_date"] = master_plan_date

    with c3:
        if st.button("➕", help="Add New Task", use_container_width=False):
            last_end_time = st.session_state.tasks[-1]["end_time"]
            new_start_time = last_end_time
            last_end_datetime = datetime.combine(st.session_state.plan_date, last_end_time)
            new_end_datetime = last_end_datetime + timedelta(hours=1)
            new_end_time = new_end_datetime.time()
            st.session_state.tasks.append(
                {
                    "start_time": new_start_time,
                    "end_time": new_end_time,
                    "plan_date": st.session_state.plan_date,
                    "activity": "",
                    "location": "",
                    "num_customers": "",
                    "customers": [],
                }
            )
            st.session_state.needs_rerun = True
            st.rerun()

    # Task rows
    for i, task in enumerate(st.session_state.tasks):
        time_col1, time_col2, time_col4, time_col6, time_col7 = st.columns([1, 1, 2, 2, 1])

        with time_col1:
            start_input = st.text_input(
                f"🕐 Start Time {i+1}",
                value=task["start_time"].strftime("%H:%M"),
                key=f"start_{i}",
            )
            try:
                if start_input:
                    if len(start_input.split(":")[0]) == 1:
                        start_input = "0" + start_input
                    st.session_state.tasks[i]["start_time"] = datetime.strptime(start_input, "%H:%M").time()
            except:
                pass

        with time_col2:
            end_input = st.text_input(
                f"🕔 End Time {i+1}",
                value=task["end_time"].strftime("%H:%M"),
                key=f"end_{i}",
            )
            try:
                if end_input:
                    if len(end_input.split(":")[0]) == 1:
                        end_input = "0" + end_input
                    st.session_state.tasks[i]["end_time"] = datetime.strptime(end_input, "%H:%M").time()
            except:
                pass

        with time_col4:
            activity = st.text_input(
                f"📝 Activity {i+1}",
                value=task["activity"],
                key=f"activity_{i}",
            )
            st.session_state.tasks[i]["activity"] = activity

        with time_col6:
            location = st.text_input(
                f"🎯 Location {i+1}",
                value=task["location"],
                key=f"location_{i}",
            )
            st.session_state.tasks[i]["location"] = location

        with time_col7:
            num_customers = st.text_input(
                f"👥 Number Cus {i+1}",
                value=task["num_customers"],
                key=f"num_customers_{i}",
            )
            st.session_state.tasks[i]["num_customers"] = num_customers

    st.markdown("---")
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        if st.button("🚀 Submit Daily Plan", use_container_width=True, type="primary"):
            st.success("✅ Submitted (UI-only). Later we will write to Google Sheets.")
            st.info("Next step later: replace submit handler with append_rows to sheet 'plan'.")


def tab_market_visit_customer():
    st.markdown(
        """
        <div class="function-card">
            <h2>👥 Customer Portfolio Presentation</h2>
            <p>UI-only mode (shows dummy / cached data)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = st.session_state.get("customers", pd.DataFrame())
    if df is None or df.empty:
        st.warning("No customer data (UI-only).")
        st.info("Later: load from Google Sheets and store into st.session_state.customers")
        return

    st.markdown(f"### 👥 Showing {len(df)} Customers")
    st.dataframe(df, use_container_width=True)


def tab_customer_analysis_dashboard():
    st.markdown(
        """
        <div class="function-card">
            <h2>🌍 Customer Analysis Dashboard</h2>
            <p>UI-only mode</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = st.session_state.get("customers", pd.DataFrame())
    if df is None or df.empty:
        st.warning("No data for analysis (UI-only).")
        return

    # Simple example chart
    if "Potential_Level" in df.columns:
        counts = df["Potential_Level"].value_counts().reset_index()
        counts.columns = ["Potential_Level", "Count"]
        st.bar_chart(counts.set_index("Potential_Level"))


# -------------------------
# MAIN
# -------------------------
def main():
    init_session_state()

    # AUTH GATE
    if not st.session_state.get("logged_in", False):
        tab_login, tab_register = st.tabs(["🔒 Login", "📝 Register"])
        with tab_login:
            render_logo_header()
            login_form()
        with tab_register:
            render_logo_header()
            register_form()
        st.stop()

    # APP HEADER
    render_app_header()

    # MAIN TABS (same structure)
    tab1, tab2, tab3 = st.tabs(["📋 Daily Planning", "📍 Market Visit Customer", "🌍 Customer Analysis Dashboard"])
    with tab1:
        tab_daily_planning()
    with tab2:
        tab_market_visit_customer()
    with tab3:
        tab_customer_analysis_dashboard()

    # Logout
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user_data = {}
        st.session_state.staff_id = ""
        st.session_state.customers = pd.DataFrame()
        st.rerun()


if __name__ == "__main__":
    main()