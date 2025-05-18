# live_trading.py
import streamlit as st
import requests
import time
from datetime import datetime

# --- LIVE CONFIG ---
OANDA_API_URL = "https://api-fxpractice.oanda.com/v3"
API_KEY = "YOUR_OANDA_API_KEY"
ACCOUNT_ID = "YOUR_OANDA_ACCOUNT_ID"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- STREAMLIT UI ---
st.set_page_config(page_title="Live Forex Price Feed", layout="wide")
st.title("📡 Live Forex Price Tracker")
st.markdown("Real-time price updates from OANDA.")

pair = st.selectbox("Currency Pair", ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD"])
refresh_rate = st.slider("Refresh Interval (sec)", 1, 60, 5)

price_display = st.empty()
timestamp_display = st.empty()

# --- PRICE FETCH FUNCTION ---
def get_live_price(pair):
    url = f"{OANDA_API_URL}/accounts/{ACCOUNT_ID}/pricing"
    params = {"instruments": pair}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        prices = response.json()["prices"][0]
        bid = float(prices["bids"][0]["price"])
        ask = float(prices["asks"][0]["price"])
        mid = round((bid + ask) / 2, 5)
        return mid, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    else:
        return None, "Error fetching price"

# --- LIVE LOOP ---
while True:
    price, timestamp = get_live_price(pair)
    price_display.metric(label=f"{pair} Mid Price", value=price)
    timestamp_display.text(f"Last updated: {timestamp} UTC")
    time.sleep(refresh_rate)