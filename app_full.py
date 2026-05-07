# ── app.py ────────────────────────────────────────────────────────────────────
# Vibe — Employee Experience Platform · MM Group
# Entry point — login screen and home page routing by role.

import streamlit as st
import pandas as pd
from utils.helpers import (
    load_employees, load_pulse, load_kudos, load_activities,
    filter_pulse_by_role, filter_kudos_by_role,
    engagement_color, engagement_label, format_delta,
    is_logged_in, get_role, get_emp_id, get_manager_name,
)

# ── Page config ───────────────────────────────────────────────────────────────
# Must be the very first Streamlit command in the file.
# Sets the browser tab title, icon, and sidebar default state.
st.set_page_config(
    page_title = "Vibe — MM Group",
    page_icon  = "🔵",
    layout     = "wide",              # use full browser width
    initial_sidebar_state = "expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
# Applies the Vibe warm palette and hides the default Streamlit menu/footer.
# Colors match the UX mockups — background, cards, accent, text.
st.markdown("""
<style>
    /* Hide Streamlit default header and footer */
    #MainMenu {visibility: hidden;}
    footer     {visibility: hidden;}
    header     {visibility: hidden;}

    /* App background */
    .stApp {
        background-color: #fffbf8;
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #fff3ea;
    }

    /* Metric card styling */
    [data-testid="stMetric"] {
        background-color: #ffece1;
        border-radius: 10px;
        padding: 12px;
    }

    /* Primary button */
    .stButton > button {
        background-color: #f49052;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 500;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #e07840;
        color: white;
    }

    /* Input fields */
    .stSelectbox, .stTextInput {
        background-color: #fff;
    }

    /* Hide page names in sidebar nav — we control nav manually */
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# ── Login screen ──────────────────────────────────────────────────────────────
# Shown when no role is set in session state.
# User selects their role and enters their Employee ID.
# On successful login, role and emp_id are stored in session state.

def show_login():
    """Render the Vibe login screen."""

    # Centre the login card using columns
    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Logo and branding
        st.markdown("""
        <div style='text-align:center; margin-bottom:32px;'>
            <div style='font-size:42px; margin-bottom:8px;'>🔵</div>
            <div style='font-size:28px; font-weight:500; color:#2C2C2A;'>Vibe</div>
            <div style='font-size:13px; color:#a07050; margin-top:4px;'>
                Employee Experience Platform
            </div>
            <div style='font-size:11px; color:#c0a080; margin-top:2px;'>
                MM Group
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Login form
        st.markdown("**Select your role**")
        role = st.selectbox(
            label      = "Role",
            options    = ["Employee", "Manager", "HR"],
            label_visibility = "collapsed",  # hide label — shown above manually
        )

        st.markdown("**Employee ID**")
        emp_id_input = st.text_input(
            label       = "Employee ID",
            placeholder = "e.g. 1042",
            label_visibility = "collapsed",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Login button
        if st.button("Sign in to Vibe"):

            # Validate employee ID input
            if not emp_id_input.strip():
                st.error("Please enter your Employee ID.")
                return

            # Check if employee ID exists in the data
            df_emp = load_employees()
            try:
                emp_id = int(emp_id_input.strip())
            except ValueError:
                st.error("Employee ID must be a number.")
                return

            emp_row = df_emp[df_emp["employee_id"] == emp_id]

            if emp_row.empty:
                st.error(f"Employee ID {emp_id} not found. Please try again.")
                return

            # Store login details in session state
            # These persist across all pages for the duration of the session
            st.session_state.role         = role
            st.session_state.emp_id       = emp_id
            st.session_state.emp_name     = emp_row.iloc[0]["name"]
            st.session_state.department   = emp_row.iloc[0]["department"]
            st.session_state.manager_name = emp_row.iloc[0]["manager"]
            st.session_state.job_title    = emp_row.iloc[0]["job_title"]

            # Reload the app — now is_logged_in() returns True
            st.rerun()

        # Helper text below the form
        st.markdown("""
        <div style='text-align:center; margin-top:16px; font-size:11px; color:#c0a080;'>
            Demo app · Use any Employee ID between 1000 and 1499
        </div>
        """, unsafe_allow_html=True)

# ── Sidebar navigation ────────────────────────────────────────────────────────
# Shown after login. Displays the Vibe logo, user info, points balance,
# and navigation links to all module pages.

def show_sidebar():
    """Render the sidebar navigation after login."""

    role      = get_role()
    emp_name  = st.session_state.get("emp_name", "")
    dept      = st.session_state.get("department", "")

    with st.sidebar:

        # Logo
        st.markdown("""
        <div style='padding:8px 0 16px;'>
            <span style='font-size:20px; font-weight:500; color:#2C2C2A;'>🔵 Vibe</span>
            <div style='font-size:10px; color:#a07050; margin-top:2px;'>
                Employee Experience Platform
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # User info and role badge
        role_colors = {
            "Employee": ("#E1F5EE", "#085041"),
            "Manager":  ("#E6F1FB", "#0C447C"),
            "HR":       ("#FAECE7", "#712B13"),
        }
        bg, fg = role_colors.get(role, ("#eee", "#333"))

        st.markdown(f"""
        <div style='margin-bottom:12px;'>
            <div style='font-size:13px; font-weight:500;
                        color:#2C2C2A;'>{emp_name}</div>
            <div style='font-size:11px; color:#a07050;
                        margin-top:2px;'>{dept}</div>
            <span style='font-size:10px; font-weight:500;
                         background:{bg}; color:{fg};
                         padding:2px 8px; border-radius:10px;
                         display:inline-block; margin-top:4px;'>{role}</span>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Navigation links
        # st.page_link points to each file in the pages/ folder
        st.markdown("**Navigate**")
        st.page_link("app.py",                      label="🏠  Home",        )
        st.page_link("pages/1_Pulse_Survey.py",      label="📊  Pulse Survey" )
        st.page_link("pages/2_Wellbeing.py",         label="💚  Wellbeing"    )
        st.page_link("pages/3_Activities.py",        label="🎯  Activities"   )
        st.page_link("pages/4_Rewards.py",           label="🎁  Rewards"      )
        st.page_link("pages/5_Kudos.py",             label="⭐  Kudos"        )
        st.page_link("pages/6_Connect.py",           label="📣  Connect"      )

        st.divider()

        # Sign out button
        if st.button("Sign out"):
            # Clear all session state and return to login screen
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ── Main router ───────────────────────────────────────────────────────────────
# Checks login state and renders the correct screen.

if not is_logged_in():
    # Not logged in — show login screen only, no sidebar
    show_login()

else:
    # Logged in — show sidebar and home page
    show_sidebar()

    role      = get_role()
    emp_id    = get_emp_id()
    emp_name  = st.session_state.get("emp_name", "")
    dept      = st.session_state.get("department", "")
    mgr_name  = get_manager_name()

    # Load data
    df_employees  = load_employees()
    df_pulse      = load_pulse()
    df_pulse_role = filter_pulse_by_role(df_pulse, role, emp_id, mgr_name)
    df_kudos      = load_kudos()
    df_kudos_role = filter_kudos_by_role(
                        df_kudos, role, emp_id, mgr_name, df_employees)

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='margin-bottom:20px;'>
        <span style='font-size:22px; font-weight:500;
                     color:#2C2C2A;'>Welcome back, {emp_name.split()[0]}</span>
        <span style='font-size:12px; color:#a07050;
                     margin-left:10px;'>MM Group · Vibe</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Route to correct home page by role ────────────────────────────────────
    if role == "Employee":

        # ── Employee home ─────────────────────────────────────────────────────
        # Personal engagement summary, 5C scores, streak, latest Kudos,
        # upcoming activities.

        # Get this employee's pulse data
        my_pulse = df_pulse_role.copy()

        if my_pulse.empty:
            st.info("No pulse data found for your account yet.")
        else:
            # Latest week scores
            latest = my_pulse.sort_values("week_number").iloc[-1]
            prev   = my_pulse.sort_values("week_number").iloc[-2] \
                     if len(my_pulse) > 1 else latest

            # ── Hero metrics ──────────────────────────────────────────────────
            score       = latest["composite_score"]
            score_delta = round(score - prev["composite_score"], 1)
            color       = engagement_color(score)

            st.markdown(f"""
            <div style='background:#f49052; border-radius:12px;
                        padding:20px 24px; margin-bottom:20px;
                        display:flex; align-items:center;
                        justify-content:space-between;'>
                <div>
                    <div style='font-size:11px; color:#fff3ea;
                                text-transform:uppercase;
                                letter-spacing:.07em;'>Your engagement</div>
                    <div style='font-size:28px; font-weight:500;
                                color:#fff; margin:4px 0;'>{emp_name}</div>
                    <div style='font-size:12px; color:#fff3ea;'>
                        {dept} · {st.session_state.get("job_title","")}
                    </div>
                </div>
                <div style='text-align:center;'>
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
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.metric("Clarity",      latest["clarity"])
            with k2:
                st.metric("Connection",   latest["connection"])
            with k3:
                st.metric("Contribution", latest["contribution"])
            with k4:
                st.metric("Confidence",   latest["confidence"])

            # ── 5C scores and trend ───────────────────────────────────────────
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Your 5C scores this week")
                dims = ["clarity","connection","contribution","confidence","care"]
                for dim in dims:
                    val = latest[dim]
                    bar_color = engagement_color(val * 10)
                    st.markdown(f"""
                    <div style='display:flex; align-items:center;
                                gap:10px; margin-bottom:6px;'>
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
                import plotly.express as px
                trend_data = my_pulse.sort_values("week_number").tail(8)
                fig = px.line(
                    trend_data,
                    x     = "week_date",
                    y     = "composite_score",
                    markers = True,
                    color_discrete_sequence = ["#f49052"],
                )
                fig.update_layout(
                    height          = 200,
                    margin          = dict(l=0, r=0, t=0, b=0),
                    plot_bgcolor    = "#fffbf8",
                    paper_bgcolor   = "#fffbf8",
                    xaxis_title     = "",
                    yaxis_title     = "",
                    yaxis_range     = [0, 100],
                    showlegend      = False,
                )
                st.plotly_chart(fig, use_container_width=True)

            # ── Latest Kudos received ─────────────────────────────────────────
            st.markdown("##### Latest Kudos received")
            my_kudos_received = df_kudos_role[
                df_kudos_role["recipient_id"] == emp_id
            ].sort_values("date", ascending=False).head(3)

            if my_kudos_received.empty:
                st.info("No Kudos received yet — keep up the great work!")
            else:
                for _, kudo in my_kudos_received.iterrows():
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

    elif role == "Manager":

        # ── Manager home ──────────────────────────────────────────────────────
        # Team engagement summary, member scores, 5C breakdown,
        # participation tracker, coaching nudge.

        team_pulse = df_pulse_role.copy()

        if team_pulse.empty:
            st.info("No team pulse data found.")
        else:
            latest_week = team_pulse["week_number"].max()
            latest_team = team_pulse[
                team_pulse["week_number"] == latest_week
            ]
            org_avg = df_pulse[
                df_pulse["week_number"] == latest_week
            ]["composite_score"].mean()

            team_score  = round(latest_team["composite_score"].mean(), 1)
            vs_org      = round(team_score - org_avg, 1)
            at_risk     = (latest_team["engagement_label"] == "At Risk").sum()
            responded   = len(latest_team)

            # ── Hero banner ───────────────────────────────────────────────────
            hero_color = "#2C2C2A"
            st.markdown(f"""
            <div style='background:{hero_color}; border-radius:12px;
                        padding:20px 24px; margin-bottom:20px;'>
                <div style='font-size:11px; color:#888780;
                            text-transform:uppercase;
                            letter-spacing:.07em;'>
                    {dept} · Week {latest_week}
                </div>
                <div style='font-size:24px; font-weight:500;
                            color:#F1EFE8; margin:4px 0;'>{emp_name}</div>
                <div style='font-size:12px; color:#B4B2A9;'>
                    Team score: <strong style='color:
                    {"#E24B4A" if team_score < 45 else
                     "#f49052" if team_score < 70 else "#4caf7d"};'>
                    {team_score}</strong> ·
                    vs org avg: <strong style='color:
                    {"#E24B4A" if vs_org < 0 else "#4caf7d"};'>
                    {format_delta(vs_org)}</strong> ·
                    At risk: <strong style='color:#E24B4A;'>{at_risk}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── KPI strip ─────────────────────────────────────────────────────
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.metric("Team score",   team_score)
            with k2:
                st.metric("vs Org avg",   format_delta(vs_org))
            with k3:
                st.metric("Responded",    f"{responded} members")
            with k4:
                st.metric("At risk",      at_risk)

            # ── Team member scores ────────────────────────────────────────────
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Team member scores")
                members = latest_team[
                    ["name","composite_score","engagement_label"]
                ].sort_values("composite_score", ascending=False)

                for _, row in members.iterrows():
                    color = engagement_color(row["composite_score"])
                    st.markdown(f"""
                    <div style='display:flex; align-items:center;
                                gap:10px; margin-bottom:6px;'>
                        <span style='font-size:12px; color:#505050;
                                     flex:1;'>{row['name']}</span>
                        <div style='width:100px; height:6px;
                                    background:#f5e8d8; border-radius:3px;
                                    overflow:hidden;'>
                            <div style='width:{row["composite_score"]}%;
                                        height:100%; background:{color};
                                        border-radius:3px;'></div>
                        </div>
                        <span style='font-size:12px; font-weight:500;
                                     color:{color}; width:36px;'>
                            {row["composite_score"]}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                st.markdown("##### Team 5C breakdown")
                dims = ["clarity","connection","contribution","confidence","care"]
                for dim in dims:
                    avg_val = round(latest_team[dim].mean(), 1)
                    color   = engagement_color(avg_val * 10)
                    st.markdown(f"""
                    <div style='display:flex; align-items:center;
                                gap:10px; margin-bottom:6px;'>
                        <span style='width:90px; font-size:12px;
                                     color:#705040; text-align:right;
                                     text-transform:capitalize;'>{dim}</span>
                        <div style='flex:1; height:8px;
                                    background:#f5e8d8; border-radius:4px;
                                    overflow:hidden;'>
                            <div style='width:{avg_val*10}%; height:100%;
                                        background:{color};
                                        border-radius:4px;'></div>
                        </div>
                        <span style='font-size:12px; font-weight:500;
                                     color:#505050;
                                     width:28px;'>{avg_val}</span>
                    </div>
                    """, unsafe_allow_html=True)

                # Coaching nudge
                if at_risk > 0:
                    st.markdown(f"""
                    <div style='background:#FAEEDA; border-left:3px solid #f49052;
                                padding:10px 12px; margin-top:12px;
                                border-radius:0 8px 8px 0;'>
                        <div style='font-size:11px; font-weight:500;
                                    color:#633806;'>Coaching nudge</div>
                        <div style='font-size:11px; color:#854F0B;
                                    margin-top:3px; line-height:1.5;'>
                            {at_risk} member{"s" if at_risk > 1 else ""}
                            below threshold this week.
                            Review Care and Connection scores —
                            consider scheduling 1-on-1s.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    elif role == "HR":

        # ── HR home ───────────────────────────────────────────────────────────
        # Org-wide engagement summary, department heatmap,
        # flagged teams, intervention alerts, leaderboard snapshot.

        latest_week  = df_pulse["week_number"].max()
        latest_pulse = df_pulse[df_pulse["week_number"] == latest_week]

        org_score    = round(latest_pulse["composite_score"].mean(), 1)
        response_rate = round(
            len(latest_pulse) / len(df_employees) * 100, 1)
        at_risk_teams = latest_pulse.groupby("department").apply(
            lambda x: (x["engagement_label"] == "At Risk").mean()
        )
        flagged_depts = at_risk_teams[at_risk_teams > 0.3].index.tolist()

        # ── Hero banner ───────────────────────────────────────────────────────
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
                <div style='font-size:24px; font-weight:500;
                            color:#fff; margin:4px 0;'>{alert_msg}</div>
                <div style='font-size:12px; color:#AFA9EC;'>
                    {len(df_employees):,} employees ·
                    9 departments · MM Group
                </div>
            </div>
            <div style='text-align:right;'>
                <div style='font-size:42px; font-weight:500;
                            color:#f49052; line-height:1;'>{org_score}</div>
                <div style='font-size:11px; color:#AFA9EC;
                            margin-top:4px;'>org engagement score</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── KPI strip ─────────────────────────────────────────────────────────
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.metric("Org score",      org_score)
        with k2:
            st.metric("Response rate",  f"{response_rate}%")
        with k3:
            st.metric("At-risk depts",  len(flagged_depts))
        with k4:
            engaged_pct = round(
                (latest_pulse["engagement_label"]=="Engaged").mean()*100, 1)
            st.metric("Engaged",        f"{engaged_pct}%")
        with k5:
            avg_sentiment = round(
                latest_pulse["composite_score"].mean(), 1)
            st.metric("Avg composite",  avg_sentiment)

        # ── Department heatmap + flagged teams ────────────────────────────────
        col1, col2 = st.columns([1.6, 1])

        with col1:
            st.markdown("##### Department scores — latest week")
            import plotly.graph_objects as go

            dept_summary = latest_pulse.groupby("department")[
                ["clarity","connection","contribution","confidence","care"]
            ].mean().round(1)

            fig = go.Figure(data=go.Heatmap(
                z          = dept_summary.values,
                x          = ["Clarity","Connection",
                               "Contribution","Confidence","Care"],
                y          = dept_summary.index.tolist(),
                colorscale = [
                    [0.0, "#FCEBEB"],
                    [0.5, "#FAEEDA"],
                    [1.0, "#E1F5EE"],
                ],
                zmin = 1, zmax = 10,
                text = dept_summary.values.round(1),
                texttemplate = "%{text}",
                showscale    = False,
            ))
            fig.update_layout(
                height        = 260,
                margin        = dict(l=0, r=0, t=0, b=0),
                plot_bgcolor  = "#fffbf8",
                paper_bgcolor = "#fffbf8",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("##### Flagged departments")
            if not flagged_depts:
                st.success("No departments flagged this week.")
            else:
                for dept_name in flagged_depts:
                    dept_score = round(
                        latest_pulse[
                            latest_pulse["department"]==dept_name
                        ]["composite_score"].mean(), 1)
                    risk_pct   = round(at_risk_teams[dept_name]*100, 1)
                    st.markdown(f"""
                    <div style='display:flex; align-items:center;
                                justify-content:space-between;
                                padding:8px 0;
                                border-bottom:0.5px solid #f0d0b8;'>
                        <span style='font-size:12px;
                                     color:#505050;'>{dept_name}</span>
                        <span style='font-size:10px; font-weight:500;
                                     background:#FCEBEB; color:#791F1F;
                                     padding:2px 8px;
                                     border-radius:8px;'>
                            {risk_pct}% at risk
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Leaderboard snapshot ──────────────────────────────────────────
            st.markdown("##### Points leaderboard — top 5")
            # Approximate points from pulse completions only for now
            # Full points engine built in later modules
            pulse_counts = df_pulse.groupby(
                ["employee_id","name"]
            )["response_id"].count().reset_index()
            pulse_counts.columns = ["employee_id","name","submissions"]
            pulse_counts["points"] = pulse_counts["submissions"] * 20
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