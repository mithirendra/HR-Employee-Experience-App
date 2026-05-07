# ── pages/2_Wellbeing.py ──────────────────────────────────────────────────────
# Vibe — Wellbeing Index module
# Employee : personal wellbeing score, burnout risk, absenteeism trend
# Manager  : team burnout heatmap, absenteeism by member
# HR       : org-wide burnout risk, mental health signals, absenteeism trends

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import (
    load_employees, load_pulse,
    filter_pulse_by_role,
    engagement_color, format_delta,
    is_logged_in, get_role, get_emp_id, get_manager_name,
    apply_vibe_style,
)

# ── Guard ─────────────────────────────────────────────────────────────────────
if not is_logged_in():
    st.warning("Session expired. Please log in again.")
    if st.button("Go to login"):
        st.switch_page("app.py")
    st.stop()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Wellbeing — Vibe",
    page_icon  = "💚",
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

df_employees = load_employees()
df_pulse     = load_pulse()

# Filter pulse data based on role
df_pulse_role = filter_pulse_by_role(df_pulse, role, emp_id, mgr_name)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("## 💚 Wellbeing Index")
st.markdown("---")

# ── Burnout score calculation ─────────────────────────────────────────────────
# Burnout risk is derived from three signals:
# 1. Low composite engagement score
# 2. High absenteeism days
# 3. High overtime hours
# Each signal contributes to a burnout risk score 0-100
# 0-30 = Low, 31-60 = Moderate, 61-100 = High

def calculate_burnout(df):
    """
    Calculate burnout risk score for a DataFrame of pulse rows.
    Returns a score 0-100 and a label Low / Moderate / High.
    """
    if df.empty:
        return 0, "Low"

    # Signal 1 — low engagement pulls burnout up
    # Invert composite score — low score = high burnout contribution
    avg_composite  = df["composite_score"].mean()
    engagement_risk = max(0, (70 - avg_composite) / 70 * 40)

    # Signal 2 — absenteeism
    # Average absent days per week, scaled to 0-30
    avg_absent     = df["absent_days"].mean()
    absent_risk    = min(avg_absent / 3 * 30, 30)

    # Signal 3 — overtime
    # Average overtime hours per week, scaled to 0-30
    avg_overtime   = df["overtime_hours"].mean()
    overtime_risk  = min(avg_overtime / 10 * 30, 30)

    # Combined burnout score
    burnout_score  = round(engagement_risk + absent_risk + overtime_risk)
    burnout_score  = min(burnout_score, 100)

    # Label
    if burnout_score <= 30:
        label = "Low"
    elif burnout_score <= 60:
        label = "Moderate"
    else:
        label = "High"

    return burnout_score, label


