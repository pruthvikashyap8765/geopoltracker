import streamlit as st
import plotly.express as px

def make_bar_graph(indicator: str, summary, units):
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
    fig = px.bar(
        chart_df,
        x=chart_df.index,
        y=chart_df.values,
        labels={"x": "Year", "y": units},
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
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=False)
