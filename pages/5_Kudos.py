# ── pages/5_Kudos.py ──────────────────────────────────────────────────────────
# Vibe — Kudos module (Version 0 placeholder)
# Shows Kudos wall, give Kudos form, and My Kudos history
# Full points wiring and analytics in Version 1

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.helpers import (
    load_employees, load_kudos,
    is_logged_in, get_role, get_emp_id, get_manager_name,
    apply_vibe_style, show_sidebar, show_footer,
    filter_kudos_by_role
)

# ── Guard ─────────────────────────────────────────────────────────────────────
if not is_logged_in():
    st.warning("Session expired. Please log in again.")
    if st.button("Go to login"):
        st.switch_page("app.py")
    st.stop()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Kudos — VIBE Demo | Mitma Consulting",
    page_icon  = "assets/mitma_favicon.png",
    layout     = "wide",
)
apply_vibe_style()

# ── Date references ───────────────────────────────────────────────────────────
TODAY         = pd.Timestamp.today().normalize()
CURRENT_YEAR  = datetime.now().year
CURRENT_MONTH = datetime.now().strftime("%b")


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

# ── Load data ─────────────────────────────────────────────────────────────────
emp_id       = get_emp_id()
mgr_name     = get_manager_name()
df_employees = load_employees()
df_kudos     = load_kudos()

# Filter Kudos to today — no future data
df_kudos_todate = df_kudos[df_kudos["date"] <= TODAY]

# Filter by role
df_kudos_role = filter_kudos_by_role(
    df_kudos_todate, role, emp_id, mgr_name, df_employees)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("## ⭐ Kudos")
st.markdown("---")

# Personal Kudos stats — current year only
kudos_received = len(df_kudos_todate[
    (df_kudos_todate["recipient_id"] == emp_id) &
    (df_kudos_todate["date"].dt.year == CURRENT_YEAR)
])
kudos_given = len(df_kudos_todate[
    (df_kudos_todate["giver_id"] == emp_id) &
    (df_kudos_todate["date"].dt.year == CURRENT_YEAR)
])

