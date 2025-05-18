import statistics
from oanda import get_historical_candles
from strategy import should_enter_trade

class Backtester:
    def __init__(self, pair, granularity, days, initial_balance, risk_per_trade, trade_fee, max_spread):
        self.pair = pair
        self.granularity = granularity
        self.days = days
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.trade_fee = trade_fee
        self.max_spread = max_spread

    def run(self):
        candles = get_historical_candles(self.pair, self.granularity, self.days)
        if not candles:
            print("❌ No candle data fetched.")
            return []

        trades = []
        closes = [c["close"] for c in candles]
        timestamps = [c["time"] for c in candles]

        price_history = []

        for i in range(len(closes)):
            price = closes[i]
            price_history.append(price)
            if len(price_history) > 20:
                price_history.pop(0)

            if len(price_history) < 20:
                continue

            avg = statistics.mean(price_history)
            stddev = statistics.stdev(price_history)
            threshold = stddev * 1  # Multiplier = 1

            c = candles[i]
            ma50 = statistics.mean(closes[max(0, i-49):i+1]) if i >= 49 else None
            atr = max(c["high"] - c["low"], abs(c["high"] - c["close"]), abs(c["low"] - c["close"]))
            spread = c["high"] - c["low"]
            if ma50 is None:
                continue

            direction = None
            if price < avg - threshold and price > ma50:
                direction = "buy"
            elif price > avg + threshold and price < ma50:
                direction = "sell"

            if direction:
                trade = should_enter_trade(
    index=i,
    candles=candles,
    closes=closes,
    price=price,
    ma50=ma50,
    atr=atr,
    spread=spread,
    direction=direction,
    risk_per_trade=self.risk_per_trade,
    trade_fee=self.trade_fee,
    max_spread=self.max_spread,
    threshold=threshold  # ✅ this line fixes the error
)
                if trade:
                    self.balance += trade.profit
                    trades.append(trade)

        return trades
