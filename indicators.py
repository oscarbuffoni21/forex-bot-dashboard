import statistics

def compute_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50  # neutral RSI if not enough data
    gains, losses = [], []
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i - 1]
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    return 100 - (100 / (1 + rs))

def get_moving_average(prices, period=50):
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period

def compute_atr(candles, period=14):
    if len(candles) < period + 1:
        return None
    trs = []
    for i in range(1, len(candles)):
        high = candles[i]['high']
        low = candles[i]['low']
        prev_close = candles[i - 1]['close']
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)
    return sum(trs[-period:]) / period
def evaluate_signal_strength(price, avg, threshold, direction):
    deviation = abs(price - avg)
    score = 0

    if deviation > threshold * 1.5:
        score += 0.5
    elif deviation > threshold:
        score += 0.3
    elif deviation > threshold * 0.5:
        score += 0.2

    if direction == "buy" and price < avg:
        score += 0.3
    if direction == "sell" and price > avg:
        score += 0.3

    return min(score, 1.0)