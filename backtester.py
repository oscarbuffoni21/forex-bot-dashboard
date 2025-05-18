import statistics
from oanda import get_historical_candles
from strategy import should_enter_trade

class Backtester:
    def __init__(
        self,
        pair: str,
        granularity: str,
        days: int,
        initial_balance: float,
        risk_per_trade: float,
        trade_fee: float,
        max_spread: float,
        strategy_type: str | None = None
    ):
        self.pair = pair
        self.granularity = granularity
        self.days = days
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.trade_fee = trade_fee
        self.max_spread = max_spread
        self.strategy_type = strategy_type

    def run(self) -> list:
        """
        Fetches historical candles, runs through them, and applies the strategy's
        should_enter_trade logic to generate trades.
        Returns a list of Trade objects.
        """
        candles = get_historical_candles(self.pair, self.granularity, self.days)
        if not candles:
            print("❌ No candle data fetched.")
            return []

        trades = []
        closes = [c["close"] for c in candles]

        window_size = 20
        for i, price in enumerate(closes):
            # Ensure enough data for window
            if i < window_size - 1:
                continue

            # Compute SMA + threshold
            window_closes = closes[i - window_size + 1: i + 1]
            avg = statistics.mean(window_closes)
            stddev = statistics.stdev(window_closes)
            threshold = stddev

            # 50-period MA
            ma50 = None
            if i >= 49:
                ma50 = statistics.mean(closes[i - 49: i + 1])

            # ATR (single-period)
            atr = None
            if i >= 1:
                prev_close = candles[i - 1]["close"]
                high = candles[i]["high"]
                low = candles[i]["low"]
                tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
                atr = tr

            # Spread filter
            spread = candles[i]["high"] - candles[i]["low"]
            if spread > self.max_spread:
                continue

            # Entry direction
            direction = None
            if price < avg - threshold and ma50 is not None:
                direction = "buy"
            elif price > avg + threshold and ma50 is not None:
                direction = "sell"

            if not direction:
                continue

            # Delegate to strategy
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
                threshold=threshold,
                max_spread=self.max_spread
            )
            if trade:
                self.balance += trade.profit
                trades.append(trade)

        return trades
