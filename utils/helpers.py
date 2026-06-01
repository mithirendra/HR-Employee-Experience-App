# data loading with caching, shared functions
# ── utils/helpers.py ──────────────────────────────────────────────────────────
# Shared data loading and utility functions for the Vibe app.
# All pages import from here — data is loaded once and cached.

import os
import pandas as pd
import streamlit as st
import base64
from datetime import datetime

# Global today reference — used across all pages for consistent filtering
TODAY        = pd.Timestamp.today().normalize()
CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().strftime("%b")

# ── File paths ────────────────────────────────────────────────────────────────
# Builds paths to each CSV relative to this file's location.
# Works whether you run the app from the project root or a subdirectory.
BASE_DIR   = os.path.dirname(os.path.dirname(__file__))  # project root
DATA_DIR   = os.path.join(BASE_DIR, "data")

# ── Data loaders ──────────────────────────────────────────────────────────────
# @st.cache_data tells Streamlit to load this data once and keep it in memory.
# The function only re-runs if the CSV file changes.
# This is what keeps page navigation fast despite 26,000 pulse rows.

@st.cache_data
def load_employees():
    """Load and return the employee master list."""
    path = os.path.join(DATA_DIR, "employees.csv")
    df   = pd.read_csv(path)
    return df

@st.cache_data
def load_pulse():
    """Load and return the pulse responses dataset."""
    path = os.path.join(DATA_DIR, "pulse_responses.csv")
    df   = pd.read_csv(path, parse_dates=["week_date"])
    # Add a year and month column for easier filtering later
    df["year"]  = df["week_date"].dt.year
    df["month"] = df["week_date"].dt.month
    return df

@st.cache_data
def load_activities():
    """Load and return the activities dataset."""
    path = os.path.join(DATA_DIR, "activities.csv")
    df   = pd.read_csv(path, parse_dates=["date"])
    return df

@st.cache_data
def load_kudos():
    """Load and return the Kudos dataset."""
    path = os.path.join(DATA_DIR, "kudos.csv")
    df   = pd.read_csv(path, parse_dates=["date"])
    return df

# ── Role-based data filters ───────────────────────────────────────────────────
# These functions take a full DataFrame and filter it down to what each
# role is allowed to see. Called on every page before rendering.

def filter_pulse_by_role(df_pulse, role, emp_id=None, manager_name=None):
    """
    Filter pulse data based on the logged-in user's role.
    - Employee : sees only their own rows
    - Manager  : sees only their direct reports
    - HR       : sees everything
    """
    if role == "HR":
        return df_pulse                          # HR sees all rows unfiltered

    elif role == "Manager":
        if manager_name:
            # Return all employees whose manager matches this manager's name
            return df_pulse[df_pulse["manager"] == manager_name]
        return df_pulse

    elif role == "Employee":
        if emp_id:
            # Return only this employee's own rows
            return df_pulse[df_pulse["employee_id"] == emp_id]
        return df_pulse

    return df_pulse

def filter_kudos_by_role(df_kudos, role, emp_id=None, manager_name=None,
                          df_employees=None):
    """
    Filter Kudos data based on role.
    - Employee : sees only Kudos they gave or received
    - Manager  : sees Kudos involving their team members
    - HR       : sees everything
    """
    if role == "HR":
        return df_kudos

    elif role == "Manager" and manager_name and df_employees is not None:
        # Get list of employee IDs under this manager
        team_ids = df_employees[
            df_employees["manager"] == manager_name
        ]["employee_id"].tolist()
        # Return Kudos where giver or recipient is on the team
        return df_kudos[
            (df_kudos["giver_id"].isin(team_ids)) |
            (df_kudos["recipient_id"].isin(team_ids))
        ]

    elif role == "Employee" and emp_id:
        # Return only Kudos this employee gave or received
        return df_kudos[
            (df_kudos["giver_id"]    == emp_id) |
            (df_kudos["recipient_id"] == emp_id)
        ]

    return df_kudos

# ── Metric helpers ────────────────────────────────────────────────────────────
# Small utility functions used across multiple pages.

def engagement_color(score):
    """
    Return a hex colour based on an engagement score.
    Used for metric cards, badges, and conditional formatting.
    Green = engaged, orange = neutral, red = at risk.
    """
    if score >= 70:
        return "#4caf7d"    # green — engaged
    elif score >= 45:
        return "#f49052"    # orange — neutral
    else:
        return "#E24B4A"    # red — at risk

def engagement_label(score):
    """Return Engaged / Neutral / At Risk label from a composite score."""
    if score >= 70:
        return "Engaged"
    elif score >= 45:
        return "Neutral"
    else:
        return "At Risk"

