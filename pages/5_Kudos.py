import streamlit as st
from utils.helpers import is_logged_in, get_role

if not is_logged_in():
    st.warning("Please log in from the home page.")
    st.stop()

st.set_page_config(page_title="Kudos — Vibe", page_icon="⭐", layout="wide")

role = get_role()

st.markdown("## ⭐ Kudos")
st.markdown("---")
st.info("This module is coming soon.")