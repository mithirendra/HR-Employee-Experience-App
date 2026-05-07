# ── pages/1_Pulse_Survey.py ───────────────────────────────────────────────────
# Vibe — Pulse Survey module
# Employee : submit weekly pulse form
# Manager  : team response tracker + sentiment + driver analysis
# HR       : org-wide response rates + sentiment + driver analysis

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import (
    load_employees, load_pulse,
    filter_pulse_by_role,
    engagement_color, format_delta,
    is_logged_in, get_role, get_emp_id, get_manager_name, apply_vibe_style
)

# ── Guard — redirect to login if not logged in ────────────────────────────────
# st.stop() halts execution so nothing else renders
if not is_logged_in():
    st.warning("Session expired. Please log in again.")
    if st.button("Go to login"):
        st.switch_page("app.py")
    st.stop()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Pulse Survey — Vibe",
    page_icon  = "📊",
    layout     = "wide",
)

# ── Same CSS as app.py — keeps styling consistent across all pages ────────────
apply_vibe_style()

# ── Sidebar — same as app.py ──────────────────────────────────────────────────
# Repeated on every page to keep navigation consistent
role     = get_role()
emp_name = st.session_state.get("emp_name", "")
dept     = st.session_state.get("department", "")

role_colors = {
    "Employee": ("#E1F5EE", "#085041"),
    "Manager":  ("#E6F1FB", "#0C447C"),
    "HR":       ("#FAECE7", "#712B13"),
}
bg, fg = role_colors.get(role, ("#eee", "#333"))