def format_delta(value, inverse=False):
    """
    Format a delta value with an arrow and sign.
    inverse=True means a higher number is bad (e.g. absenteeism).
    Returns a string like '▲ +3.2' or '▼ -1.5'.
    """
    if value > 0:
        arrow = "▲" if not inverse else "▼"
        return f"{arrow} +{value:.1f}"
    elif value < 0:
        arrow = "▼" if not inverse else "▲"
        return f"{arrow} {value:.1f}"
    else:
        return "→ No change"

# ── Session state helpers ─────────────────────────────────────────────────────
# Convenience functions for reading session state safely.
# Returns None if the key hasn't been set yet rather than throwing an error.

def get_role():
    """Return the current user's role from session state."""
    return st.session_state.get("role", None)

def get_emp_id():
    """Return the current user's employee ID from session state."""
    return st.session_state.get("emp_id", None)

def get_manager_name():
    """Return the current user's manager name from session state."""
    return st.session_state.get("manager_name", None)

def is_logged_in():
    """Return True if the user has completed the login screen."""
    return st.session_state.get("role", None) is not None

def apply_vibe_style():
    """Apply Mitma Consulting brand styles to any Vibe page."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

        /* ── Hidden chrome ───────────────────────────────────────────────── */
        #MainMenu                               { visibility: hidden; }
        footer                                  { visibility: hidden; }
        header                                  { visibility: hidden; }
        [data-testid="stSidebarNav"]            { display: none; }
        [data-testid="stSidebarCollapseButton"] { display: none; }

        /* ── Global font ─────────────────────────────────────────────────── */
        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif;
        }

        /* ── App background ──────────────────────────────────────────────── */
        .stApp {
            background-color: #fffbf8;
        }

        /* ── Sidebar ─────────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background-color: #ffece1;
        }

        /* ── Metric cards ────────────────────────────────────────────────── */
        [data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #f0d9cc;
            border-radius: 12px;
            padding: 20px;
        }

        /* ── Buttons ─────────────────────────────────────────────────────── */
        /* Target every layer Streamlit wraps around button text            */
        .stButton > button,
        .stButton > button:focus,
        div[data-testid="stButton"] > button {
            background-color: #f49052 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 500 !important;
            width: 100% !important;
        }

        /* Streamlit wraps button label in a <p> tag — target it directly   */
        .stButton > button p,
        div[data-testid="stButton"] > button p {
            color: #ffffff !important;
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 500 !important;
        }

        /* Hover state — change background and keep text white              */
        .stButton > button:hover,
        div[data-testid="stButton"] > button:hover {
            background-color: #505050 !important;
            color: #ffffff !important;
        }

        .stButton > button:hover p,
        div[data-testid="stButton"] > button:hover p {
            color: #ffffff !important;
        }
        
        /* ── Link buttons ────────────────────────────────────────────────────── */
        [data-testid="stLinkButton"] a {
            background-color: #505050 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 500 !important;
        }

        [data-testid="stLinkButton"] a:hover {
            background-color: #f49052 !important;
            color: #ffffff !important;
        }

        [data-testid="stLinkButton"] a p {
            color: #ffffff !important;
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 500 !important;
        }

        /* ── Input fields ────────────────────────────────────────────────── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            background-color: #ffece1 !important;
            border: 1px solid #f0d9cc !important;
            border-radius: 8px !important;
            font-family: 'Montserrat', sans-serif !important;
        }

        /* ── Headings ────────────────────────────────────────────────────── */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Montserrat', sans-serif !important;
            color: #000000 !important;
            font-weight: 600 !important;
        }

        /* ── Body text ───────────────────────────────────────────────────── */
        p, div, span {
            font-family: 'Montserrat', sans-serif;
            color: #505050;
        }

        /* ── Tabs ────────────────────────────────────────────────────────── */
        [data-testid="stTabs"] button {
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 500 !important;
        }
        [data-testid="stTabs"] button[aria-selected="true"] {
            color: #f49052 !important;
            border-bottom-color: #f49052 !important;
        }

        /* ── Divider ─────────────────────────────────────────────────────── */
        hr {
            border-color: #f0d9cc !important;
        }

        /* ── Scrollbar ───────────────────────────────────────────────────── */
        ::-webkit-scrollbar       { width: 6px; }
        ::-webkit-scrollbar-track { background: #fffbf8; }
        ::-webkit-scrollbar-thumb { background: #f0d9cc; border-radius: 3px; }

    </style>
    """, unsafe_allow_html=True)

