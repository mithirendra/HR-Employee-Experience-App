# ── pages/6_Connect.py ────────────────────────────────────────────────────────
# Vibe — Connect module (Version 0 placeholder)
# Shows news feed, polls, anonymous feedback, communities
# Full logic in Version 1

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.helpers import (
    is_logged_in, get_role, get_emp_id, get_manager_name,
    load_employees, load_pulse,
    apply_vibe_style, show_sidebar, show_footer,
)

# ── Guard ─────────────────────────────────────────────────────────────────────
if not is_logged_in():
    st.warning("Session expired. Please log in again.")
    if st.button("Go to login"):
        st.switch_page("app.py")
    st.stop()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Connect — VIBE Demo | Mitma Consulting",
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
TODAY         = pd.Timestamp.today().normalize()
CURRENT_YEAR  = datetime.now().year
CURRENT_MONTH = datetime.now().strftime("%b")

emp_id   = get_emp_id()
mgr_name = get_manager_name()
df_employees = load_employees()
df_pulse     = load_pulse()

# Filter pulse to current year and up to today
df_pulse_current = df_pulse[
    (df_pulse["week_date"].dt.year == CURRENT_YEAR) &
    (df_pulse["week_date"] <= TODAY)
]

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("## 📣 Connect")
st.markdown("---")

