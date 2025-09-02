from typing import Dict
from .indicators import get_country_indicators
import logging

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(pathname)s:%(lineno)d] - %(message)s",
        handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
    )

COUNTRY_CODE:Dict[str, str] = {
    "India": "IND",
    "US": "USA",
    "China": "CHN",
    "Russia": "RUS"
}

def get_country_summary(country: str) -> Dict:

    data = get_country_indicators(COUNTRY_CODE[country])
    return {
        "GDP growth (annual %)": data.get("GDP growth (annual %)"),
        "GDP (current US$)": data.get("GDP (current US$)"),
        "Inflation rate (CPI %)": data.get("Inflation rate (CPI %)"),
        "Unemployment rate (%)": data.get("Unemployment rate (%)"),
    }
