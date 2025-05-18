import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from backtester import Backtester
from streamlit_autorefresh import st_autorefresh
import base64
import os
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Forex Backtester Dashboard", layout="wide")
st.title("💹 Forex Backtester Dashboard")
st.markdown("Analyze backtest performance, view trade details, and customize strategy parameters.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Backtest Controls")
pair = st.sidebar.selectbox("Currency Pair", ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD"])
granularity = st.sidebar.selectbox("Timeframe", ["M1", "M5", "M15", "H1", "H4"])
days = st.sidebar.slider("Days of Historical Data", min_value=1, max_value=30, value=7)
initial_balance = st.sidebar.number_input("Initial Balance (£)", value=1000)
risk_per_trade = st.sidebar.number_input("Risk Per Trade (£)", value=100)
trade_fee = st.sidebar.number_input("Trade Fee (£)", value=5)
max_spread = st.sidebar.number_input("Max Spread", value=0.00038, format="%.5f")
strategy_type = st.sidebar.selectbox("Strategy Type", ["RSI + MA", "Breakout", "MACD", "Stochastic", "Bollinger Bands", "ATR Reversal", "Custom"])

# --- AUTO REFRESH ---
refresh_interval = st.sidebar.slider("🔄 Auto Refresh (seconds)", 0, 300, 0, step=10)
if refresh_interval > 0:
    st_autorefresh(interval=refresh_interval * 1000, key="auto_refresh")

# Create folder for saved runs if it doesn't exist
os.makedirs("saved_runs", exist_ok=True)

# --- MANUAL RUN ---
if st.sidebar.button("▶️ Run Backtest"):
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
    df = pd.DataFrame([t.to_dict() for t in trades])

    if not df.empty:
        df["cumulative_balance"] = initial_balance + df["profit"].cumsum()

        # Save run with tag
        tag = st.text_input("💾 Enter a name to save this run", value=f"{pair}_{granularity}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        if st.button("✅ Save This Run"):
            filepath = f"saved_runs/{tag}.csv"
            df.to_csv(filepath, index=False)
            st.success(f"Backtest saved as: `{filepath}`")

        # --- FILTER ---
        trade_filter = st.selectbox("Filter Trades", ["All", "BUY", "SELL"])
        if trade_filter != "All":
            df = df[df["type"] == trade_filter]

        # --- RESULTS SUMMARY ---
        st.subheader("📊 Results Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Final Balance", f"£{df['cumulative_balance'].iloc[-1]:.2f}")
        col2.metric("Total Trades", len(df))
        win_rate = 100 * (df["profit"] > 0).mean()
        col3.metric("Win Rate", f"{win_rate:.1f}%")
        total_profit = df["profit"].sum()
        col4.metric("Total Profit", f"£{total_profit:.2f}")

        # --- TRADE LOG TABLE ---
        st.subheader("📄 Trade Log")
        st.dataframe(df)

        # --- CHARTS ---
        st.subheader("📈 Equity Curve")
        fig, ax = plt.subplots()
        ax.plot(df["cumulative_balance"], label="Equity Curve")
        ax.set_xlabel("Trade Number")
        ax.set_ylabel("Balance (£)")
        ax.grid(True)
        st.pyplot(fig)

        st.subheader("📊 Profit Distribution")
        fig2, ax2 = plt.subplots()
        ax2.hist(df["profit"], bins=20, color="skyblue", edgecolor="black")
        ax2.set_xlabel("Profit (£)")
        ax2.set_ylabel("Number of Trades")
        st.pyplot(fig2)

        # --- DOWNLOAD CSV ---
        csv = df.to_csv(index=False).encode()
        st.download_button("📥 Download CSV", csv, "backtest_results.csv", "text/csv")

        # --- DOWNLOAD CHARTS ---
        from io import BytesIO
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format="png")
        st.download_button("📸 Download Equity Curve", data=img_buffer.getvalue(), file_name="equity_curve.png", mime="image/png")

    else:
        st.warning("⚠️ No trades were made. Try adjusting your strategy filters or timeframe.")

# --- LOAD SAVED RUNS FOR COMPARISON ---
saved_files = [f for f in os.listdir("saved_runs") if f.endswith(".csv")]
if saved_files:
    st.subheader("📂 Compare Saved Backtests")
    selected = st.multiselect("Select backtests to compare", saved_files)

    if selected:
        tabs = st.tabs(selected)
        for i, filename in enumerate(selected):
            with tabs[i]:
                run_df = pd.read_csv(f"saved_runs/{filename}")
                st.write(f"📁 `{filename}`")
                st.dataframe(run_df)

                st.metric("Final Balance", f"£{run_df['cumulative_balance'].iloc[-1]:.2f}")
                st.metric("Total Trades", len(run_df))
                st.metric("Win Rate", f"{(run_df['profit'] > 0).mean() * 100:.1f}%")

                # Chart
                fig, ax = plt.subplots()
                ax.plot(run_df["cumulative_balance"])
                ax.set_title("Equity Curve")
                ax.set_xlabel("Trade #")
                ax.set_ylabel("£ Balance")
                st.pyplot(fig)