# ── Route by role ─────────────────────────────────────────────────────────────
if role == "Employee":

    # ── Employee wellbeing view ───────────────────────────────────────────────
    my_pulse = df_pulse_role.copy()

    if my_pulse.empty:
        st.info("No wellbeing data found for your account.")
    else:
        # Calculate personal burnout score
        burnout_score, burnout_label = calculate_burnout(my_pulse)

        # Burnout colour — green/amber/red
        burnout_color = (
            "#4caf7d" if burnout_label == "Low" else
            "#f49052" if burnout_label == "Moderate" else
            "#E24B4A"
        )

        # ── Hero banner ───────────────────────────────────────────────────────
        st.markdown(f"""
        <div style='background:#085041; border-radius:12px;
                    padding:20px 24px; margin-bottom:20px;
                    display:flex; align-items:center;
                    justify-content:space-between;'>
            <div>
                <div style='font-size:11px; color:#9FE1CB;
                            text-transform:uppercase;
                            letter-spacing:.07em;'>
                    Your wellbeing
                </div>
                <div style='font-size:26px; font-weight:500;
                            color:#fff; margin:4px 0;'>{emp_name}</div>
                <div style='font-size:12px; color:#9FE1CB;'>
                    Burnout risk — {burnout_label}
                </div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:48px; font-weight:500;
                            color:{burnout_color};
                            line-height:1;'>{burnout_score}</div>
                <div style='font-size:11px; color:#9FE1CB;
                            margin-top:4px;'>Burnout risk score</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── KPI strip ─────────────────────────────────────────────────────────
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            # Average absent days per week
            avg_absent = round(my_pulse["absent_days"].mean(), 1)
            st.metric("Avg absent days", avg_absent)
            # st.caption("Average days absent per week")
        with k2:
            # Average overtime hours per week
            avg_overtime = round(my_pulse["overtime_hours"].mean(), 1)
            st.metric("Avg overtime hrs", avg_overtime)
            # st.caption("Average overtime hours per week")
        with k3:
            # Lowest dimension score — most at-risk area
            dims    = ["clarity","connection","contribution","confidence","care"]
            avg_dim = {d: my_pulse[d].mean() for d in dims}
            lowest  = min(avg_dim, key=avg_dim.get)
            st.metric("Lowest dimension", lowest.capitalize())
            st.caption("Your weakest 5C area over all weeks")
        with k4:
            # Weeks flagged At Risk
            at_risk_weeks = (my_pulse["engagement_label"] == "At Risk").sum()
            st.metric("At-risk weeks", at_risk_weeks)
            st.caption("Weeks your engagement score fell below 4")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            # ── Wellbeing trend — composite score over time ───────────────────
            st.markdown("##### Wellbeing trend — all weeks")
            fig = px.line(
                my_pulse.sort_values("week_number"),
                x                       = "week_date",
                y                       = "composite_score",
                markers                 = False,
                color_discrete_sequence = ["#4caf7d"],
            )
            # Add a reference line at 45 — below this is At Risk
            fig.add_hline(
                y           = 45,
                line_dash   = "dash",
                line_color  = "#E24B4A",
                annotation_text = "At risk threshold",
            )
            fig.update_layout(
                height        = 240,
                margin        = dict(l=0, r=0, t=0, b=0),
                plot_bgcolor  = "#fffbf8",
                paper_bgcolor = "#fffbf8",
                xaxis_title   = "",
                yaxis_title   = "",
                yaxis_range   = [0, 100],
                showlegend    = False,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # ── Absenteeism trend ─────────────────────────────────────────────
            st.markdown("##### Absenteeism — absent days per week")
            fig2 = px.bar(
                my_pulse.sort_values("week_number"),
                x                       = "week_date",
                y                       = "absent_days",
                color_discrete_sequence = ["#f49052"],
            )
            fig2.update_layout(
                height        = 240,
                margin        = dict(l=0, r=0, t=0, b=0),
                plot_bgcolor  = "#fffbf8",
                paper_bgcolor = "#fffbf8",
                xaxis_title   = "",
                yaxis_title   = "",
                showlegend    = False,
            )
            st.plotly_chart(fig2, use_container_width=True)


elif role == "Manager":

    # ── Manager wellbeing view ────────────────────────────────────────────────
    team_pulse = df_pulse_role.copy()

    if team_pulse.empty:
        st.info("No team wellbeing data found.")
    else:
        # Calculate burnout score for the whole team
        burnout_score, burnout_label = calculate_burnout(team_pulse)
        burnout_color = (
            "#4caf7d" if burnout_label == "Low" else
            "#f49052" if burnout_label == "Moderate" else
            "#E24B4A"
        )

         # ── Hero banner ───────────────────────────────────────────────────────
        st.markdown(f"""
        <div style='background:#085041; border-radius:12px;
                    padding:20px 24px; margin-bottom:20px;
                    display:flex; align-items:center;
                    justify-content:space-between;'>
            <div>
                <div style='font-size:11px; color:#9FE1CB;
                            text-transform:uppercase;
                            letter-spacing:.07em;'>
                    Team wellbeing · {dept}
                </div>
                <div style='font-size:26px; font-weight:500;
                            color:#fff; margin:4px 0;'>{emp_name}</div>
                <div style='font-size:12px; color:#9FE1CB;'>
                    Team burnout risk — {burnout_label}
                </div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:48px; font-weight:500;
                            color:{burnout_color};
                            line-height:1;'>{burnout_score}</div>
                <div style='font-size:11px; color:#9FE1CB;
                            margin-top:4px;'>Team burnout score</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── KPI strip ─────────────────────────────────────────────────────────
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            avg_absent = round(team_pulse["absent_days"].mean(), 1)
            st.metric("Avg absent days", avg_absent)
        with k2:
            avg_overtime = round(team_pulse["overtime_hours"].mean(), 1)
            st.metric("Avg overtime hrs", avg_overtime)
        with k3:
            # Count team members with high burnout
            member_burnout = team_pulse.groupby("employee_id").apply(
                lambda x: calculate_burnout(x)[0]
            )
            high_burnout = (member_burnout > 60).sum()
            st.metric("High burnout members", high_burnout)
        with k4:
            at_risk_pct = round(
                (team_pulse["engagement_label"] == "At Risk").mean() * 100)
            st.metric("At-risk %", f"{at_risk_pct}%")
            st.caption('Percentage of employees with engagement score below 45')

        st.markdown("---")

        # ── Member burnout heatmap ────────────────────────────────────────────
        st.markdown("##### Team member burnout risk")

        # Calculate burnout per member
        members      = team_pulse["name"].unique()
        member_stats = []

        for name in members:
            member_data   = team_pulse[team_pulse["name"] == name]
            score, label  = calculate_burnout(member_data)
            avg_absent    = round(member_data["absent_days"].mean(), 1)
            avg_overtime  = round(member_data["overtime_hours"].mean(), 1)
            avg_composite = round(member_data["composite_score"].mean())
            member_stats.append({
                "name":          name,
                "burnout_score": score,
                "burnout_label": label,
                "avg_absent":    avg_absent,
                "avg_overtime":  avg_overtime,
                "avg_composite": avg_composite,
            })

        # Sort by burnout score highest first
        member_stats = sorted(
            member_stats, key=lambda x: x["burnout_score"], reverse=True)

        for m in member_stats:
            color = (
                "#4caf7d" if m["burnout_label"] == "Low" else
                "#f49052" if m["burnout_label"] == "Moderate" else
                "#E24B4A"
            )
            st.markdown(f"""
            <div style='display:flex; align-items:center;
                        gap:12px; padding:8px 0;
                        border-bottom:0.5px solid #f0d0b8;'>
                <span style='font-size:12px; color:#505050;
                             flex:1;'>{m['name']}</span>
                <span style='font-size:11px; color:#a07050;
                             width:100px;'>
                    Absent: {m['avg_absent']}d <br>
                    OT: {m['avg_overtime']}h
                </span>
                <div style='width:80px; height:6px;
                            background:#f5e8d8; border-radius:3px;
                            overflow:hidden;'>
                    <div style='width:{m["burnout_score"]}%; height:100%;
                                background:{color};
                                border-radius:3px;'></div>
                </div>
                <span style='font-size:11px; font-weight:500;
                             color:{color}; width:60px;
                             text-align:right;'>
                    {m['burnout_label']}
                </span>
            </div>
            """, unsafe_allow_html=True)


elif role == "HR":

    # ── HR wellbeing view ─────────────────────────────────────────────────────
    st.markdown("##### Org-wide burnout risk by department")

    # Calculate burnout per department
    dept_stats = []
    for dept_name in df_pulse["department"].unique():
        dept_data     = df_pulse[df_pulse["department"] == dept_name]
        score, label  = calculate_burnout(dept_data)
        avg_absent    = round(dept_data["absent_days"].mean(), 1)
        avg_overtime  = round(dept_data["overtime_hours"].mean(), 1)
        dept_stats.append({
            "department":    dept_name,
            "burnout_score": score,
            "burnout_label": label,
            "avg_absent":    avg_absent,
            "avg_overtime":  avg_overtime,
        })

    # Sort by burnout score
    dept_stats = sorted(
        dept_stats, key=lambda x: x["burnout_score"], reverse=True)
    
    # ── KPI strip ─────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        high_burnout_depts = sum(
            1 for d in dept_stats if d["burnout_label"] == "High")
        st.metric("High burnout depts", high_burnout_depts)
        st.caption('Departments with burnout score above 60')
    with k2:
        org_absent = round(df_pulse["absent_days"].mean(), 1)
        st.metric("Org avg absent days", org_absent)
    with k3:
        org_overtime = round(df_pulse["overtime_hours"].mean(), 1)
        st.metric("Org avg overtime hrs", org_overtime)
    with k4:
        at_risk_pct = round(
            (df_pulse["engagement_label"] == "At Risk").mean() * 100)
        st.metric("Org at-risk %", f"{at_risk_pct}%")
        st.caption('Percentage of employees with engagement score below 45')


    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # ── Department burnout bar chart ──────────────────────────────────────
        st.markdown("##### Burnout risk score by department")
        dept_df = pd.DataFrame(dept_stats)
        fig = px.bar(
            dept_df,
            x                       = "burnout_score",
            y                       = "department",
            orientation             = "h",
            color                   = "burnout_score",
            color_continuous_scale  = ["#4caf7d","#f49052","#E24B4A"],
            range_color             = [0, 100],
            text                    = "burnout_score",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height              = 320,
            margin              = dict(l=0, r=0, t=0, b=0),
            plot_bgcolor        = "#fffbf8",
            paper_bgcolor       = "#fffbf8",
            showlegend          = False,
            coloraxis_showscale = False,
            xaxis_title         = "",
            yaxis_title         = "",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # ── Absenteeism by department ─────────────────────────────────────────
        st.markdown("##### Avg absenteeism by department")
        absent_df = pd.DataFrame(dept_stats).sort_values(
            "avg_absent", ascending=False)
        fig2 = px.bar(
            absent_df,
            x                       = "avg_absent",
            y                       = "department",
            orientation             = "h",
            color                   = "avg_absent",
            color_continuous_scale  = ["#4caf7d","#f49052","#E24B4A"],
            text                    = "avg_absent",
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(
            height              = 320,
            margin              = dict(l=0, r=0, t=0, b=0),
            plot_bgcolor        = "#fffbf8",
            paper_bgcolor       = "#fffbf8",
            showlegend          = False,
            coloraxis_showscale = False,
            xaxis_title         = "",
            yaxis_title         = "",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

     # ── Mental health signals ─────────────────────────────────────────────────
    # HR only — language pattern flags in open text feedback
    # Looks for negative keywords that may indicate mental health concerns
    st.markdown("##### Mental health signals — open text flags")
    st.markdown("""
    <div style='font-size:11px; color:#a07050; margin-bottom:12px;'>
        Based on keyword detection in open text feedback.
        Handle all flagged feedback with care and confidentiality.
    </div>
    """, unsafe_allow_html=True)

    # Keywords that may indicate mental health concerns
    MH_KEYWORDS = [
        "overwhelmed", "stressed", "anxious", "burnout",
        "exhausted", "struggling", "hopeless", "disconnected",
        "unsupported", "isolated", "pressure", "breaking point",
    ]

    # Filter feedback containing any of the keywords
    mh_flags = df_pulse[
        df_pulse["feedback"].notna() &
        df_pulse["feedback"].str.lower().str.contains(
            "|".join(MH_KEYWORDS), na=False)
    ][["department","feedback","week_date"]].sort_values(
        "week_date", ascending=False
    ).head(10)

    if mh_flags.empty:
        st.success("No mental health signals detected this period.")
    else:
        st.markdown(f"**{len(mh_flags)} flagged responses detected**")
        for _, row in mh_flags.iterrows():
            st.markdown(f"""
            <div style='background:#FCEBEB; border-radius:8px;
                        padding:10px 14px; margin-bottom:8px;
                        border-left:3px solid #E24B4A;'>
                <div style='font-size:11px; font-weight:500;
                            color:#791F1F; margin-bottom:3px;'>
                    {row['department']} ·
                    {row['week_date'].strftime('%d %b %Y')}
                </div>
                <div style='font-size:12px; color:#505050;
                            font-style:italic;'>
                    "{row['feedback']}"
                </div>
            </div>
            """, unsafe_allow_html=True)