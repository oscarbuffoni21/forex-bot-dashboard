import requests
from datetime import datetime, timedelta

# --- OANDA API Setup ---
API_KEY = "29311d57933f296890c32f56286ed54f-801350f3b7ce5aebe90fb3c8633d0e9d"
OANDA_API_URL = "https://api-fxpractice.oanda.com/v3"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- Candle Fetching Function ---
def get_historical_candles(pair="EUR_USD", granularity="M5", days=7):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    url = f"{OANDA_API_URL}/instruments/{pair}/candles"
    params = {
        "from": start_time.isoformat("T") + "Z",
        "to": end_time.isoformat("T") + "Z",
        "granularity": granularity,
        "price": "M"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    try:
        candles = response.json()["candles"]
        return [
            {
                "time": c["time"],
                "open": float(c["mid"]["o"]),
                "high": float(c["mid"]["h"]),
                "low": float(c["mid"]["l"]),
                "close": float(c["mid"]["c"])
            }
            for c in candles if c["complete"]
        ]
    except Exception as e:
        print("⚠️ Error getting candles:", e)
        return []

# ✅ Export for module use
__all__ = ["get_historical_candles"]