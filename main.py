import requests
import statistics
import matplotlib.pyplot as plt
import csv
from datetime import datetime, timedelta

# --- Setup ---
API_KEY       = "29311d57933f296890c32f56286ed54f-801350f3b7ce5aebe90fb3c8633d0e9d"
ACCOUNT_ID    = "101-004-31712326-001"
OANDA_API_URL = "https://api-fxpractice.oanda.com/v3"
PAIR          = "EUR_USD"
GRANULARITY   = "M5"
MAX_SPREAD    = 0.00038
RISK_PER_TRADE= 100     # £ risk per trade
TRADE_FEE     = 5       # Fixed commission fee per trade

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_historical_candles(pair=PAIR, granularity=GRANULARITY, days=7):
    end_time   = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    url        = f"{OANDA_API_URL}/instruments/{pair}/candles"
    params     = {
        "from": start_time.isoformat("T") + "Z",
        "to":   end_time.isoformat("T") + "Z",
        "granularity": granularity,
        "price":       "M"
    }
    resp = requests.get(url, headers=HEADERS, params=params)
    try:
        candles = resp.json()["candles"]
        return [
            {
                "time":  c["time"],
                "open":  float(c["mid"]["o"]),
                "high":  float(c["mid"]["h"]),
                "low":   float(c["mid"]["l"]),
                "close": float(c["mid"]["c"])
            }
            for c in candles if c["complete"]
        ]
    except Exception as e:
        print("⚠️ Error fetching candles:", e)
        return []

def compute_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i-1]
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    return 100 - (100 / (1 + rs))

def get_moving_average(prices, period=50):
    return sum(prices[-period:]) / period if len(prices) >= period else None

def compute_atr(candles, period=14):
    if len(candles) < period + 1:
        return None
    trs = []
    for i in range(1, len(candles)):
        high, low = candles[i]['high'], candles[i]['low']
        prev = candles[i-1]['close']
        trs.append(max(high - low, abs(high - prev), abs(low - prev)))
    return sum(trs[-period:]) / period

def simulate_exit(i, candles, entry, tp, sl, typ, atr, atr_mult=1.2):
    stop = sl
    for j in range(1, 11):
        if i+j >= len(candles): break
        hi, lo = candles[i+j]['high'], candles[i+j]['low']
        if typ == "BUY":
            if hi - entry >= 0.5 * atr:
                stop = max(stop, hi - atr * atr_mult)
            if lo <= stop: return stop, "stop_loss"
            if hi >= tp: return tp,   "take_profit"
        else:
            if entry - lo >= 0.5 * atr:
                stop = min(stop, lo + atr * atr_mult)
            if hi >= stop: return stop, "stop_loss"
            if lo <= tp: return tp,   "take_profit"
    return candles[min(i+10, len(candles)-1)]['close'], "time_exit"

def backtest(window=20, mult=1):
    candles = get_historical_candles(days=7)
    if len(candles) < window:
        print("❌ Not enough data.")
        return
    closes = [c["close"] for c in candles]
    balance = 1000
    trades  = []

    for i in range(window, len(closes)):
        hist = closes[i-window:i]
        avg  = statistics.mean(hist)
        std  = statistics.stdev(hist)
        th   = std * mult
        price= closes[i]
        ma50 = get_moving_average(closes[:i+1], 50)
        atr  = compute_atr(candles[:i+1], 14)
        if ma50 is None or atr is None: continue
        spread = candles[i]['high'] - candles[i]['low']
        if spread > MAX_SPREAD: continue

        # basic Bollinger‐style breakouts + RSI
        rsi = compute_rsi(hist[-15:])
        trade = None
        # BUY
        if price < avg - th and price > ma50 and rsi < 40:
            strength = 1  # simplified
            entry     = price
            sl        = entry - 1.2 * atr
            tp        = entry + 2   * atr
            size      = max(1, RISK_PER_TRADE / (entry - sl))
            exit_p, reason = simulate_exit(i, candles, entry, tp, sl, "BUY", atr)
            profit = (exit_p - entry) * size - TRADE_FEE
            balance+= profit
            trades.append((candles[i]["time"], "BUY", entry, exit_p, profit, size, rsi, reason))

        # SELL
        if price > avg + th and price < ma50 and rsi > 60:
            strength = 1
            entry     = price
            sl        = entry + 1.2 * atr
            tp        = entry - 2   * atr
            size      = max(1, RISK_PER_TRADE / (sl - entry))
            exit_p, reason = simulate_exit(i, candles, entry, tp, sl, "SELL", atr)
            profit = (entry - exit_p) * size - TRADE_FEE
            balance+= profit
            trades.append((candles[i]["time"], "SELL", entry, exit_p, profit, size, rsi, reason))

    # report
    print(f"Final Balance: £{balance:.2f} | Trades: {len(trades)} | Profit: £{balance-1000:.2f}")
    wins = sum(1 for t in trades if t[4]>0)
    print(f"Win Rate: {100*wins/len(trades):.1f}%")
    for t in trades:
        time,type_,e,x,p,sz,rsi,rsn = t
        print(f"{time} | {type_} {e:.5f}->{x:.5f} | P/L £{p:.2f} | RSI {rsi:.1f} | Exit {rsn}")

if __name__=="__main__":
    backtest()