with st.sidebar:
    st.markdown("""
    <div style='padding:8px 0 12px;'>
        <span style='font-size:20px; font-weight:500;
                     color:#2C2C2A;'>🔵 Vibe</span>
        <div style='font-size:10px; color:#a07050; margin-top:2px;'>
            Employee Experience Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown(f"""
    <div style='margin-bottom:12px;'>
        <div style='font-size:13px; font-weight:500;
                    color:#2C2C2A;'>{emp_name}</div>
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

    st.markdown("**Navigate**")
    st.page_link("app.py",                  label="🏠  Home")
    st.page_link("pages/1_Pulse_Survey.py", label="📊  Pulse Survey")
    st.page_link("pages/2_Wellbeing.py",    label="💚  Wellbeing")
    st.page_link("pages/3_Activities.py",   label="🎯  Activities")
    st.page_link("pages/4_Rewards.py",      label="🎁  Rewards")
    st.page_link("pages/5_Kudos.py",        label="⭐  Kudos")
    st.page_link("pages/6_Connect.py",      label="📣  Connect")

    st.divider()

    if st.button("Sign out"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("app.py")

# ── Load data ─────────────────────────────────────────────────────────────────
emp_id   = get_emp_id()
mgr_name = get_manager_name()

df_employees  = load_employees()
df_pulse      = load_pulse()

# Filter pulse data based on role
df_pulse_role = filter_pulse_by_role(df_pulse, role, emp_id, mgr_name)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("## 📊 Pulse Survey")
st.markdown("---")

# ── Route by role ─────────────────────────────────────────────────────────────
if role == "Employee":

    # ── Employee view — submit weekly pulse ───────────────────────────────────
    # Shows the 5C survey form + open text + submission button
    # After submission, shows confirmation and points earned

    latest_week = df_pulse["week_number"].max()

    # Check if employee already submitted this week
    # Track submission in session state instead of checking the CSV
    # This way the form always shows on first visit this session
    submitted_key     = f"submitted_w{latest_week}_{emp_id}"
    already_submitted = st.session_state.get(submitted_key, False)

    if already_submitted:
        # ── Already submitted — show their scores ─────────────────────────────
        st.success(f"✓ You submitted your pulse for week {latest_week}. Well done — +20 pts earned.")

        # Show their latest scores
        latest = df_pulse_role[
            df_pulse_role["week_number"] == latest_week
        ].iloc[0]

        st.markdown("##### Your scores this week")

        # Display 5C scores as metric cards
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Clarity",      latest["clarity"])
            st.caption("I understand what is expected of me")
        with c2:
            st.metric("Connection",   latest["connection"])
            st.caption("I feel connected to my team and organisation")
        with c3:
            st.metric("Contribution", latest["contribution"])
            st.caption("My work makes a meaningful difference")
        with c4:
            st.metric("Confidence",   latest["confidence"])
            st.caption("I have the tools and support to do my job well")
        with c5:
            st.metric("Care",         latest["care"])
            st.caption("My manager genuinely cares about my wellbeing")

        # Show their open text if they submitted one
        if pd.notna(latest["feedback"]) and latest["feedback"] != "":
            st.markdown("##### Your feedback this week")
            st.markdown(f"""
            <div style='background:#ffece1; border-radius:8px;
                        padding:12px 16px; font-style:italic;
                        color:#505050; font-size:13px;'>
                "{latest['feedback']}"
            </div>
            """, unsafe_allow_html=True)

    else:
        # ── Not yet submitted — show the survey form ──────────────────────────
        st.markdown(f"##### Week {latest_week} pulse — please rate each dimension 1 to 10")
        st.markdown("""
        <div style='font-size:12px; color:#a07050; margin-bottom:16px;'>
            1 = Strongly disagree · 10 = Strongly agree
        </div>
        """, unsafe_allow_html=True)

        # Each dimension gets a slider — 1 to 10
        clarity = st.slider(
            "🎯 Clarity — I understand what is expected of me",
            min_value=1, max_value=10, value=7)

        connection = st.slider(
            "🤝 Connection — I feel connected to my team and organisation",
            min_value=1, max_value=10, value=7)

        contribution = st.slider(
            "💡 Contribution — my work makes a meaningful difference",
            min_value=1, max_value=10, value=7)

        confidence = st.slider(
            "💪 Confidence — I have the tools and support to do my job well",
            min_value=1, max_value=10, value=7)

        care = st.slider(
            "❤️ Care — my manager genuinely cares about my wellbeing",
            min_value=1, max_value=10, value=7)

        st.markdown("##### Open feedback — optional")
        feedback = st.text_area(
            label       = "Share anything on your mind this week",
            placeholder = "How are you feeling? What could be better?",
            height      = 100,
        )

        # Show live composite score as user adjusts sliders
        composite = round((clarity + connection + contribution +
                           confidence + care) / 5 * 10)
        color     = engagement_color(composite)

        st.markdown(f"""
        <div style='background:#ffece1; border-radius:8px;
                    padding:12px 16px; margin:16px 0;
                    display:flex; align-items:center;
                    justify-content:space-between;'>
            <span style='font-size:13px; color:#705040;'>
                Your composite score this week
            </span>
            <span style='font-size:24px; font-weight:500;
                         color:{color};'>{composite}</span>
        </div>
        """, unsafe_allow_html=True)

        # Submit button
        if st.button("Submit pulse · +20 pts"):
            # Mark as submitted in session state
            st.session_state[submitted_key] = True
            # Add points to session state balance
            current_pts = st.session_state.get("points", 0)
            st.session_state["points"] = current_pts + 20
            st.success("✓ Pulse submitted successfully! +20 pts added to your balance.")
            st.balloons()
            st.rerun()

elif role == "Manager":

    # ── Manager view — team response tracker + sentiment + driver analysis ────
    latest_week = df_pulse["week_number"].max()
    latest_team = df_pulse_role[df_pulse_role["week_number"] == latest_week]

    # ── Response tracker ──────────────────────────────────────────────────────
    st.markdown("##### Team pulse response — week " + str(latest_week))

    # Get all employees under this manager
    team_members = df_employees[
        df_employees["manager"] == mgr_name
    ][["employee_id","name"]].copy()

    # Mark who has responded this week
    responded_ids = latest_team["employee_id"].tolist()
    team_members["responded"] = team_members["employee_id"].isin(responded_ids)

    # Response rate
    response_rate = round(len(responded_ids) / len(team_members) * 100)

    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("Response rate",  f"{response_rate}%")
    with r2:
        st.metric("Responded",      len(responded_ids))
    with r3:
        st.metric("Pending",        len(team_members) - len(responded_ids))

    st.markdown("---")

    # Show each team member with responded/pending status
    st.markdown("##### Member status")
    for _, member in team_members.iterrows():
        status_color = "#4caf7d" if member["responded"] else "#E24B4A"
        status_text  = "✓ Responded" if member["responded"] else "⏳ Pending"
        st.markdown(f"""
        <div style='display:flex; align-items:center;
                    justify-content:space-between;
                    padding:7px 0;
                    border-bottom:0.5px solid #f0d0b8;'>
            <span style='font-size:12px;
                         color:#505050;'>{member['name']}</span>
            <span style='font-size:11px; font-weight:500;
                         color:{status_color};'>{status_text}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Driver analysis ───────────────────────────────────────────────────────
    # Shows which of the 5C dimensions score lowest for the team
    st.markdown("##### Team dimension driver analysis")

    if latest_team.empty:
        st.info("No responses yet this week.")
    else:
        dims     = ["clarity","connection","contribution","confidence","care"]
        avg_dims = {dim: round(latest_team[dim].mean(), 1) for dim in dims}

        # Sort dimensions lowest to highest — worst drivers at top
        sorted_dims = sorted(avg_dims.items(), key=lambda x: x[1])

        for dim, val in sorted_dims:
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

    st.markdown("---")

    # ── Sentiment summary ─────────────────────────────────────────────────────
    # Shows open text feedback from the team this week
    st.markdown("##### Team feedback this week")

    team_feedback = latest_team[
        latest_team["feedback"].notna() &
        (latest_team["feedback"] != "")
    ]["feedback"].tolist()

    if not team_feedback:
        st.info("No open text feedback submitted this week.")
    else:
        for fb in team_feedback[:5]:  # show max 5 to keep it readable
            st.markdown(f"""
            <div style='background:#ffece1; border-radius:8px;
                        padding:10px 14px; margin-bottom:8px;
                        font-size:12px; color:#505050;
                        font-style:italic;'>
                "{fb}"
            </div>
            """, unsafe_allow_html=True)

elif role == "HR":

    # ── HR view — org-wide response rates + sentiment + driver analysis ───────
    latest_week  = df_pulse["week_number"].max()
    latest_pulse = df_pulse[df_pulse["week_number"] == latest_week]

    # ── Response rate by department ───────────────────────────────────────────
    st.markdown("##### Response rates by department — week " + str(latest_week))

    # Count responses per department this week
    dept_responses = latest_pulse.groupby("department").size().reset_index()
    dept_responses.columns = ["department", "responses"]

    # Count total employees per department
    dept_total = df_employees.groupby("department").size().reset_index()
    dept_total.columns = ["department", "total"]

    # Merge and calculate response rate
    dept_rate = dept_responses.merge(dept_total, on="department")
    dept_rate["rate"] = round(dept_rate["responses"] / dept_rate["total"] * 100)
    dept_rate = dept_rate.sort_values("rate", ascending=False)

    # Overall response rate metrics
    r1, r2, r3 = st.columns(3)
    with r1:
        overall_rate = round(len(latest_pulse) / len(df_employees) * 100)
        st.metric("Org response rate", f"{overall_rate}%")
    with r2:
        st.metric("Responses received", len(latest_pulse))
    with r3:
        st.metric("Pending",            len(df_employees) - len(latest_pulse))

    st.markdown("---")

    # Bar chart of response rates by department
    fig = px.bar(
        dept_rate,
        x                      = "rate",
        y                      = "department",
        orientation            = "h",           # horizontal bars
        color                  = "rate",
        color_continuous_scale = ["#E24B4A", "#f49052", "#4caf7d"],
        range_color            = [0, 100],
        text                   = "rate",
        labels                 = {"rate": "Response rate %",
                                   "department": ""},
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(
        height        = 320,
        margin        = dict(l=0, r=0, t=0, b=0),
        plot_bgcolor  = "#fffbf8",
        paper_bgcolor = "#fffbf8",
        showlegend    = False,
        coloraxis_showscale = False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Org-wide driver analysis ──────────────────────────────────────────────
    st.markdown("##### Org-wide dimension driver analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Average 5C scores across the whole org this week
        dims     = ["clarity","connection","contribution","confidence","care"]
        avg_dims = {dim: round(latest_pulse[dim].mean(), 1) for dim in dims}
        sorted_dims = sorted(avg_dims.items(), key=lambda x: x[1])

        for dim, val in sorted_dims:
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
        # Engagement label distribution — Engaged / Neutral / At Risk
        label_counts = latest_pulse["engagement_label"].value_counts()
        fig = px.pie(
            values = label_counts.values,
            names  = label_counts.index,
            color  = label_counts.index,
            color_discrete_map = {
                "Engaged": "#4caf7d",
                "Neutral": "#f49052",
                "At Risk": "#E24B4A",
            },
        )
        fig.update_layout(
            height        = 260,
            margin        = dict(l=0, r=0, t=0, b=0),
            paper_bgcolor = "#fffbf8",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Sample open text feedback ─────────────────────────────────────────────
    st.markdown("##### Sample open text feedback this week")

    # Show a sample from each engagement label
    for label, color in [("At Risk","#FCEBEB"),
                          ("Neutral","#FAEEDA"),
                          ("Engaged","#E1F5EE")]:
        sample = latest_pulse[
            (latest_pulse["engagement_label"] == label) &
            (latest_pulse["feedback"].notna()) &
            (latest_pulse["feedback"] != "")
        ]["feedback"].head(2).tolist()

        if sample:
            st.markdown(f"**{label}**")
            for fb in sample:
                st.markdown(f"""
                <div style='background:{color}; border-radius:8px;
                            padding:10px 14px; margin-bottom:8px;
                            font-size:12px; color:#505050;
                            font-style:italic;'>
                    "{fb}"
                </div>
                """, unsafe_allow_html=True)