# data loading with caching, shared functions
# ── utils/helpers.py ──────────────────────────────────────────────────────────
# Shared data loading and utility functions for the Vibe app.
# All pages import from here — data is loaded once and cached.

import os
import pandas as pd
import streamlit as st

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
    """Apply Vibe warm palette CSS to any page."""
    st.markdown("""
    <style>
        #MainMenu  {visibility: hidden;}
        footer     {visibility: hidden;}
        header     {visibility: hidden;}
        [data-testid="stSidebarNav"] {display: none;}
        .stApp     {background-color: #fffbf8;}
        [data-testid="stSidebar"] {background-color: #fff3ea;}
        [data-testid="stMetric"]  {
            background-color: #ffece1;
            border-radius: 10px;
            padding: 12px;
        }
        .stButton > button {
            background-color: #f49052;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 500;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #e07840;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

def show_footer():
    """Render Vibe footer with copyright."""
    st.markdown("""
    <div style='text-align:center; padding:20px 0 10px;
                font-size:11px; color:#c0a080;
                border-top:0.5px solid #f0d0b8;
                margin-top:40px;'>
        © 2026 Mitma Consulting · Vibe Employee Experience Platform Version 0·
        Built by Mithirendra Maniam
    </div>
    """, unsafe_allow_html=True)