# ── Hero banner ───────────────────────────────────────────────────────────
st.markdown(f"""
<div style='background:#f49052; border-radius:12px;
            padding:20px 24px; margin-bottom:20px;
            display:flex; align-items:center;
            justify-content:space-between;'>
    <div>
        <div style='font-size:11px; color:#fff3ea;
                    text-transform:uppercase; letter-spacing:.07em;'>
            Recognition · Jan — {CURRENT_MONTH} {CURRENT_YEAR}
        </div>
        <div style='font-size:26px; font-weight:500;
                    color:#fff; margin:4px 0;'>{emp_name}</div>
        <div style='font-size:12px; color:#fff3ea;'>
            Give recognition · earn points · build culture
        </div>
    </div>
    <div style='display:flex; gap:20px;'>
        <div style='text-align:center;'>
            <div style='font-size:32px; font-weight:500;
                        color:#fff; line-height:1;'>{kudos_received}</div>
            <div style='font-size:10px; color:#fff3ea;
                        margin-top:3px;'>Received</div>
        </div>
        <div style='text-align:center;'>
            <div style='font-size:32px; font-weight:500;
                        color:#fff; line-height:1;'>{kudos_given}</div>
            <div style='font-size:10px; color:#fff3ea;
                        margin-top:3px;'>Given</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
# Three tabs — Kudos wall, Give Kudos, My Kudos
tab1, tab2, tab3 = st.tabs(["🌟 Kudos wall", "✉️ Give Kudos", "📬 My Kudos"])

with tab1:
    # ── Kudos wall — latest recognition org-wide ──────────────────────────────
    st.markdown("##### Latest recognition across MM Group")

    # Show latest 20 Kudos sorted by date
    wall_kudos = df_kudos_todate.sort_values(
            "date", ascending=False).head(100)

    for _, kudo in wall_kudos.head(20).iterrows():
        # Category colour
        cat_colors = {
            "Teamwork":             "#E1F5EE",
            "Innovation":           "#EEEDFE",
            "Leadership":           "#E6F1FB",
            "Customer Focus":       "#FAEEDA",
            "Going Above and Beyond":"#FAECE7",
            "Integrity":            "#E1F5EE",
            "Problem Solving":      "#FAEEDA",
            "Mentoring":            "#EEEDFE",
        }
        card_bg = cat_colors.get(kudo["category"], "#ffece1")

        st.markdown(f"""
        <div style='background:{card_bg}; border-radius:8px;
                    padding:12px 16px; margin-bottom:8px;'>
            <div style='display:flex; align-items:center;
                        justify-content:space-between;
                        margin-bottom:6px;'>
                <span style='font-size:12px; font-weight:500;
                             color:#505050;'>
                    {kudo['giver_name']}
                    <span style='color:#a07050;'> → </span>
                    {kudo['recipient_name']}
                </span>
                <span style='font-size:10px; font-weight:500;
                             background:#fff;
                             padding:2px 8px; border-radius:8px;
                             color:#505050;'>{kudo['category']}</span>
            </div>
            <div style='font-size:12px; color:#505050;
                        font-style:italic;'>
                "{kudo['message']}"
            </div>
            <div style='font-size:10px; color:#a07050; margin-top:6px;'>
                {kudo['giver_dept']} →
                {kudo['recipient_dept']} ·
                {kudo['date'].strftime('%d %b %Y')}
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    # ── Give Kudos form ───────────────────────────────────────────────────────
    st.markdown("##### Recognise a colleague")
    st.markdown("""
    <div style='font-size:12px; color:#a07050; margin-bottom:16px;'>
        Giving Kudos earns you 10 pts.
        Your colleague receives 15 pts.
    </div>
    """, unsafe_allow_html=True)

    # Recipient selector — all employees except self
    all_names = df_employees[
        df_employees["employee_id"] != emp_id
    ]["name"].sort_values().tolist()

    recipient = st.selectbox("Select colleague", all_names)

    # Category selector
    KUDOS_CATEGORIES = [
        "Teamwork", "Innovation", "Leadership", "Customer Focus",
        "Going Above and Beyond", "Integrity", "Problem Solving", "Mentoring",
    ]
    category = st.selectbox("Recognition category", KUDOS_CATEGORIES)

    # Message
    message = st.text_area(
        "Write your message",
        placeholder="Share what this person did and why it mattered...",
        height=100,
    )

    if st.button("Send Kudos · +10 pts for you · +15 pts for them"):
        if not message.strip():
            st.error("Please write a message before sending.")
        else:
            # Track in session state — full DB write in Version 1
            kudos_count = st.session_state.get("kudos_sent_today", 0)
            if kudos_count >= 3:
                st.warning("You have reached the maximum of 3 Kudos per week.")
            else:
                st.session_state["kudos_sent_today"] = kudos_count + 1
                st.success(
                    f"✓ Kudos sent to {recipient}! "
                    f"+10 pts for you · +15 pts for {recipient.split()[0]}")
                st.balloons()

with tab3:
    # ── My Kudos history ──────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Kudos I received")
        received = df_kudos_todate[
            df_kudos_todate["recipient_id"] == emp_id
        ].sort_values("date", ascending=False)

        if received.empty:
            st.info("No Kudos received yet.")
        else:
            st.metric("Total received", len(received))
            st.caption(f"+{len(received) * 15} pts earned")
            st.markdown("---")
            for _, kudo in received.head(10).iterrows():
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
                        {kudo['date'].strftime('%d %b %Y')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown("##### Kudos I gave")
        given = df_kudos_todate[
            df_kudos_todate["giver_id"] == emp_id
        ].sort_values("date", ascending=False)

        if given.empty:
            st.info("No Kudos given yet.")
        else:
            st.metric("Total given", len(given))
            st.caption(f"+{len(given) * 10} pts earned")
            st.markdown("---")
            for _, kudo in given.head(10).iterrows():
                st.markdown(f"""
                <div style='background:#E1F5EE; border-radius:8px;
                            padding:10px 14px; margin-bottom:8px;'>
                    <div style='font-size:12px; color:#505050;
                                font-style:italic;'>
                        "{kudo['message']}"
                    </div>
                    <div style='font-size:10px; color:#a07050;
                                margin-top:4px;'>
                        to {kudo['recipient_name']} ·
                        {kudo['category']} ·
                        {kudo['date'].strftime('%d %b %Y')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

show_footer()
