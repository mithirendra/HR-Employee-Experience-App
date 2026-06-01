# ── app.py ────────────────────────────────────────────────────────────────────
# Vibe — Employee Experience Platform · MM Group
# Entry point — login screen, sidebar, home page routing by role.

import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import (
    load_employees, load_pulse, load_kudos, load_activities,
    filter_pulse_by_role, filter_kudos_by_role,
    engagement_color, format_delta, is_logged_in,
    get_role, get_emp_id, get_manager_name,
    apply_vibe_style, show_footer, get_logo_base64,
    show_sidebar,
)


# Must be the first Streamlit command in the file
st.set_page_config(
    page_title            = "VIBE App - Demo | Mitma Consulting",
    page_icon             = "assets/mitma_favicon.png",
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

# Vibe warm palette + hide Streamlit default chrome
apply_vibe_style()

# ── Login screen ──────────────────────────────────────────────────────────────
def show_login():
    """Render the Vibe login screen."""

    # Centre the login card using 3 columns
    # Middle column (1.2) is wider than the two empty side columns (1)
    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        # Add vertical spacing at the top so the card sits in the middle
        st.markdown("<br><br>", unsafe_allow_html=True)

        # ── Branding ──────────────────────────────────────────────────────────
        # Load Mitma logo as base64 — embedded directly in HTML
        # Falls back to emoji if logo file not found
        logo_b64  = get_logo_base64()

        logo_html = (
            f"<img src='data:image/png;base64,{logo_b64}' "
            f"style='height:30px; margin-bottom:12px;'>"
            if logo_b64 else "🔵"
        )

        # Render logo, app name, tagline and Mitma branding
        # text-align:center centres everything in the column
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
        </div>
        """, unsafe_allow_html=True)

        # ── Role selector ─────────────────────────────────────────────────────
        # label_visibility="collapsed" hides the Streamlit label
        # We show our own bold label above instead for styling control
        st.markdown("**Select your role**")
        role = st.selectbox(
            label            = "Role",
            options          = ["Employee", "Manager", "HR"],
            label_visibility = "collapsed",
        )

        # ── Employee ID input ─────────────────────────────────────────────────
        # Same pattern — custom label above, Streamlit label hidden
        st.markdown("**Employee ID**")
        emp_id_input = st.text_input(
            label            = "Employee ID",
            placeholder      = "e.g. 1042",
            label_visibility = "collapsed",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Sign in button — centred ──────────────────────────────────────────
        # Streamlit buttons default to left — use columns to centre
        # Empty columns on either side push the button to the middle
        # ── Sign in button — centred using HTML ───────────────────────────────────
        # Streamlit buttons can't be reliably centred with CSS
        # Use st.columns to push button to centre instead
        col_l, col_m, col_r = st.columns([2, 3, 2])
        with col_m:
            sign_in = st.button("Sign in to Vibe", use_container_width=True)

        # ── Login validation and session state ────────────────────────────────
        # Only runs when the button is clicked
        if sign_in:

            # Must not be empty
            if not emp_id_input.strip():
                st.error("Please enter your Employee ID.")
                return

            # Must be a valid integer
            try:
                emp_id = int(emp_id_input.strip())
            except ValueError:
                st.error("Employee ID must be a number.")
                return

            # Must exist in the employees CSV
            df_emp  = load_employees()
            emp_row = df_emp[df_emp["employee_id"] == emp_id]

            if emp_row.empty:
                st.error(
                    f"Employee ID {emp_id} not found. "
                    f"Try a number between 1000 and 1499.")
                return

            # Store all login details in session state
            # These persist across all pages for the session
            st.session_state.role         = role
            st.session_state.emp_id       = emp_id
            st.session_state.emp_name     = emp_row.iloc[0]["name"]
            st.session_state.department   = emp_row.iloc[0]["department"]
            st.session_state.manager_name = emp_row.iloc[0]["manager"]
            st.session_state.job_title    = emp_row.iloc[0]["job_title"]

            # Rerun the app — is_logged_in() now returns True
            # Main router picks this up and shows the home page
            st.rerun()

        # ── Helper text ───────────────────────────────────────────────────────
        # Shown below the button — guides demo users on what IDs to use
        st.markdown("""
        <div style='text-align:center; margin-top:16px;
                    font-size:11px; color:#c0a080;
                    font-family:Montserrat,sans-serif;'>
            Demo app · Use any Employee ID between 1000 and 1499<br>
            Select any role to explore different views
        </div>
        """, unsafe_allow_html=True)


# ── Main router ───────────────────────────────────────────────────────────────
# This is the core logic — runs every time the page loads.
# Checks session state and routes to the correct screen.

if not is_logged_in():
    show_login()
else:
    show_sidebar()
    role     = get_role()
    emp_id   = get_emp_id()
    emp_name = st.session_state.get("emp_name", "")
    dept     = st.session_state.get("department", "")
    mgr_name = get_manager_name()

    # Load data
    df_employees = load_employees()
    df_pulse     = load_pulse()
    df_kudos     = load_kudos()
    df_activities = load_activities()

    # Filter data by role
    df_pulse_role = filter_pulse_by_role(df_pulse, role, emp_id, mgr_name)
    df_kudos_role = filter_kudos_by_role(
                        df_kudos, role, emp_id, mgr_name, df_employees)

    # ── Route to correct home by role ─────────────────────────────────────────
    if role == "Employee":

        my_pulse = df_pulse_role.copy()

        if my_pulse.empty:
            st.info("No pulse data found for your account.")
        else:
            latest = my_pulse.sort_values("week_number").iloc[-1]
            prev   = my_pulse.sort_values("week_number").iloc[-2] \
                        if len(my_pulse) > 1 else latest

            score       = round(latest["composite_score"])
            score_delta = round(score - prev["composite_score"])

            # ── Hero banner ───────────────────────────────────────────────────
            st.markdown(f"""
            <div style='background:#f49052; border-radius:12px;
                        padding:20px 24px; margin-bottom:20px;
                        display:flex; align-items:center;
                        justify-content:space-between;'>
                <div>
                    <div style='font-size:11px; color:#fff3ea;
                                text-transform:uppercase;
                                letter-spacing:.07em;'>
                        Good day
                    </div>
                    <div style='font-size:26px; font-weight:500;
                                color:#fff; margin:4px 0;'>{emp_name}</div>
                    <div style='font-size:12px; color:#fff3ea;'>
                        {dept} · {st.session_state.get("job_title", "")}
                    </div>
                </div>
                <div style='text-align:center;'>
                    <div style='font-size:11px; color:#fff3ea;
                                margin-bottom:4px;'>
                        Your engagement score
                    </div>
                    <div style='font-size:48px; font-weight:500;
                                color:#fff; line-height:1;'>{score}</div>
                    <div style='font-size:11px; color:#fff3ea;
                                margin-top:4px;'>
                        {format_delta(score_delta)} from last week
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── KPI strip ─────────────────────────────────────────────────────
            k1, k2, k3, k4, k5 = st.columns(5)
            with k1:
                st.metric("Clarity",      latest["clarity"])
                st.caption("I understand what is expected of me")
            with k2:
                st.metric("Connection",   latest["connection"])
                st.caption("I feel connected to my team and organisation")
            with k3:
                st.metric("Contribution", latest["contribution"])
                st.caption("My work makes a meaningful difference")
            with k4:
                st.metric("Confidence",   latest["confidence"])
                st.caption("I have the tools and support to do my job well")
            with k5:
                st.metric("Care",         latest["care"])
                st.caption("My manager genuinely cares about my wellbeing")

            st.markdown("---")

            # ── 5C scores and trend ───────────────────────────────────────────
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Your 5C scores this week")
                dims = ["clarity","connection","contribution","confidence","care"]
                for dim in dims:
                    val       = latest[dim]
                    bar_color = engagement_color(val * 10)
                    st.markdown(f"""
                    <div style='display:flex; align-items:center;
                                gap:10px; margin-bottom:8px;'>
                        <span style='width:90px; font-size:12px;
                                        color:#705040; text-align:right;
                                        text-transform:capitalize;'>{dim}</span>
                        <div style='flex:1; height:8px;
                                    background:#f5e8d8; border-radius:4px;
                                    overflow:hidden;'>
                            <div style='width:{val*10}%; height:100%;
                                        background:{bar_color};
                                        border-radius:4px;'></div>
                        </div>
                        <span style='font-size:12px; font-weight:500;
                                        color:#505050; width:28px;'>{val}</span>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                st.markdown("##### Engagement trend — last 8 weeks")
                trend_data = my_pulse.sort_values("week_number").tail(8)
                fig = px.line(
                    trend_data,
                    x                      = "week_date",
                    y                      = "composite_score",
                    markers                = True,
                    color_discrete_sequence = ["#f49052"],
                )
                fig.update_layout(
                    height        = 220,
                    margin        = dict(l=0, r=0, t=0, b=0),
                    plot_bgcolor  = "#fffbf8",
                    paper_bgcolor = "#fffbf8",
                    xaxis_title   = "",
                    yaxis_title   = "",
                    yaxis_range   = [0, 100],
                    showlegend    = False,
                )
                st.plotly_chart(fig)

            st.markdown("---")

            # ── Latest Kudos received ─────────────────────────────────────────
            col3, col4 = st.columns(2)

            with col3:
                st.markdown("##### Latest Kudos received")
                my_kudos = df_kudos_role[
                    df_kudos_role["recipient_id"] == emp_id
                ].sort_values("date", ascending=False).head(3)

                if my_kudos.empty:
                    st.info("No Kudos received yet.")
                else:
                    for _, kudo in my_kudos.iterrows():
                        st.markdown(f"""
                        <div style='background:#ffece1; border-radius:8px;
                                    padding:10px 14px; margin-bottom:8px;'>
                            <div style='font-size:12px; color:#505050;
                                        font-style:italic;'>
                                "{kudo['message']}"
                            </div>
                            <div style='font-size:10px; color:#a07050;
                                        margin-top:4px;'>
                                from {kudo['giver_name']} ·
                                {kudo['category']} ·
                                +{kudo['recipient_points']} pts
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            with col4:
                st.markdown("##### Upcoming activities")
                today      = pd.Timestamp("2025-12-01")  # demo date
                upcoming   = df_activities[
                    df_activities["date"] >= today
                ].sort_values("date").head(3)

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
                                {act['format']} ·
                                +{act['points']} pts
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    elif role == "Manager":

            # Get this manager's team pulse data — already filtered by filter_pulse_by_role()
            team_pulse = df_pulse_role.copy()

            if team_pulse.empty:
                st.info("No team data found.")
            else:
                # Get the most recent week number in the dataset
                latest_week = team_pulse["week_number"].max()

                # Filter to only the latest week's rows for this team
                latest_team = team_pulse[team_pulse["week_number"] == latest_week]

                # Calculate org-wide average for the same week — used for comparison
                org_avg = round(df_pulse[
                    df_pulse["week_number"] == latest_week
                ]["composite_score"].mean(), 1)

                # Team average composite score this week
                team_score = round(latest_team["composite_score"].mean())

                # Difference between team score and org average — positive is good
                vs_org = round(team_score - org_avg, 1)

                # Count how many team members are flagged At Risk this week
                at_risk = (latest_team["engagement_label"] == "At Risk").sum()

                # How many team members submitted a pulse this week
                responded = len(latest_team)

                # ── Hero banner ───────────────────────────────────────────────────
                # Dark charcoal background — matches manager UX mockup
                # Shows team score, vs org delta, and at risk count as big numbers
                st.markdown(f"""
                <div style='background:#2C2C2A; border-radius:12px;
                            padding:20px 24px; margin-bottom:20px;
                            display:flex; align-items:center;
                            justify-content:space-between;'>
                    <div>
                        <div style='font-size:11px; color:#888780;
                                    text-transform:uppercase;
                                    letter-spacing:.07em;'>
                            {dept} · Week {latest_week}
                        </div>
                        <div style='font-size:26px; font-weight:500;
                                    color:#F1EFE8; margin:4px 0;'>{emp_name}</div>
                        <div style='font-size:12px; color:#B4B2A9;'>
                            Manager · {dept}
                        </div>
                    </div>
                    <div style='display:flex; gap:16px;'>
                        <div style='text-align:center;'>
                            <div style='font-size:32px; font-weight:500;
                                        color:{"#E24B4A" if team_score < 45 else
                                            "#f49052" if team_score < 70 else
                                            "#4caf7d"};
                                        line-height:1;'>{team_score}</div>
                            <div style='font-size:10px; color:#888780;
                                        margin-top:3px;'>Team score</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:32px; font-weight:500;
                                        color:{"#E24B4A" if vs_org < 0 else "#4caf7d"};
                                        line-height:1;'>{vs_org:+.1f}</div>
                            <div style='font-size:10px; color:#888780;
                                        margin-top:3px;'>vs org avg</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:32px; font-weight:500;
                                        color:#E24B4A; line-height:1;'>{at_risk}</div>
                            <div style='font-size:10px; color:#888780;
                                        margin-top:3px;'>At risk</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── KPI strip ─────────────────────────────────────────────────────
                # Four metric cards below the hero — quick numbers at a glance
                # st.metric() renders the built-in Streamlit metric card
                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.metric("Team score",  team_score)   # avg composite this week
                with k2:
                    st.metric("vs Org avg",  f"{vs_org:+.1f}")  # +/- vs org
                with k3:
                    st.metric("Responded",   f"{responded} members")  # pulse count
                with k4:
                    st.metric("At risk",     at_risk)       # below threshold count

                st.markdown("---")  # horizontal divider line

                # ── Two columns — member scores left, 5C breakdown right ──────────
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("##### Team member scores")

                    # Sort members highest to lowest score for easy scanning
                    members = latest_team[
                        ["name", "composite_score", "engagement_label"]
                    ].sort_values("composite_score", ascending=False)

                    # Loop through each team member and render an HTML bar row
                    for _, row in members.iterrows():

                        # Color the bar based on their score — green/orange/red
                        color = engagement_color(row["composite_score"])

                        st.markdown(f"""
                        <div style='display:flex; align-items:center;
                                    gap:10px; margin-bottom:8px;'>
                            <!-- Employee name — takes up remaining space -->
                            <span style='font-size:12px; color:#505050;
                                        flex:1;'>{row['name']}</span>
                            <!-- Grey track — full width bar background -->
                            <div style='width:120px; height:6px;
                                        background:#f5e8d8; border-radius:3px;
                                        overflow:hidden;'>
                                <!-- Coloured fill — width = composite score as % -->
                                <div style='width:{row["composite_score"]}%;
                                            height:100%; background:{color};
                                            border-radius:3px;'></div>
                            </div>
                            <!-- Score number on the right -->
                            <span style='font-size:12px; font-weight:500;
                                        color:{color}; width:36px;
                                        text-align:right;'>
                                {row["composite_score"]}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

                with col2:
                    st.markdown("##### Team 5C breakdown")

                    # Loop through each of the 5 dimensions
                    dims = ["clarity","connection","contribution","confidence","care"]
                    for dim in dims:

                        # Average this dimension score across all team members
                        avg_val   = round(latest_team[dim].mean(), 1)

                        # Convert 1-10 score to 0-100 for color function
                        bar_color = engagement_color(avg_val * 10)

                        # Render HTML bar — same pattern as member scores above
                        st.markdown(f"""
                        <div style='display:flex; align-items:center;
                                    gap:10px; margin-bottom:8px;'>
                            <span style='width:90px; font-size:12px;
                                        color:#705040; text-align:right;
                                        text-transform:capitalize;'>{dim}</span>
                            <div style='flex:1; height:8px;
                                        background:#f5e8d8; border-radius:4px;
                                        overflow:hidden;'>
                                <div style='width:{avg_val*10}%; height:100%;
                                            background:{bar_color};
                                            border-radius:4px;'></div>
                            </div>
                            <span style='font-size:12px; font-weight:500;
                                        color:#505050;
                                        width:28px;'>{avg_val}</span>
                        </div>
                        """, unsafe_allow_html=True)

                    # ── Coaching nudge ────────────────────────────────────────────
                    # Only shows if at least one team member is At Risk
                    # Amber left-border box — matches UX mockup
                    if at_risk > 0:
                        st.markdown(f"""
                        <div style='background:#FAEEDA;
                                    border-left:3px solid #f49052;
                                    padding:10px 12px; margin-top:12px;
                                    border-radius:0 8px 8px 0;'>
                            <div style='font-size:11px; font-weight:500;
                                        color:#633806;'>Coaching nudge</div>
                            <div style='font-size:11px; color:#854F0B;
                                        margin-top:3px; line-height:1.5;'>
                                <!-- Grammatically correct singular/plural -->
                                {at_risk} member{"s" if at_risk > 1 else ""}
                                below threshold this week.
                                Review Care and Connection scores —
                                consider scheduling 1-on-1s.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")  # divider before participation section

                # ── Team participation ────────────────────────────────────────────
                # Three metrics showing how active the team has been this week
                st.markdown("##### Team participation this week")
                p1, p2, p3 = st.columns(3)

                with p1:
                    # Count of team members who submitted a pulse this week
                    pulse_count = len(latest_team)
                    st.metric("Pulse responses", f"{pulse_count} members")

                with p2:
                    # Count Kudos given by any team member this week
                    # isin() checks if giver_id is in the list of team employee IDs
                    team_ids    = latest_team["employee_id"].tolist()
                    kudos_count = len(df_kudos[
                        df_kudos["giver_id"].isin(team_ids) &
                        (df_kudos["week_number"] == latest_week)
                    ])
                    st.metric("Kudos given", kudos_count)

                with p3:
                    # Average absent days across all team members this week
                    avg_absent = round(latest_team["absent_days"].mean(), 1)
                    st.metric("Avg absent days", avg_absent)

    elif role == "HR":

        # Get the most recent week in the dataset
        latest_week  = df_pulse["week_number"].max()

        # Filter all pulse data to the latest week only
        latest_pulse = df_pulse[df_pulse["week_number"] == latest_week]

        # Org-wide engagement score — average of all composite scores this week
        org_score    = round(latest_pulse["composite_score"].mean())

        # Response rate — how many employees submitted a pulse this week
        # Divided by total employees to get a percentage
        response_rate = round(
            len(latest_pulse) / len(df_employees) * 100, 1)

        # Calculate at-risk percentage per department
        # groupby("department") splits the data by dept
        # apply() runs a function on each dept group
        # The function calculates what % of that dept is At Risk
        at_risk_teams = latest_pulse.groupby("department").apply(
            lambda x: (x["engagement_label"] == "At Risk").mean()
        )

        # Flag departments where more than 30% of employees are At Risk
        flagged_depts = at_risk_teams[at_risk_teams > 0.3].index.tolist()

        # ── Hero banner ───────────────────────────────────────────────────────
        # Deep purple background — matches HR UX mockup
        # Alert message changes based on how many depts are flagged
        alert_msg = (
            f"{len(flagged_depts)} department"
            f"{'s' if len(flagged_depts) != 1 else ''} need attention"
            if flagged_depts else "Org engagement is healthy this week"
        )

        st.markdown(f"""
        <div style='background:#3C3489; border-radius:12px;
                    padding:20px 24px; margin-bottom:20px;
                    display:flex; align-items:center;
                    justify-content:space-between;'>
            <div>
                <div style='font-size:11px; color:#AFA9EC;
                            text-transform:uppercase;
                            letter-spacing:.07em;'>
                    Org overview · Week {latest_week}
                </div>
                <div style='font-size:26px; font-weight:500;
                            color:#fff; margin:4px 0;'>{alert_msg}</div>
                <div style='font-size:12px; color:#AFA9EC;'>
                    {len(df_employees):,} employees ·
                    9 departments · MM Group
                </div>
            </div>
            <div style='text-align:center;'>
                <!-- Big org score on the right side of the banner -->
                <div style='font-size:48px; font-weight:500;
                            color:#f49052; line-height:1;'>{org_score}</div>
                <div style='font-size:11px; color:#AFA9EC;
                            margin-top:4px;'>org engagement score</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── KPI strip ─────────────────────────────────────────────────────────
        # Five metrics across the top — org score, response rate,
        # flagged depts, engaged %, avg composite
        k1, k2, k3, k4, k5 = st.columns(5)

        with k1:
            st.metric("Org score",     org_score)
        with k2:
            st.metric("Response rate", f"{response_rate}%")
        with k3:
            # Count of departments with >30% at risk members
            st.metric("Flagged depts", len(flagged_depts))
        with k4:
            # Percentage of all employees labelled Engaged this week
            engaged_pct = round(
                (latest_pulse["engagement_label"] == "Engaged").mean() * 100, 1)
            st.metric("Engaged",       f"{engaged_pct}%")
        with k5:
            # Count of employees labelled At Risk this week
            at_risk_count = (latest_pulse["engagement_label"] == "At Risk").sum()
            st.metric("At risk",       at_risk_count)

        st.markdown("---")

        # ── Department heatmap + flagged teams ────────────────────────────────
        col1, col2 = st.columns([1.6, 1])

        with col1:
            st.markdown("##### Department scores — latest week")

            # Group by department and average all 5 dimension scores
            # Result is a DataFrame with depts as rows and dims as columns
            dept_summary = latest_pulse.groupby("department")[
                ["clarity","connection","contribution","confidence","care"]
            ].mean().round(1)

            # Plotly heatmap — go.Heatmap gives more control than px.imshow
            # z = the values, x = column labels, y = row labels
            fig = go.Figure(data=go.Heatmap(
                z            = dept_summary.values,
                x            = ["Clarity","Connection",
                                 "Contribution","Confidence","Care"],
                y            = dept_summary.index.tolist(),
                colorscale   = [
                                [0.0, "#E24B4A"],   # strong red — low scores
                                [0.4, "#f49052"],   # orange — mid-low
                                [0.6, "#FAEEDA"],   # amber — mid
                                [1.0, "#4caf7d"],   # strong green — high scores
                            ],
                zmin         = 3,       # minimum score on scale
                zmax         = 9,      # maximum score on scale
                text         = dept_summary.values.round(1),
                texttemplate = "%{text}",  # show value inside each cell
                showscale    = False,      # hide the colour legend bar
            ))
            fig.update_layout(
                height        = 280,
                margin        = dict(l=0, r=0, t=0, b=0),
                plot_bgcolor  = "#fffbf8",
                paper_bgcolor = "#fffbf8",
            )
            st.plotly_chart(fig)

        with col2:
            st.markdown("##### Flagged departments")

            if not flagged_depts:
                st.success("No departments flagged this week.")
            else:
                # Loop through each flagged dept and show score + risk %
                for dept_name in flagged_depts:
                    dept_score = round(
                        latest_pulse[
                            latest_pulse["department"] == dept_name
                        ]["composite_score"].mean(), 1)
                    risk_pct   = round(at_risk_teams[dept_name] * 100, 1)

                    st.markdown(f"""
                    <div style='display:flex; align-items:center;
                                justify-content:space-between;
                                padding:8px 0;
                                border-bottom:0.5px solid #f0d0b8;'>
                        <span style='font-size:12px;
                                     color:#505050;'>{dept_name}</span>
                        <div style='text-align:right;'>
                            <span style='font-size:12px; font-weight:500;
                                         color:#E24B4A;'>{dept_score}</span>
                            <span style='font-size:10px; font-weight:500;
                                         background:#FCEBEB; color:#791F1F;
                                         padding:2px 8px; border-radius:8px;
                                         margin-left:6px;'>
                                {risk_pct}% at risk
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")

            # ── Points leaderboard snapshot ───────────────────────────────────
            st.markdown("##### Points leaderboard — top 5")

            # Approximate points from pulse submissions only for now
            # Full points engine wired in later modules
            # Count how many pulse responses each employee submitted
            pulse_counts = df_pulse.groupby(
                ["employee_id","name"]
            )["response_id"].count().reset_index()
            pulse_counts.columns = ["employee_id","name","submissions"]

            # Each submission = 20 points
            pulse_counts["points"] = pulse_counts["submissions"] * 20

            # Get top 5 by points
            top5 = pulse_counts.nlargest(5, "points")

            for i, row in enumerate(top5.itertuples(), 1):
                st.markdown(f"""
                <div style='display:flex; align-items:center;
                            justify-content:space-between;
                            padding:6px 0;
                            border-bottom:0.5px solid #f0d0b8;'>
                    <span style='font-size:12px; color:#505050;'>
                        {i}. {row.name}
                    </span>
                    <span style='font-size:12px; font-weight:500;
                                 color:#f49052;'>
                        {row.points:,} pts
                    </span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Intervention alerts ───────────────────────────────────────────────
        st.markdown("##### Intervention alerts")

        if not flagged_depts:
            st.success("No intervention alerts this week.")
        else:
            for dept_name in flagged_depts:
                risk_pct = round(at_risk_teams[dept_name] * 100, 1)
                st.markdown(f"""
                <div style='display:flex; align-items:center;
                            justify-content:space-between;
                            padding:10px 14px; margin-bottom:8px;
                            background:#FCEBEB; border-radius:8px;
                            border-left:3px solid #E24B4A;'>
                    <span style='font-size:12px; color:#505050;'>
                        {dept_name} — {risk_pct}% of team at risk
                        this week
                    </span>
                    <span style='font-size:10px; font-weight:500;
                                 color:#E24B4A;'>Review →</span>
                </div>
                """, unsafe_allow_html=True)
    
    
show_footer()