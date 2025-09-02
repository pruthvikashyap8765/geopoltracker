import streamlit as st
from datetime import datetime
import plotly.express as px

# --- import page logic (no Streamlit inside those modules) ---
from widgets.main import get_country_summary


st.set_page_config(page_title="GEOPOLTRACKER", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")


def set_country(c: str):
    st.session_state.selected_country = c


def make_graph(indicator: str, summary):
    st.markdown("<br>", unsafe_allow_html=True)
    data = summary[indicator]
    min_year = int(data["Year"].min())
    max_year = int(data["Year"].max())
    year_range = st.slider(
        "Select year range",
        min_value=min_year,
        max_value=max_year,
        value=(max(min_year, max_year - 10), max_year),
        step=1,
        key=f"year_range_{indicator}"
    )
    filtered_data = data[(data["Year"] >= year_range[0]) & (data["Year"] <= year_range[1])]
    chart_df = filtered_data.set_index("Year")["Value"]
    fig = px.line(
        chart_df,
        x=chart_df.index,
        y=chart_df.values,
        labels={"x": "Year", "y": ""},
        title=indicator
    )

    st.plotly_chart(fig, use_container_width=False)




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
        <h1 style="text-align:center; margin-top:20px; padding:0">{country}</h2>
    """,
    unsafe_allow_html=True
)

col1,col2,col3 = st.columns([8,2,8])

with col1:
    make_graph("GDP growth (annual %)", summary[country])

with col3:  
    make_graph("Inflation rate (CPI %)", summary[country])
   



col1,col2,col3 = st.columns([8,2,8])

with col1:
    make_graph("GDP (current US$)", summary[country])

with col3:  
    make_graph("Unemployment rate (%)", summary[country])
