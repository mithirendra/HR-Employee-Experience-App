# ── pages/3_Activities.py ─────────────────────────────────────────────────────
# Vibe — Activities + Participation module
# Employee : upcoming activities, register, points ledger, leaderboard
# Manager  : team participation tracker, upcoming activities
# HR       : org-wide participation dashboard, full leaderboard

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.helpers import (
    load_employees, load_pulse, load_kudos, load_activities,
    filter_pulse_by_role, filter_kudos_by_role,
    engagement_color, format_delta,
    is_logged_in, get_role, get_emp_id, get_manager_name,
    apply_vibe_style, show_footer, show_sidebar,
)

# ── Guard ─────────────────────────────────────────────────────────────────────
if not is_logged_in():
    st.warning("Session expired. Please log in again.")
    if st.button("Go to login"):
        st.switch_page("app.py")
    st.stop()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Activities — VIBE Demo | Mitma Consulting",
    page_icon  = "assets/mitma_favicon.png",
    layout     = "wide",
)
apply_vibe_style()

# ── Sidebar ───────────────────────────────────────────────────────────────────
role     = get_role()
emp_name = st.session_state.get("emp_name", "")
dept     = st.session_state.get("department", "")

role_colors = {
    "Employee": ("#E1F5EE", "#085041"),
    "Manager":  ("#E6F1FB", "#0C447C"),
    "HR":       ("#FAECE7", "#712B13"),
}
bg, fg = role_colors.get(role, ("#eee", "#333"))

show_sidebar()

# ── Date references ───────────────────────────────────────────────────────────
TODAY        = pd.Timestamp.today().normalize()
CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().strftime("%b")

# ── Load data ─────────────────────────────────────────────────────────────────
emp_id   = get_emp_id()
mgr_name = get_manager_name()

df_employees  = load_employees()
df_pulse      = load_pulse()
df_kudos      = load_kudos()
df_activities = load_activities()

# ── Points calculation helper ─────────────────────────────────────────────────
# Calculates total points for an employee from all earning sources:
# Pulse submissions (20 pts each) + Kudos given (10 pts) +
# Kudos received (15 pts)
# Activity attendance points handled separately via session state

def calculate_points(employee_id):
    """Calculate total points earned by an employee across all modules."""

    # Points from pulse submissions — 20 pts per submission
    pulse_count   = len(df_pulse[df_pulse["employee_id"] == employee_id])
    pulse_points  = pulse_count * 20

    # Points from Kudos given — 10 pts per Kudos given
    kudos_given   = len(df_kudos[df_kudos["giver_id"] == employee_id])
    given_points  = kudos_given * 10

    # Points from Kudos received — 15 pts per Kudos received
    kudos_received   = len(df_kudos[df_kudos["recipient_id"] == employee_id])
    received_points  = kudos_received * 15

    # Session state points — from activity registrations and check-ins
    # these are tracked in memory during the demo session
    session_points = st.session_state.get(f"activity_pts_{employee_id}", 0)

    total = pulse_points + given_points + received_points + session_points
    return {
        "pulse":    pulse_points,
        "given":    given_points,
        "received": received_points,
        "session":  session_points,
        "total":    total,
    }

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("## 🎯 Activities")
st.markdown("---")