def get_logo_base64():
    """Load Mitma logo as base64 for embedding in HTML."""
    # Build path to assets/mitma_logo.png from the project root
    logo_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "assets", "mitma_logo_color.png"
    )
    try:
        # Open the file in binary mode and encode to base64
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        # Return None if file not found — caller falls back to emoji
        return None

def show_sidebar():
    """Render the Vibe sidebar navigation — call on every page."""
    
    role     = get_role()
    emp_name = st.session_state.get("emp_name", "")
    dept     = st.session_state.get("department", "")

    # Role badge colours
    role_colors = {
        "Employee": ("#E1F5EE", "#085041"),
        "Manager":  ("#E6F1FB", "#0C447C"),
        "HR":       ("#FAECE7", "#712B13"),
    }
    bg, fg = role_colors.get(role, ("#eee", "#333"))

    # Load logo
    logo_b64  = get_logo_base64()
    logo_html = (
        f"<img src='data:image/png;base64,{logo_b64}' "
        f"style='height:36px; margin-bottom:8px;'>"
        if logo_b64 else "🔵"
    )

    with st.sidebar:

        # ── Logo and branding ─────────────────────────────────────────────
        st.markdown(f"""
        <div style='text-align:center; margin-bottom:32px;'>
                    {logo_html}
            <div style='font-size:28px; font-weight:600;
                        color:#000000; margin-top:8px;
                        font-family:Montserrat,sans-serif;'>VIBE</div>
            <div style='font-size:13px; color:#a07050;
                        margin-top:4px;
                        font-family:Montserrat,sans-serif;'>
                EMPLOYEE EXPERIENCE PLATFORM
            </div>
            <div style='font-size:11px; color:#c0a080;
                        margin-top:2px;
                        font-family:Montserrat,sans-serif;'>
                By Mitma Consulting
            </div>
            <div style='display:inline-block; margin-top:8px;
                    font-size:9px; font-weight:600;
                    background:#f49052; color:#fff;
                    padding:2px 8px; border-radius:4px;
                    letter-spacing:.06em;'>
                DEMO VERSION
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── User info and role badge ───────────────────────────────────────
        st.markdown(f"""
        <div style='margin-bottom:12px;'>
            <div style='font-size:13px; font-weight:500;
                        color:#000000;'>{emp_name}</div>
            <div style='font-size:11px; color:#a07050;
                        margin-top:2px;'>{dept}</div>
            <span style='font-size:10px; font-weight:500;
                         background:{bg}; color:{fg};
                         padding:2px 8px; border-radius:10px;
                         display:inline-block;
                         margin-top:6px;'>{role}</span>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Navigation links ──────────────────────────────────────────────
        st.markdown("**Navigate**")
        st.page_link("app.py",                  label="🏠  Home")
        st.page_link("pages/1_Pulse_Survey.py", label="📊  Pulse Survey")
        st.page_link("pages/2_Wellbeing.py",    label="💚  Wellbeing")
        st.page_link("pages/3_Activities.py",   label="🎯  Activities")
        st.page_link("pages/4_Rewards.py",      label="🎁  Rewards")
        st.page_link("pages/5_Kudos.py",        label="⭐  Kudos")
        st.page_link("pages/6_Connect.py",      label="📣  Connect")

        st.divider()

         # ── Contact links ─────────────────────────────────────────────────────
        st.markdown("""
        <div style='font-size:12px; color:#9a8880;
                    text-align:center; margin-top:16px;
                    margin-bottom:16px; line-height:1.6;'>
            This app is a <strong>DEMO VERSION</strong> with limited views.
            <br><br>
            Contact Mitma Consulting to get access to the
            <strong>FULL VERSION</strong>.
        </div>
        """, unsafe_allow_html=True)
        st.link_button(
            "Contact Mitma Consulting →",
            "https://mitmaconsulting.framer.ai/contact",
            use_container_width=True
        )
        st.link_button(
            "Connect on LinkedIn →",
            "https://www.linkedin.com/in/mithirendra-maniam/",
            use_container_width=True
        )
        st.divider()

        # ── Sign out ──────────────────────────────────────────────────────
        if st.button("Sign out"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("app.py")


def show_footer():
    """Render Vibe footer with copyright."""
    st.markdown("""
    <div style='text-align:center; padding:20px 0 10px;
                font-size:11px; color:#c0a080;
                border-top:0.5px solid #f0d0b8;
                margin-top:40px;'>
        © 2026 Mitma Consulting · Vibe Employee Experience Platform Demo Version 0·
        Built by Mithirendra Maniam
    </div>
    """, unsafe_allow_html=True)
