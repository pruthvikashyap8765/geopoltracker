import streamlit as st
from datetime import datetime
import streamlit.components.v1 as components


# --- import page logic (no Streamlit inside those modules) ---
from widgets.main import get_country_summary
from graph_builders.linegraph import make_line_graph
from graph_builders.bargraph import make_bar_graph


st.set_page_config(page_title="GEOPOLTRACKER", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")


def set_country(c: str):
    st.session_state.selected_country = c






# cache the data fetch
countries = ["India", "US", "China", "Russia"]

@st.cache_data(show_spinner=False)
def load_summary():
    master_summary = {}
    for country in countries:
        master_summary[country] = get_country_summary(country)

    return master_summary

summary = load_summary()




# ---------------- Header ----------------
st.markdown(
    """
    <h1 style="text-align:center; margin-bottom:0; padding:0">📊 GEOPOLTRACKER</h1>
    <h4 style="text-align:center; color:gray; margin-top:0; margin-bottom:20px">Economic & Market Intelligence</h4>
    """,
    unsafe_allow_html=True
)


# ---------------- Country Selection ----------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.button("India", use_container_width=True, on_click=set_country, args=("India",))
with col2:
    st.button("US", use_container_width=True, on_click=set_country, args=("US",))
with col3:
    st.button("China", use_container_width=True, on_click=set_country, args=("China",))
with col4:
    st.button("Russia", use_container_width=True, on_click=set_country, args=("Russia",))


country = st.session_state.get("selected_country", "India")


st.markdown(
    f"""
        <h1 style="text-align:center; margin-top:20px; padding:0">{country}</h1>
    """,
    unsafe_allow_html=True
)





#------------------ Country Overview ----------------
st.markdown(
    """
        <h3 style=" color:silver; margin-top:10px; margin-bottom:0; padding:0">Country Overview:</h3>
    """,
    unsafe_allow_html=True
)
st.divider()

col1,col2,col3 = st.columns([8,2,8])

with col1:
    make_line_graph("GDP (current US$)", summary[country], '$')

with col3:  
    make_bar_graph("GDP growth (annual %)", summary[country], "GDP Growth %")



col1,col2,col3 = st.columns([8,2,8])

with col1:
    make_bar_graph("Inflation rate (CPI %)", summary[country], "Inflation rate %")

with col3:  
    make_bar_graph("Unemployment rate (%)", summary[country], "Unemployment Rate %")





#------------------ Markets Overview ----------------