# ── Route by role ─────────────────────────────────────────────────────────────
if role == "Employee":

    # ── Employee activities view ──────────────────────────────────────────────
    points = calculate_points(emp_id)

    # ── Hero banner ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:#f49052; border-radius:12px;
                padding:20px 24px; margin-bottom:20px;
                display:flex; align-items:center;
                justify-content:space-between;'>
        <div>
            <div style='font-size:11px; color:#fff3ea;
                        text-transform:uppercase;
                        letter-spacing:.07em;'>
                Activities + Points · Jan — {CURRENT_MONTH} {CURRENT_YEAR}
            </div>
            <div style='font-size:26px; font-weight:500;
                        color:#fff; margin:4px 0;'>{emp_name}</div>
            <div style='font-size:12px; color:#fff3ea;'>
                Earn points by participating in activities,
                submitting pulses, and giving Kudos
            </div>
        </div>
        <div style='text-align:center;'>
            <div style='font-size:48px; font-weight:500;
                        color:#fff; line-height:1;'>
                {points["total"]:,}
            </div>
            <div style='font-size:11px; color:#fff3ea;
                        margin-top:4px;'>Total points</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Activities taken part — registered and checked in
    registered_count = sum(
        1 for key in st.session_state
        if key.startswith(f"registered_{emp_id}_")
        and st.session_state[key]
    )
    checkedin_count = sum(
        1 for key in st.session_state
        if key.startswith(f"checkedin_{emp_id}_")
        and st.session_state[key]
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Activities registered", registered_count)
        st.caption("This session")
    with k2:
        st.metric("Activities attended",   checkedin_count)
        st.caption("Checked in this session")
    with k3:
        st.metric("Activity points",       f"{points['session']:,}")
        st.caption("From registrations and check-ins")
    with k4:
        st.metric("Total points",          f"{points['total']:,}")
        st.caption(f"Jan — {CURRENT_MONTH} {CURRENT_YEAR}")

    st.markdown("---")

    # ── Upcoming activities ───────────────────────────────────────────────────
    st.markdown("##### Upcoming activities")

    # Show activities relevant to this employee's department or org-wide
    upcoming = df_activities[
        (df_activities["date"] >= TODAY) &
        (
            (df_activities["department_target"] == "All") |
            (df_activities["department_target"] == dept)
        )
    ].sort_values("date")

    if upcoming.empty:
        st.info("No upcoming activities at this time.")
    else:
        for _, act in upcoming.iterrows():

            # Check if already registered via session state
            reg_key     = f"registered_{emp_id}_{act['activity_id']}"
            checkin_key = f"checkedin_{emp_id}_{act['activity_id']}"
            registered  = st.session_state.get(reg_key, False)
            checked_in  = st.session_state.get(checkin_key, False)

            # Status badge
            if checked_in:
                status = "✓ Attended"
                status_color = "#4caf7d"
            elif registered:
                status = "✓ Registered"
                status_color = "#f49052"
            else:
                status = "Open"
                status_color = "#a07050"

            # Activity type colour dot
            type_colors = {
                "Wellness":     "#4caf7d",
                "Learning":     "#378ADD",
                "Social":       "#f49052",
                "Town Hall":    "#3C3489",
                "Volunteering": "#085041",
                "ERG":          "#712B13",
            }
            dot_color = type_colors.get(act["type"], "#a07050")

            # Render activity card
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"""
                <div style='background:#ffece1; border-radius:8px;
                            padding:12px 16px; margin-bottom:8px;'>
                    <div style='display:flex; align-items:center;
                                gap:8px; margin-bottom:4px;'>
                        <div style='width:8px; height:8px;
                                    border-radius:50%;
                                    background:{dot_color};'></div>
                        <span style='font-size:13px; font-weight:500;
                                     color:#505050;'>{act['name']}</span>
                        <span style='font-size:10px; font-weight:500;
                                     color:{status_color};
                                     margin-left:auto;'>{status}</span>
                    </div>
                    <div style='font-size:11px; color:#a07050;'>
                        {act['date'].strftime('%a %d %b %Y')} ·
                        {act['type']} ·
                        {act['format']} ·
                        +{act['points']} pts on attendance
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if not checked_in and not registered:
                    # Register button — earns 5 pts
                    if st.button("Register +5pts",
                                 key=f"reg_{act['activity_id']}"):
                        st.session_state[reg_key] = True
                        # Add 5 pts to session activity points
                        current = st.session_state.get(
                            f"activity_pts_{emp_id}", 0)
                        st.session_state[f"activity_pts_{emp_id}"] = \
                            current + 5
                        st.rerun()

                elif registered and not checked_in:
                    # Check in button — earns 25 pts
                    if st.button("Check in +25pts",
                                 key=f"checkin_{act['activity_id']}"):
                        st.session_state[checkin_key] = True
                        current = st.session_state.get(
                            f"activity_pts_{emp_id}", 0)
                        st.session_state[f"activity_pts_{emp_id}"] = \
                            current + 25
                        st.rerun()

    st.markdown("---")

    # ── Leaderboard — org wide ────────────────────────────────────────────────
    st.markdown("##### Org-wide leaderboard")

    # Vectorised points calculation — much faster than looping
    # Filter to current year and up to today once
    pulse_cy = df_pulse[
        (df_pulse["week_date"].dt.year == CURRENT_YEAR) &
        (df_pulse["week_date"] <= TODAY)
    ]
    kudos_given_cy = df_kudos[
        (df_kudos["date"].dt.year == CURRENT_YEAR) &
        (df_kudos["date"] <= TODAY)
    ]
    kudos_rcvd_cy = df_kudos[
        (df_kudos["date"].dt.year == CURRENT_YEAR) &
        (df_kudos["date"] <= TODAY)
    ]

    # Count per employee in one operation
    pulse_pts   = pulse_cy.groupby("employee_id").size().reset_index()
    pulse_pts.columns = ["employee_id", "pulse_pts"]
    pulse_pts["pulse_pts"] *= 20

    given_pts   = kudos_given_cy.groupby("giver_id").size().reset_index()
    given_pts.columns = ["employee_id", "given_pts"]
    given_pts["given_pts"] *= 10

    rcvd_pts    = kudos_rcvd_cy.groupby("recipient_id").size().reset_index()
    rcvd_pts.columns = ["employee_id", "rcvd_pts"]
    rcvd_pts["rcvd_pts"] *= 15

    # Merge all into one DataFrame
    leaderboard_df = df_employees[["employee_id","name","department"]].copy()
    leaderboard_df = leaderboard_df.merge(pulse_pts,  on="employee_id", how="left")
    leaderboard_df = leaderboard_df.merge(given_pts,  on="employee_id", how="left")
    leaderboard_df = leaderboard_df.merge(rcvd_pts,   on="employee_id", how="left")
    leaderboard_df = leaderboard_df.fillna(0)
    leaderboard_df["points"] = (
        leaderboard_df["pulse_pts"] +
        leaderboard_df["given_pts"] +
        leaderboard_df["rcvd_pts"]
    ).astype(int)
    leaderboard_df = leaderboard_df.sort_values(
        "points", ascending=False).head(20)

    # Highlight current employee's row
    for i, row in enumerate(leaderboard_df.itertuples(), 1):
        is_me     = row.employee_id == emp_id
        bg_color  = "#ffece1" if is_me else "#fff"
        font_weight = "600" if is_me else "400"
        you_tag   = " · You" if is_me else ""

        st.markdown(f"""
        <div style='display:flex; align-items:center;
                    gap:12px; padding:8px 12px;
                    background:{bg_color}; border-radius:6px;
                    margin-bottom:4px;'>
            <span style='font-size:12px; color:#a07050;
                         width:24px;'>#{i}</span>
            <span style='font-size:12px; font-weight:{font_weight};
                         color:#505050; flex:1;'>
                {row.name}{you_tag}
            </span>
            <span style='font-size:11px; color:#a07050;
                         width:100px;'>{row.department}</span>
            <span style='font-size:12px; font-weight:500;
                         color:#f49052;'>{row.points:,} pts</span>
        </div>
        """, unsafe_allow_html=True)

elif role == "Manager":

    # ── Manager activities view ───────────────────────────────────────────────
    # Team participation tracker + upcoming activities + dept leaderboard

    # ── Hero banner ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:#2C2C2A; border-radius:12px;
                padding:20px 24px; margin-bottom:20px;'>
        <div style='font-size:11px; color:#888780;
                    text-transform:uppercase;
                    letter-spacing:.07em;'>
            Team activities · {dept} ·
            Jan — {CURRENT_MONTH} {CURRENT_YEAR}
        </div>
        <div style='font-size:26px; font-weight:500;
                    color:#F1EFE8; margin:4px 0;'>{emp_name}</div>
        <div style='font-size:12px; color:#B4B2A9;'>
            Track your team's participation and points
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Team points summary ───────────────────────────────────────────────────
    team_members = df_employees[
        df_employees["manager"] == mgr_name
    ].copy()

   # Vectorised — filter once, merge, no looping
    pulse_cy       = df_pulse[
        (df_pulse["week_date"].dt.year == CURRENT_YEAR) &
        (df_pulse["week_date"] <= TODAY)
    ]
    kudos_given_cy = df_kudos[
        (df_kudos["date"].dt.year == CURRENT_YEAR) &
        (df_kudos["date"] <= TODAY)
    ]
    kudos_rcvd_cy  = df_kudos[
        (df_kudos["date"].dt.year == CURRENT_YEAR) &
        (df_kudos["date"] <= TODAY)
    ]

    pulse_pts = pulse_cy.groupby("employee_id").size().reset_index()
    pulse_pts.columns = ["employee_id", "pulse_pts"]
    pulse_pts["pulse_pts"] *= 20

    given_pts = kudos_given_cy.groupby("giver_id").size().reset_index()
    given_pts.columns = ["employee_id", "given_pts"]
    given_pts["given_pts"] *= 10

    rcvd_pts  = kudos_rcvd_cy.groupby("recipient_id").size().reset_index()
    rcvd_pts.columns = ["employee_id", "rcvd_pts"]
    rcvd_pts["rcvd_pts"] *= 15

    team_pts_df = team_members[["employee_id","name"]].copy()
    team_pts_df = team_pts_df.merge(pulse_pts, on="employee_id", how="left")
    team_pts_df = team_pts_df.merge(given_pts, on="employee_id", how="left")
    team_pts_df = team_pts_df.merge(rcvd_pts,  on="employee_id", how="left")
    team_pts_df = team_pts_df.fillna(0)
    team_pts_df["points"] = (
        team_pts_df["pulse_pts"] +
        team_pts_df["given_pts"] +
        team_pts_df["rcvd_pts"]
    ).astype(int)
    team_pts_df = team_pts_df.sort_values("points", ascending=False)

    # KPI strip
    k1, k2, k3 = st.columns(3)
    with k1:
        avg_pts = round(team_pts_df["points"].mean())
        st.metric("Team avg points", f"{avg_pts:,}")
        st.caption("Average points per team member")
    with k2:
        top_earner = team_pts_df.iloc[0]["name"]
        st.metric("Top earner", top_earner.split()[0])
        st.caption(f"{team_pts_df.iloc[0]['points']:,} pts")
    with k3:
        total_pts = team_pts_df["points"].sum()
        st.metric("Team total points", f"{total_pts:,}")
        st.caption("Combined across all modules")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # ── Team member points breakdown ──────────────────────────────────────
        st.markdown("##### Team points breakdown")
        for _, row in team_pts_df.iterrows():
            st.markdown(f"""
            <div style='display:flex; align-items:center;
                        gap:10px; margin-bottom:8px;'>
                <span style='font-size:12px; color:#505050;
                             flex:1;'>{row['name']}</span>
                <div style='width:100px; height:6px;
                            background:#f5e8d8; border-radius:3px;
                            overflow:hidden;'>
                    <div style='width:{min(row["points"]/2000*100, 100)}%;
                                height:100%; background:#f49052;
                                border-radius:3px;'></div>
                </div>
                <span style='font-size:12px; font-weight:500;
                             color:#f49052; width:60px;
                             text-align:right;'>
                    {row['points']:,}
                </span>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        # ── Upcoming activities for the team ──────────────────────────────────
        st.markdown("##### Upcoming activities")
        upcoming = df_activities[
            (df_activities["date"] >= TODAY) &
            (
                (df_activities["department_target"] == "All") |
                (df_activities["department_target"] == dept)
            )
        ].sort_values("date").head(5)

        if upcoming.empty:
            st.info("No upcoming activities.")
        else:
            for _, act in upcoming.iterrows():
                st.markdown(f"""
                <div style='background:#ffece1; border-radius:8px;
                            padding:10px 14px; margin-bottom:8px;'>
                    <div style='font-size:12px; font-weight:500;
                                color:#505050;'>{act['name']}</div>
                    <div style='font-size:10px; color:#a07050;
                                margin-top:3px;'>
                        {act['date'].strftime('%a %d %b')} ·
                        {act['type']} ·
                        {act['format']} ·
                        +{act['points']} pts
                    </div>
                </div>
                """, unsafe_allow_html=True)

elif role == "HR":

    # ── HR activities view ────────────────────────────────────────────────────
    # Org-wide participation dashboard + activity management + full leaderboard

    # ── Hero banner ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:#3C3489; border-radius:12px;
                padding:20px 24px; margin-bottom:20px;
                display:flex; align-items:center;
                justify-content:space-between;'>
        <div>
            <div style='font-size:11px; color:#AFA9EC;
                        text-transform:uppercase;
                        letter-spacing:.07em;'>
                Activities + Participation · MM Group ·
                Jan — {CURRENT_MONTH} {CURRENT_YEAR}
            </div>
            <div style='font-size:26px; font-weight:500;
                        color:#fff; margin:4px 0;'>
                Organisation overview
            </div>
            <div style='font-size:12px; color:#AFA9EC;'>
                {len(df_activities)} activities ·
                {len(df_employees):,} employees
            </div>
        </div>
        <div style='text-align:center;'>
            <div style='font-size:48px; font-weight:500;
                        color:#f49052; line-height:1;'>
                {len(df_activities)}
            </div>
            <div style='font-size:11px; color:#AFA9EC;
                        margin-top:4px;'>Total activities</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI strip ─────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        org_wide = (df_activities["department_target"] == "All").sum()
        st.metric("Org-wide activities", org_wide)
        st.caption("Open to all employees")
    with k2:
        dept_specific = (df_activities["department_target"] != "All").sum()
        st.metric("Dept-specific", dept_specific)
        st.caption("Targeted by department")
    with k3:
        activity_types = df_activities["type"].nunique()
        st.metric("Activity types", activity_types)
        st.caption("Wellness, Learning, Social etc.")
    with k4:
        total_pts_available = df_activities["points"].sum()
        st.metric("Total pts available", f"{total_pts_available:,}")
        st.caption("If all activities attended")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # ── Activities by type ────────────────────────────────────────────────
        st.markdown("##### Activities by type")
        st.caption(f"All {len(df_activities)} activities — org-wide and dept-specific combined")
        type_counts = df_activities["type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        fig = px.bar(
            type_counts,
            x                       = "count",
            y                       = "type",
            orientation             = "h",
            color                   = "count",
            color_continuous_scale  = ["#ffece1","#f49052"],
            text                    = "count",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height              = 280,
            margin              = dict(l=0, r=0, t=0, b=0),
            plot_bgcolor        = "#fffbf8",
            paper_bgcolor       = "#fffbf8",
            showlegend          = False,
            coloraxis_showscale = False,
            xaxis_title         = "",
            yaxis_title         = "",
        )
        st.plotly_chart(fig)

    with col2:
        # ── Activities by format ──────────────────────────────────────────────
        st.markdown("##### In-person vs virtual")
        st.caption(f"All {len(df_activities)} activities — org-wide and dept-specific combined")
        format_counts = df_activities["format"].value_counts()
        fig2 = px.pie(
            values = format_counts.values,
            names  = format_counts.index,
            color  = format_counts.index,
            color_discrete_map = {
                "In-Person": "#f49052",
                "Virtual":   "#3C3489",
            },
        )
        fig2.update_layout(
            height        = 280,
            margin        = dict(l=0, r=0, t=0, b=0),
            paper_bgcolor = "#fffbf8",
        )
        st.plotly_chart(fig2)

    st.markdown("---")

    # ── Full activity list ────────────────────────────────────────────────────
    st.markdown("##### All activities")

    # Filter controls
    f1, f2 = st.columns(2)
    with f1:
        type_filter = st.selectbox(
            "Filter by type",
            ["All"] + df_activities["type"].unique().tolist(),
        )
    with f2:
        target_filter = st.selectbox(
            "Filter by target",
            ["All", "Org-wide", "Department-specific"],
        )

    # Apply filters
    filtered = df_activities.copy()
    if type_filter != "All":
        filtered = filtered[filtered["type"] == type_filter]
    if target_filter == "Org-wide":
        filtered = filtered[filtered["department_target"] == "All"]
    elif target_filter == "Department-specific":
        filtered = filtered[filtered["department_target"] != "All"]

    filtered = filtered.sort_values("date", ascending=False)

    for _, act in filtered.iterrows():
        st.markdown(f"""
        <div style='display:flex; align-items:center;
                    justify-content:space-between;
                    padding:8px 12px; margin-bottom:6px;
                    background:#ffece1; border-radius:8px;'>
            <div>
                <span style='font-size:12px; font-weight:500;
                             color:#505050;'>{act['name']}</span>
                <span style='font-size:10px; color:#a07050;
                             margin-left:8px;'>
                    {act['date'].strftime('%d %b %Y')} ·
                    {act['type']} ·
                    {act['format']} ·
                    Target: {act['department_target']}
                </span>
            </div>
            <span style='font-size:12px; font-weight:500;
                         color:#f49052; white-space:nowrap;'>
                +{act['points']} pts
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Org leaderboard ───────────────────────────────────────────────────────
    st.markdown("##### Points leaderboard — top 20")

    # Department filter for HR
    dept_filter = st.selectbox(
        "Filter by department",
        ["All departments"] + df_employees["department"].unique().tolist(),
    )

    # Calculate points for filtered employees
    if dept_filter == "All departments":
        emp_pool = df_employees    # all 500 employees
    else:
        emp_pool = df_employees[
            df_employees["department"] == dept_filter
        ]

    leaderboard = []
    for _, emp in emp_pool.iterrows():
        pts = calculate_points(emp["employee_id"])
        leaderboard.append({
            "name":       emp["name"],
            "department": emp["department"],
            "points":     pts["total"],
        })

    leaderboard_df = pd.DataFrame(leaderboard).sort_values(
        "points", ascending=False).head(20)

    for i, row in enumerate(leaderboard_df.itertuples(), 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
        st.markdown(f"""
        <div style='display:flex; align-items:center;
                    gap:12px; padding:8px 12px;
                    background:#fff; border-radius:6px;
                    margin-bottom:4px;
                    border:0.5px solid #f0d0b8;'>
            <span style='font-size:12px; width:32px;'>{medal}</span>
            <span style='font-size:12px; color:#505050;
                         flex:1;'>{row.name}</span>
            <span style='font-size:11px; color:#a07050;
                         width:120px;'>{row.department}</span>
            <span style='font-size:12px; font-weight:500;
                         color:#f49052;'>{row.points:,} pts</span>
        </div>
        """, unsafe_allow_html=True)

show_footer()