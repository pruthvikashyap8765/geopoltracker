import streamlit as st
from datetime import datetime
import plotly.express as px

# --- import page logic (no Streamlit inside those modules) ---
from widgets.main import get_country_summary


st.set_page_config(page_title="GEOPOLTRACKER", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")


def set_country(c: str):
    st.session_state.selected_country = c


def make_graph(indicator: str, summary):
    st.markdown(
        """
        <br>
        <h3>""" + indicator + """</h3>
        """, unsafe_allow_html=True
    )

    data = summary[indicator]

    min_year = int(data["Year"].min())
    max_year = int(data["Year"].max())

    # --- average options (checkboxes) ---
    opt_col1, opt_col2 = st.columns([1, 1])
    with opt_col1:
        show_mean = st.checkbox("Show mean", value=True, key=f"mean_chk_{indicator}")
    with opt_col2:
        show_roll = st.checkbox("Show rolling avg", value=True, key=f"roll_chk_{indicator}")


    sld_col1,sld_col2,sld_col3 = st.columns([8,1,8])
    with sld_col1:
        year_range = st.slider(
            "Select year range",
            min_value=min_year,
            max_value=max_year,
            value=(max(min_year, max_year - 10), max_year),
            step=1,
            key=f"year_range_{indicator}",
        )

    filtered_data = data[(data["Year"] >= year_range[0]) & (data["Year"] <= year_range[1])]
    chart_df = filtered_data.set_index("Year")["Value"]

    with sld_col3:
        rolling_win = st.select_slider(
            "Rolling average (years)",
            options=[0, 3, 5, 10],
            value=5,
            key=f"roll_win_{indicator}",
            disabled=not show_roll,   # disable window when rolling avg is off
        )

    # --- base chart ---
    fig = px.line(
        chart_df,
        x=chart_df.index,
        y=chart_df.values,
        labels={"x": "Year", "y": ""},
    )

    # 1) horizontal mean line
    if show_mean and len(chart_df):
        mean_val = float(chart_df.mean())
        fig.add_hline(
            y=mean_val,
            line_dash="dot",
            line_color="silver",
            annotation_text=f"Avg: {mean_val:.2f}",
            annotation_position="top left",
        )

    # 2) rolling average curve
    if show_roll and rolling_win and rolling_win > 0 and len(chart_df):
        roll = chart_df.rolling(rolling_win, min_periods=1).mean()
        fig.add_scatter(
            x=roll.index,
            y=roll.values,
            name=f"{rolling_win}-yr avg",
            mode="lines",
            line=dict(color="steelblue", width=2, dash="dash")
        )

    fig.update_layout(
        title_font=dict(size=24),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
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
        <h1 style="text-align:center; margin-top:20px; padding:0">{country}</h1>

        <h3 style=" color:silver; margin-top:10px; margin-bottom:0; padding:0">Economic Indicators:</h3>
    """,
    unsafe_allow_html=True
)
st.divider()

col1,col2,col3 = st.columns([8,2,8])

with col1:
    make_graph("GDP (current US$)", summary[country])

with col3:  
    make_graph("GDP growth (annual %)", summary[country])

   



col1,col2,col3 = st.columns([8,2,8])

with col1:
    make_graph("Inflation rate (CPI %)", summary[country])

with col3:  
    make_graph("Unemployment rate (%)", summary[country])
