"""
Economic Indicator Dashboard for GEOPOLTRACKER
------------------------------------------------

This Streamlit app pulls selected macro‑economic indicators from the
World Bank’s public API and displays them for a chosen country.

Indicators included:

* **GDP growth (annual %)** – World Bank indicator `NY.GDP.MKTP.KD.ZG`
* **Inflation rate (CPI %)** – World Bank indicator `FP.CPI.TOTL.ZG`
* **Unemployment rate (%)** – World Bank indicator `SL.UEM.TOTL.ZS`
* **GDP (current US$)** – World Bank indicator `NY.GDP.MKTP.CD`

The app allows users to pick a country (by its ISO‑3 code) and
automatically fetches all four series, harmonises them into a tidy
DataFrame and renders simple line charts for each indicator.  A table
of the most recent available values is also displayed at the top of
each chart for quick reference.

To extend this app to other indicators or data providers, you can
modify the ``INDICATORS`` mapping below or add additional helper
functions.  The World Bank API is free to use and does not require an
API key.  More information about the API is available at
https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation.

Note: This script does not rely on any external packages beyond
``requests``, ``pandas``, and ``streamlit``.  To fetch market data
(e.g. currency exchange rates or stock indices), you can optionally
install ``yfinance`` locally and add another function to retrieve
those series.
"""

import datetime
import json
from typing import Dict

import pandas as pd
import requests
try:
    import streamlit as st  # type: ignore
except ImportError:
    # Provide a minimal shim when streamlit is unavailable (e.g. during testing).
    class _StreamlitShim:
        def __getattr__(self, name):
            # Return a no‑op function for any attribute to avoid crashes.
            def _noop(*args, **kwargs):
                return None
            return _noop

    st = _StreamlitShim()  # type: ignore


# Mapping of human‑readable indicator names to World Bank API codes.
# You can add more series here as needed.
INDICATORS: Dict[str, str] = {
    "GDP growth (annual %)": "NY.GDP.MKTP.KD.ZG",
    "Inflation rate (CPI %)": "FP.CPI.TOTL.ZG",
    "Unemployment rate (%)": "SL.UEM.TOTL.ZS",
    "GDP (current US$)": "NY.GDP.MKTP.CD",
}


def fetch_world_bank_series(country_code: str, indicator_code: str) -> Dict[int, float]:
    """Fetch a time series from the World Bank API.

    Parameters
    ----------
    country_code : str
        Two‑ or three‑letter ISO country code (e.g. ``'IND'`` for India).
    indicator_code : str
        World Bank indicator code (e.g. ``'NY.GDP.MKTP.KD.ZG'``).

    Returns
    -------
    Dict[int, float]
        Mapping from year to numeric value.  Years with missing values
        are omitted from the dictionary.
    """
    url = (
        f"https://api.worldbank.org/v2/country/{country_code}/indicator/"
        f"{indicator_code}?format=json&per_page=200"
    )
    resp = requests.get(url)
    if resp.status_code != 200:
        st.warning(f"Failed to fetch data for {indicator_code} (status code {resp.status_code})")
        return {}
    try:
        data = resp.json()[1]
    except (IndexError, json.JSONDecodeError):
        st.warning("Unexpected response structure from World Bank API")
        return {}
    series = {}
    for item in data:
        print(item)
        year_str = item.get("date")
        value = item.get("value")
        if year_str is not None and value is not None:
            try:
                year = int(year_str)
                series[year] = float(value)
            except (ValueError, TypeError):
                continue
    # print(data.keys())
    # print('\n\n\n\n\n\n\n\n\n-------------------------------------\n\n\n\n\n\n\n\n\n\n')
    return series


def assemble_dataframe(country_code: str, indicators: Dict[str, str]) -> pd.DataFrame:
    """Build a tidy DataFrame with indicator values over time for a country.

    The resulting DataFrame has columns: ``Year``, ``Indicator`` and
    ``Value``.  Only years present in any series are included.
    """
    records = []
    for name, code in indicators.items():
        series = fetch_world_bank_series(country_code, code)
        for year, value in series.items():
            records.append({"Year": year, "Indicator": name, "Value": value})
    df = pd.DataFrame(records)
    if not df.empty:
        df.sort_values(["Indicator", "Year"], inplace=True)
    return df


def main():
    st.set_page_config(page_title="Economic Indicator Dashboard", layout="wide")
    st.title("Economic Indicator Dashboard")
    st.write(
        "Use this tool to explore key macro‑economic indicators for any country. "
        "Data are pulled from the World Bank’s open API, which is free to use."
    )
    default_country = "IND"
    country_code = st.text_input(
        "Enter a country ISO‑3 code (e.g. IND for India, USA for United States):",
        value=default_country,
    ).strip().upper()
    if len(country_code) not in (2, 3):
        st.error("Please enter a 2‑ or 3‑letter ISO country code.")
        st.stop()
    df = assemble_dataframe(country_code, INDICATORS)
    if df.empty:
        st.error("No data returned. Please check the country code or try again later.")
        st.stop()
    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())
    st.sidebar.header("Filters")
    year_range = st.sidebar.slider(
        "Select year range",
        min_value=min_year,
        max_value=max_year,
        value=(max(min_year, max_year - 10), max_year),
        step=1,
    )
    filtered_df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
    st.subheader(f"Latest available values for {country_code}")
    latest = (
        filtered_df.sort_values("Year")
        .groupby("Indicator")
        .tail(1)
        .sort_values("Indicator")
    )
    latest_table = latest[["Indicator", "Year", "Value"]]
    st.table(latest_table)
    for indicator in INDICATORS.keys():
        indicator_df = filtered_df[filtered_df["Indicator"] == indicator]
        if indicator_df.empty:
            continue
        st.subheader(indicator)
        chart_df = indicator_df.set_index("Year")["Value"]
        st.line_chart(chart_df)


if __name__ == "__main__":
    main()