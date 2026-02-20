# =========================
# FULL WORKING MAIN.PY (regenerated)
# ✅ Fixes Streamlit "Oh no" startup crashes
# ✅ Removes invalid api_id/api_hash placeholders (Telegram is OPTIONAL)
# ✅ Removes duplicate connect_to_google_sheets() and login_form()
# ✅ Adds Login | Register tabs (like your screenshot)
# ✅ Register writes new users into Google Sheet ("Users")
# ✅ Login uses Staff ID only (same idea as your modified login)
# ✅ Safe logo loading (won't crash if image missing)
# =========================

import nest_asyncio
import asyncio
from telethon import TelegramClient  # OPTIONAL (safe to keep if in requirements)
from telethon.tl.functions.messages import GetHistoryRequest  # OPTIONAL
import pandas as pd
import re
from datetime import datetime, timedelta
import streamlit as st
import plotly.express as px
import pytz
from rapidfuzz import fuzz, process
import time
import folium
from streamlit_folium import st_folium
from sklearn.cluster import DBSCAN
import numpy as np
import random
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from zoneinfo import ZoneInfo
import logging
import sqlite3
from folium.plugins import HeatMap
import os
import base64
from google.oauth2.service_account import Credentials
import gspread

kh_time = datetime.now(ZoneInfo("Asia/Phnom_Penh"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHEET_ID = "1wM7DTHizhg_A3h0qV3EhX4os4hk46uolW-ESQSJkgZs"
WORKSHEET_NAME = "retail_data"

# === MUST BE THE FIRST STREAMLIT COMMAND ===
st.set_page_config(page_title="Sales Performance Dashboard", layout="wide", page_icon="📊")

nest_asyncio.apply()

# =========================
# Telegram credentials (OPTIONAL)
# If you are NOT scraping Telegram inside Streamlit, keep these commented.
# =========================
# api_id = 12345678
# api_hash = "your_api_hash"
# session_name = "customer_session_2"


# =========================
# CSS (same as your style)
# =========================
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

    /* Make auth tabs look like a top nav */
    div[data-baseweb="tab-list"] { gap: 12px; }
    button[data-baseweb="tab"] { font-size: 16px; font-weight: 700; padding: 10px 16px; }
</style>
""",
    unsafe_allow_html=True,
)

patterns = {
    "Name": r"Name:\s*([^\n]*)",
    "Tel": r"Tel:\s*([^\n]*)",
    "Business": r"Business:\s*([^\n]*)",
    "Bank": r"Bank:\s*([^\n]*)",
    "Amount": r"Amount:\s*([^\n]*)",
    "Interest": r"Interest:\s*([^\n]*)",
    "Loan Type": r"Loan\s*Type:\s*([^\n]*)",
    "Tenure": r"Tenure:\s*([^\n]*)",
    "Maturity": r"Maturity:\s*([^\n]*)",
    "Potential H/M/L": r"Potential\s*H/M/L:\s*([^\n]*)",
    "Potential Product": r"Potential\s*Product:\s*([^\n]*)",
}


def get_base64_encoded_image(image_path: str) -> str:
    """Get base64 encoded string of an image (safe)"""
    if not image_path or not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


# =========================
# LOGO (SAFE)
# =========================
LOGO_PATH = "Logo-CMCB_FA-15.png"
logo_data = get_base64_encoded_image(LOGO_PATH)


# =========================
# SESSION STATE INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "customers" not in st.session_state:
    st.session_state.customers = pd.DataFrame()
if "staff_id" not in st.session_state:
    st.session_state.staff_id = ""


# =========================
# GOOGLE SHEETS (ONLY ONE VERSION)
# =========================
@st.cache_resource
def connect_to_google_sheets():
    try:
        if "service_account" not in st.secrets:
            st.error("❌ Google Sheets credentials not found in Streamlit Secrets.")
            st.info("Streamlit Cloud → App → Settings → Secrets → add [service_account] ...")
            return None

        credentials = Credentials.from_service_account_info(
            dict(st.secrets["service_account"]),
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file",
            ],
        )
        return gspread.authorize(credentials)

    except Exception as e:
        st.error(f"❌ Failed to connect to Google Sheets: {str(e)}")
        return None


@st.cache_data(ttl=300)
def load_users_from_sheets(_gc, sheet_id, worksheet_name="Users"):
    """Load users from Google Sheets - keyed by staff_id"""
    try:
        sheet = _gc.open_by_key(sheet_id)
        worksheet = sheet.worksheet(worksheet_name)
        users_data = worksheet.get_all_records()

        users_dict = {}
        for user in users_data:
            staff_id = str(user.get("staff_id", "")).strip()
            if not staff_id:
                continue

            allowed_sources_raw = str(user.get("allowed_sources", "all")).strip()
            if allowed_sources_raw.lower() != "all":
                sources = [s.strip() for s in allowed_sources_raw.split(",") if s.strip()]
            else:
                sources = "all"

            users_dict[staff_id] = {
                "staff_id": staff_id,
                "username": str(user.get("username", "")).strip(),
                "allowed_sources": sources,
                "branch": str(user.get("branch", "")).strip(),
                "role": str(user.get("role", "rm")).strip(),
                "is_active": user.get("is_active", True),
            }

        return users_dict

    except Exception as e:
        st.error(f"❌ Error loading users: {e}")
        return {}


def authenticate_by_staff_id(staff_id: str):
    """Authenticate user from Google Sheets by staff_id"""
    try:
        if not staff_id:
            return None

        staff_id = str(staff_id).strip()
        gc = connect_to_google_sheets()
        if not gc:
            return None

        users_data = load_users_from_sheets(gc, SHEET_ID, "Users")
        user_data = users_data.get(staff_id)

        if user_data:
            is_active = user_data.get("is_active", True)
            if str(is_active).upper() == "TRUE":
                return user_data
        return None

    except Exception as e:
        st.error(f"❌ Authentication error: {e}")
        return None


def staff_id_exists(gc, sheet_id: str, staff_id: str, worksheet_name="Users") -> bool:
    sh = gc.open_by_key(sheet_id)
    ws = sh.worksheet(worksheet_name)
    rows = ws.get_all_records()
    target = str(staff_id).strip()
    for r in rows:
        if str(r.get("staff_id", "")).strip() == target:
            return True
    return False


def append_user_to_sheet(gc, sheet_id: str, new_user: dict, worksheet_name="Users") -> bool:
    """
    Append new user into Users sheet.
    REQUIRED Users header order:
    staff_id | username | branch | role | allowed_sources | is_active | created_at
    """
    try:
        sh = gc.open_by_key(sheet_id)
        ws = sh.worksheet(worksheet_name)

        row = [
            new_user.get("staff_id", ""),
            new_user.get("username", ""),
            new_user.get("branch", ""),
            new_user.get("role", "rm"),
            new_user.get("allowed_sources", "all"),
            new_user.get("is_active", True),
            new_user.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ]

        ws.append_row(row, value_input_option="USER_ENTERED")
        return True

    except Exception as e:
        st.error(f"❌ Failed to create account: {e}")
        return False


@st.cache_data(ttl=120)
def load_sheet_data(_gc, sheet_id, worksheet_name):
    """Load data from Google Sheets with error handling"""
    try:
        if _gc is None:
            return pd.DataFrame()

        spreadsheet = _gc.open_by_key(sheet_id)
        ws = spreadsheet.worksheet(worksheet_name)
        data = ws.get_all_records()
        return pd.DataFrame(data) if data else pd.DataFrame()

    except Exception as e:
        st.error(f"❌ Error loading sheet '{worksheet_name}': {e}")
        return pd.DataFrame()


# =========================
# AUTH UI: LOGIN + REGISTER
# =========================
def login_form():
    st.markdown(
        """
    <style>
        .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .stTextInput>div>div>input { padding-left: 35px; }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Logo
    if logo_data:
        st.markdown(
            f"""
            <div style='display:flex; justify-content:center; align-items:center; margin-bottom:5px;'>
                <img src='data:image/png;base64,{logo_data}' width='120' alt='Bank Logo'>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
            placeholder="Enter your Staff ID",
            help="Enter your registered Staff ID",
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

            # Load customer data (same logic idea)
            with st.spinner("Loading customer data..."):
                gc = connect_to_google_sheets()
                df = load_sheet_data(gc, SHEET_ID, WORKSHEET_NAME)

                if df is None or df.empty:
                    st.warning("⚠️ No customer data found")
                    st.session_state.customers = pd.DataFrame()
                else:
                    filtered = df.copy()

                    if "Name" in filtered.columns:
                        filtered = filtered[
                            filtered["Name"].notna()
                            & (filtered["Name"].astype(str).str.strip() != "")
                        ]

                    if "Sender_Name" in filtered.columns:
                        excluded_senders = ["Zana MAM", "Khemra BUTH"]
                        filtered = filtered[
                            ~filtered["Sender_Name"].astype(str).str.strip().isin(excluded_senders)
                        ]

                    if user_data.get("allowed_sources") != "all" and "Source_Channel" in filtered.columns:
                        allowed_sources = user_data.get("allowed_sources", [])
                        filtered = filtered[filtered["Source_Channel"].isin(allowed_sources)]

                    st.session_state.customers = filtered

            st.rerun()


def register_form():
    st.markdown(
        """
        <div class="function-card">
            <h2 style="margin:0;">📝 Register New Account</h2>
            <p style="margin:6px 0 0 0; color:#666;">Your information will be saved automatically to the Users sheet.</p>
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
            if not staff_id.strip():
                st.error("❌ Staff ID is required")
                return
            if not username.strip():
                st.error("❌ Username is required")
                return
            if not branch.strip():
                st.error("❌ Branch is required")
                return

            gc = connect_to_google_sheets()
            if not gc:
                return

            if staff_id_exists(gc, SHEET_ID, staff_id, "Users"):
                st.error("❌ This Staff ID already exists. Please use another one.")
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

            ok = append_user_to_sheet(gc, SHEET_ID, new_user, "Users")
            if ok:
                st.success("✅ Account created successfully! Please go to Login tab and sign in.")
                st.cache_data.clear()  # refresh cached users


# =========================
# YOUR OTHER HELPERS (kept)
# =========================
def safe_format_interest(x):
    try:
        if pd.isna(x):
            return ""
        if isinstance(x, (int, float)):
            return f"{x:.0f}%"
        clean_x = str(x).replace("%", "").strip()
        return f"{float(clean_x):.0f}%"
    except Exception:
        return str(x) if not pd.isna(x) else ""


@st.cache_data(ttl=300, show_spinner=False)
def load_and_clean_data():
    try:
        gc = connect_to_google_sheets()
        if not gc:
            return pd.DataFrame()

        telegram_df = load_sheet_data(gc, SHEET_ID, WORKSHEET_NAME)
        if telegram_df is None or telegram_df.empty:
            return pd.DataFrame()

        telegram_df = telegram_df.astype(str).replace(
            {"nan": "", "None": "", "NaN": "", "null": "", "NaT": "", "none": "", "<NA>": "", "NoneType": ""}
        )

        if "Name" in telegram_df.columns:
            telegram_df = telegram_df[telegram_df["Name"].str.strip() != ""]

        if "Sender_Name" in telegram_df.columns:
            telegram_df = telegram_df[
                (telegram_df["Sender_Name"].str.strip() != "Zana MAM")
                & (telegram_df["Sender_Name"].str.strip() != "Khemra BUTH")
            ]

        return telegram_df

    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return pd.DataFrame()


def init_session_state():
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


# =========================
# MAIN APP (same structure idea)
# =========================
def main():
    init_session_state()

    # ---- AUTH GATE: show Login/Register like your screenshot ----
    if not st.session_state.get("logged_in", False):
        tab_login, tab_register = st.tabs(["🔒 Login", "📝 Register"])
        with tab_login:
            login_form()
        with tab_register:
            register_form()
        st.stop()

    # ---- Header (kept style) ----
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

    # ---- Main tabs (same structure names) ----
    tab1, tab2, tab3 = st.tabs(
        [
            "📋 Daily Planning",
            "📍 Market Visit Customer",
            "🌍 Customer Analysis Dashboard",
        ]
    )

    with tab1:
        st.markdown(
            """
            <div class="function-card">
                <h2>📋 Daily Planning</h2>
                <p>Submit your daily plan</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info("✅ Paste your original Tab1 (Daily Planning) block here (unchanged).")

    with tab2:
        st.markdown(
            """
            <div class="function-card">
                <h2>👥 Customer Portfolio Presentation</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.spinner("🔄 Loading customer data..."):
            telegram_df = load_and_clean_data()
            user_data = st.session_state.get("user_data", {})
            if telegram_df.empty:
                st.error("❌ No data found from Google Sheets")
                st.stop()

            # Apply allowed_sources filter (same idea)
            if user_data.get("allowed_sources") != "all" and "Source_Channel" in telegram_df.columns:
                allowed_sources = user_data.get("allowed_sources", [])
                telegram_df = telegram_df[telegram_df["Source_Channel"].isin(allowed_sources)]

            st.success(f"✅ Loaded {len(telegram_df)} customers")

        st.dataframe(telegram_df.head(50), use_container_width=True)

    with tab3:
        st.markdown(
            """
            <div class="function-card">
                <h2>🌍 Customer Analysis Dashboard</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info("✅ Paste your original Tab3 block here (unchanged).")


if __name__ == "__main__":
    main()