# ── Coming soon banner ────────────────────────────────────────────────────────
st.markdown("""
<div style='background:#FAEEDA; border-left:4px solid #f49052;
            padding:12px 16px; border-radius:0 8px 8px 0;
            margin-bottom:20px;'>
    <div style='font-size:13px; font-weight:500; color:#633806;'>
        Full Connect module coming in Version 1
    </div>
    <div style='font-size:12px; color:#854F0B; margin-top:3px;'>
        News feed, polls, anonymous feedback, and social communities
        will be fully functional in the complete build.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📰 News feed", "📊 Polls", "💬 Feedback", "👥 Communities"])

with tab1:
    # ── Company news feed ─────────────────────────────────────────────────────
    st.markdown("##### MM Group news")

    # Static news items for demo
    NEWS = [
        {
            "title":     "Q1 2026 All-Hands recap",
            "date":      "15 Apr 2026",
            "body":      "Thank you to everyone who joined our Q1 All-Hands. "
                        "Key highlights: strong engagement scores across Marketing "
                        "and HR, new wellness programme launching in May, "
                        "and our Vibe Awards ceremony on 30 April.",
            "tag":       "Company update",
            "tag_color": "#E6F1FB",
            "tag_text":  "#0C447C",
        },
        {
            "title":     "New wellness programme — May 2026",
            "date":      "10 Apr 2026",
            "body":      "We are launching an 8-week wellness programme in May. "
                        "All employees can sign up via the Activities page. "
                        "Each session earns 25 Vibe points.",
            "tag":       "Wellness",
            "tag_color": "#E1F5EE",
            "tag_text":  "#085041",
        },
        {
            "title":     "Vibe Awards — nominations open",
            "date":      "05 Apr 2026",
            "body":      "Nominations are now open for the Vibe Awards. "
                        "Recognise a colleague who has gone above and beyond "
                        "this year. Submit your nomination via the Kudos page.",
            "tag":       "Recognition",
            "tag_color": "#FAEEDA",
            "tag_text":  "#633806",
        },
        {
            "title":     "Hybrid work policy update",
            "date":      "01 Apr 2026",
            "body":      "Effective 1 May 2026, all employees are required to be "
                        "in office a minimum of 3 days per week. Managers will "
                        "confirm team schedules by 15 April.",
            "tag":       "Policy",
            "tag_color": "#FAECE7",
            "tag_text":  "#712B13",
        },
    ]

    for news in NEWS:
        st.markdown(f"""
        <div style='background:#ffece1; border-radius:8px;
                    padding:14px 16px; margin-bottom:10px;'>
            <div style='display:flex; align-items:center;
                        justify-content:space-between;
                        margin-bottom:6px;'>
                <span style='font-size:13px; font-weight:500;
                             color:#505050;'>{news['title']}</span>
                <span style='font-size:10px; font-weight:500;
                             background:{news["tag_color"]};
                             color:{news["tag_text"]};
                             padding:2px 8px; border-radius:8px;'>
                    {news['tag']}
                </span>
            </div>
            <div style='font-size:11px; color:#a07050;
                        margin-bottom:6px;'>{news['date']}</div>
            <div style='font-size:12px; color:#505050;
                        line-height:1.6;'>{news['body']}</div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    # ── Polls ─────────────────────────────────────────────────────────────────
    st.markdown("##### Active polls")
    st.markdown("""
    <div style='font-size:12px; color:#a07050; margin-bottom:16px;'>
        Voting earns 5 pts per poll.
    </div>
    """, unsafe_allow_html=True)

    # Static polls for demo
    POLLS = [
        {
            "question": "What time works best for the January wellness sessions?",
            "options":  ["7:00am — before work",
                         "12:30pm — lunchtime",
                         "6:00pm — after work"],
            "key":      "poll_wellness",
        },
        {
            "question": "Which community would you most like to join?",
            "options":  ["Fitness and wellness",
                         "Books and learning",
                         "Parents and families",
                         "Tech and innovation"],
            "key":      "poll_community",
        },
    ]

    for poll in POLLS:
        st.markdown(f"""
        <div style='font-size:13px; font-weight:500;
                    color:#505050; margin-bottom:8px;'>
            {poll['question']}
        </div>
        """, unsafe_allow_html=True)

        already_voted = st.session_state.get(f"voted_{poll['key']}", False)

        if already_voted:
            st.success("✓ Vote submitted · +5 pts earned")
        else:
            vote = st.radio(
                label            = poll["question"],
                options          = poll["options"],
                label_visibility = "collapsed",
                key              = poll["key"],
            )
            if st.button("Submit vote · +5 pts",
                         key=f"btn_{poll['key']}"):
                st.session_state[f"voted_{poll['key']}"] = True
                st.rerun()

        st.markdown("---")

with tab3:
    # ── Anonymous feedback ────────────────────────────────────────────────────
    st.markdown("##### Share anonymous feedback")
    st.markdown("""
    <div style='background:#E1F5EE; border-radius:8px;
                padding:10px 14px; margin-bottom:16px;
                font-size:12px; color:#085041;'>
        Your feedback is completely anonymous.
        HR sees themes and trends only — not individual submissions.
        Submitting earns 15 pts.
    </div>
    """, unsafe_allow_html=True)

    feedback_topic = st.selectbox(
        "Topic",
        ["General feedback", "Workload and wellbeing",
         "Leadership and management", "Culture and inclusion",
         "Career development", "Tools and resources"],
    )

    feedback_text = st.text_area(
        "Your feedback",
        placeholder="Share your thoughts honestly. This is anonymous.",
        height=120,
    )

    already_submitted = st.session_state.get("anon_feedback_submitted", False)

    if already_submitted:
        st.success("✓ Feedback submitted this week · +15 pts earned")
    else:
        if st.button("Submit anonymously · +15 pts"):
            if not feedback_text.strip():
                st.error("Please write your feedback before submitting.")
            else:
                st.session_state["anon_feedback_submitted"] = True
                st.success("✓ Feedback submitted anonymously · +15 pts earned")
                st.rerun()

with tab4:
    # ── Social communities ────────────────────────────────────────────────────
    st.markdown("##### Communities")
    st.markdown("""
    <div style='font-size:12px; color:#a07050; margin-bottom:16px;'>
        Join a community to earn 10 pts.
        Post in a community to earn 5 pts (max 2 per week).
    </div>
    """, unsafe_allow_html=True)

    COMMUNITIES = [
        {"name": "Fitness and Wellness",   "members": 87,
         "desc": "Workout tips, wellness challenges, and healthy habits",
         "icon": "🏃"},
        {"name": "Books and Learning",     "members": 54,
         "desc": "Book recommendations, learning resources, and discussions",
         "icon": "📚"},
        {"name": "Parents and Families",   "members": 43,
         "desc": "Support, tips, and conversations for working parents",
         "icon": "👨‍👩‍👧"},
        {"name": "Tech and Innovation",    "members": 72,
         "desc": "Latest in tech, AI tools, and innovation at MM Group",
         "icon": "💡"},
        {"name": "Sustainability and ESG", "members": 38,
         "desc": "Green initiatives, ESG updates, and sustainability tips",
         "icon": "🌱"},
        {"name": "Young Professionals",    "members": 61,
         "desc": "Career tips, networking, and development for early careers",
         "icon": "🚀"},
    ]

    comm_cols = st.columns(2)
    for i, comm in enumerate(COMMUNITIES):
        joined_key = f"joined_{comm['name'].replace(' ','_')}"
        joined     = st.session_state.get(joined_key, False)

        with comm_cols[i % 2]:
            st.markdown(f"""
            <div style='background:{"#ffece1" if joined else "#fff"};
                        border:0.5px solid #f0d0b8;
                        border-radius:10px; padding:14px;
                        margin-bottom:10px;'>
                <div style='font-size:20px; margin-bottom:6px;'>
                    {comm['icon']}
                </div>
                <div style='font-size:13px; font-weight:500;
                            color:#505050;'>{comm['name']}</div>
                <div style='font-size:11px; color:#a07050;
                            margin-top:3px;'>
                    {comm['members']} members
                </div>
                <div style='font-size:11px; color:#505050;
                            margin-top:6px; line-height:1.5;'>
                    {comm['desc']}
                </div>
                <div style='margin-top:10px; font-size:11px;
                            font-weight:500;
                            color:{"#4caf7d" if joined else "#f49052"};'>
                    {"✓ Joined" if joined else "Join · +10 pts"}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if not joined:
                if st.button(f"Join {comm['name'].split()[0]}",
                             key=f"join_{i}"):
                    st.session_state[joined_key] = True
                    st.rerun()

show_footer()
