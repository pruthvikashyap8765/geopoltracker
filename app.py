import streamlit as st
from datetime import datetime

# --- import page logic (no Streamlit inside those modules) ---


st.set_page_config(page_title="GEOPOLTRACKER", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# ---------------- Header ----------------
st.markdown(
    """
    <h1 style="text-align:center; margin-bottom:0; padding:0">📊 GEOPOLTRACKER</h1>
    <h4 style="text-align:center; color:gray; margin-top:0; margin-bottom:20px">Economic & Market Intelligence</h4>
    """,
    unsafe_allow_html=True
)


