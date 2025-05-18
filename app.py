import streamlit as st
from backtester import Backtester
from visualizer import plot_equity_curve, export_trades_to_csv
import pandas as pd

st.set_page_config(page_title="Forex Backtest Dashboard", layout="wide")

st.title("💹 Forex Backtester")

# --- Sidebar inputs ---
pair = st.sidebar.selectbox("Currency Pair", [
    "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD"
])
granularity = st.sidebar.selectbox("Timeframe", ["M1", "M5", "M15", "H1", "H4"])
days = st.sidebar.slider("Days of Historical Data", 1, 30, 7)
initial_balance = st.sidebar.number_input("Initial Balance (£)", value=1000)
risk_per_trade = st.sidebar.number_input("Risk Per Trade (£)", value=100)
trade_fee = st.sidebar.number_input("Fixed Trade Fee (£)", value=5)
max_spread = st.sidebar.number_input("Max Spread", value=0.00038, format="%.5f")

# --- New Tools ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Backtest Settings")
strategy_info = st.sidebar.expander("📘 Strategy Explanation")
strategy_info.write("""
- Buy when price < lower band, RSI < 40, and above MA.
- Sell when price > upper band, RSI > 60, and below MA.
- Uses ATR-based dynamic stop loss and position sizing.
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧮 Performance Tools")
show_details = st.sidebar.checkbox("Show Trade Table")
show_equity = st.sidebar.checkbox("Show Equity Curve", value=True)

if st.sidebar.button("🚀 Run Backtest"):
    with st.spinner("Running backtest..."):
        backtester = Backtester(
            pair=pair,
            granularity=granularity,
            days=days,
            initial_balance=initial_balance,
            risk_per_trade=risk_per_trade,
            trade_fee=trade_fee,
            max_spread=max_spread
        )
        trades = backtester.run()

        st.success("✅ Backtest Complete")

        st.markdown(f"### Results for {pair}")
        st.write(f"**Final Balance:** £{backtester.balance:.2f}")
        st.write(f"**Profit:** £{backtester.balance - backtester.initial_balance:.2f}")
        st.write(f"**Total Trades:** {len(trades)}")

        if trades:
            win_rate = 100 * sum(1 for t in trades if t.profit > 0) / len(trades)
            st.write(f"**Win Rate:** {win_rate:.1f}%")

            if show_equity:
                plot_equity_curve(trades, initial_balance=initial_balance)

            export_trades_to_csv(trades)

            if show_details:
                st.markdown("### 📋 Trade Log")
                st.dataframe(pd.DataFrame([t.__dict__ for t in trades]))