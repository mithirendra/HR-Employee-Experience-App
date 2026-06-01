# ── pages/4_Rewards.py ────────────────────────────────────────────────────────
# Vibe — Rewards module (Version 0 placeholder)
# Shows rewards catalogue UI and points balance
# Full redemption logic in Version 1

import streamlit as st
from utils.helpers import (
    load_employees, load_pulse, load_kudos,
    is_logged_in, get_role, get_emp_id, get_manager_name,
    apply_vibe_style, show_footer, show_sidebar,
)
from datetime import datetime
CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().strftime("%b")

# ── Guard ─────────────────────────────────────────────────────────────────────
if not is_logged_in():
    st.warning("Session expired. Please log in again.")
    if st.button("Go to login"):
        st.switch_page("app.py")
    st.stop()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Rewards — VIBE Demo | Mitma Consulting",
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

# ── Load data ─────────────────────────────────────────────────────────────────
emp_id   = get_emp_id()
df_pulse = load_pulse()
df_kudos = load_kudos()

# Calculate points balance
pulse_pts    = len(df_pulse[df_pulse["employee_id"] == emp_id]) * 20
kudos_given  = len(df_kudos[df_kudos["giver_id"] == emp_id]) * 10
kudos_rcvd   = len(df_kudos[df_kudos["recipient_id"] == emp_id]) * 15
total_pts    = pulse_pts + kudos_given + kudos_rcvd

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("## 🎁 Rewards")
st.markdown("---")

# ── Coming soon banner ────────────────────────────────────────────────────────
st.markdown("""
<div style='background:#FAEEDA; border-left:4px solid #f49052;
            padding:12px 16px; border-radius:0 8px 8px 0;
            margin-bottom:20px;'>
    <div style='font-size:13px; font-weight:500; color:#633806;'>
        Full rewards catalogue coming in Version 1
    </div>
    <div style='font-size:12px; color:#854F0B; margin-top:3px;'>
        Redemption logic, order history, and rewards analytics
        will be available in the full build.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Points balance ────────────────────────────────────────────────────────────
st.markdown("##### Your points balance")

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Total points",   f"{total_pts:,}")
    st.caption("Available to redeem")
with k2:
    st.metric("Pulse points",   f"{pulse_pts:,}")
    st.caption("From survey submissions")
with k3:
    st.metric("Kudos points",   f"{kudos_given + kudos_rcvd:,}")
    st.caption("Given and received")
with k4:
    # Points needed to next tier
    tiers = [100, 300, 600, 1200]
    next_tier = next((t for t in tiers if t > total_pts), None)
    if next_tier:
        st.metric("Next reward at", f"{next_tier:,} pts")
        st.caption(f"{next_tier - total_pts:,} pts to go")
    else:
        st.metric("Next reward at", "Premium")
        st.caption("You qualify for all tiers")

st.markdown("---")

# ── Redemption tiers ──────────────────────────────────────────────────────────
st.markdown("##### Redemption tiers")

TIERS = [
    {"tier": "Tier 1", "points": 500,  "reward": "Voucher S",
    "desc": "Food, entertainment, bookstore",
    "color": "#E1F5EE", "text": "#085041"},
    {"tier": "Tier 2", "points": 1000, "reward": "Voucher M",
    "desc": "Shopping, wellness, transport, learning",
    "color": "#FAEEDA", "text": "#633806"},
    {"tier": "Tier 3", "points": 1500, "reward": "Merchandise",
    "desc": "Branded merch, dining, fitness tracker",
    "color": "#FAECE7", "text": "#712B13"},
    {"tier": "Tier 4", "points": 2000, "reward": "Premium reward",
    "desc": "Staycation, iPad Mini, extra annual leave",
    "color": "#EEEDFE", "text": "#3C3489"},
]

cols = st.columns(4)
for col, tier in zip(cols, TIERS):
    unlocked = total_pts >= tier["points"]
    with col:
        st.markdown(f"""
        <div style='background:{tier["color"]};
                    border-radius:10px; padding:16px;
                    opacity:{"1" if unlocked else "0.5"};
                    text-align:center;'>
            <div style='font-size:24px; margin-bottom:8px;'>
                {"🔓" if unlocked else "🔒"}
            </div>
            <div style='font-size:13px; font-weight:500;
                        color:{tier["text"]};'>{tier["reward"]}</div>
            <div style='font-size:11px; color:{tier["text"]};
                        margin-top:4px;'>{tier["points"]:,} pts</div>
            <div style='font-size:10px; color:{tier["text"]};
                        margin-top:6px; opacity:.8;'>{tier["desc"]}</div>
            <div style='margin-top:10px; font-size:11px;
                        font-weight:500;
                        color:{"#4caf7d" if unlocked else tier["text"]};'>
                {"✓ Unlocked" if unlocked else "Locked"}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── Rewards catalogue preview ─────────────────────────────────────────────────
st.markdown("##### Catalogue preview")

CATALOGUE = [
    {"name": "Grab Food Voucher",        "pts": 100, "category": "Food"},
    {"name": "Starbucks eGift",          "pts": 100, "category": "Food"},
    {"name": "Zalora Shopping Voucher",  "pts": 300, "category": "Shopping"},
    {"name": "Wellness Spa Voucher",     "pts": 300, "category": "Wellness"},
    {"name": "Vibe Branded Merchandise","pts": 600, "category": "Merchandise"},
    {"name": "Weekend Staycation",       "pts": 1200,"category": "Experience"},
]

cat_cols = st.columns(3)
for i, item in enumerate(CATALOGUE):
    unlocked = total_pts >= item["pts"]
    with cat_cols[i % 3]:
        st.markdown(f"""
        <div style='background:{"#ffece1" if unlocked else "#f5f5f5"};
                    border-radius:8px; padding:12px 14px;
                    margin-bottom:10px;
                    opacity:{"1" if unlocked else "0.6"};'>
            <div style='font-size:12px; font-weight:500;
                        color:#505050;'>{item["name"]}</div>
            <div style='font-size:10px; color:#a07050;
                        margin-top:3px;'>{item["category"]}</div>
            <div style='display:flex; align-items:center;
                        justify-content:space-between;
                        margin-top:8px;'>
                <span style='font-size:12px; font-weight:500;
                             color:#f49052;'>{item["pts"]:,} pts</span>
                <span style='font-size:10px; font-weight:500;
                             color:{"#4caf7d" if unlocked else "#a07050"};'>
                    {"Redeem →" if unlocked else "Locked"}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

show_footer()