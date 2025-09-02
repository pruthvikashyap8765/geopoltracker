from typing import Dict
import requests
import logging
import pandas as pd

INDICATORS:Dict[str, str] = {
    "GDP growth (annual %)": "NY.GDP.MKTP.KD.ZG",
    "Inflation rate (CPI %)": "FP.CPI.TOTL.ZG",
    "Unemployment rate (%)": "SL.UEM.TOTL.ZS",
    "GDP (current US$)": "NY.GDP.MKTP.CD",
}

def fetch_data_of_indicator(country_code: str, indicator_code: str, indicator: str) -> pd.DataFrame:
    url = (
        f"https://api.worldbank.org/v2/country/{country_code}/indicator/"
        f"{indicator_code}?format=json&per_page=200"
    )

    resp = requests.get(url)
    if resp.status_code != 200:
        logging.error(f"Error fetching data for {country_code} - {resp.status_code}")

    try:
        data = resp.json()[1]
    except Exception as e:
        logging.error(f"Error fetching data for {country_code} - {indicator}: {e}")
        return pd.DataFrame()
    
    series = []
    for item in data:
        year = item.get("date")
        value = item.get("value")
        if year is not None or value is not None:
            try:
                year = int(year)
                value = float(value)
            except Exception as e:
                logging.warning(f"Skipping invalid data point for {country_code} - {indicator}: {e}")
                continue

        try:
            series.append({
                "Indicator": indicator,
                "Year": year,
                "Value": value,
                
            })
        except Exception as e:
            logging.error(f"Error entering data to the table for {country_code} - {(k for k,v in INDICATORS.items() if v == indicator_code)}: {e}")
            continue
    
    df = pd.DataFrame(series)
    if not df.empty:
        df.sort_values(["Indicator", "Year"], inplace=True)
    return df



def get_country_indicators(country_code : str) -> Dict:

    master_data = {}
    for indicator, indicator_code in INDICATORS.items():
        fetched_data = fetch_data_of_indicator(country_code, indicator_code, indicator)
        if fetched_data.empty:
            logging.warning(f"No data fetched for {country_code} - {indicator}")
            continue
        master_data[indicator] = fetched_data
    return master_data



