from indicators import compute_rsi, get_moving_average, compute_atr, evaluate_signal_strength
from simulator import simulate_exit
from trade import Trade

def should_enter_trade(index, candles, closes, price, ma50, atr, spread, direction, risk_per_trade, trade_fee, threshold, max_spread):
    # Filter by spread and required indicators
    if spread > max_spread or ma50 is None or atr is None:
        return None

    # Compute RSI on last 14 closes
    recent_prices = closes[max(0, index-14):index+1]
    rsi = compute_rsi(recent_prices)

    # Calculate average and stddev of recent prices for threshold
    avg = sum(recent_prices) / len(recent_prices)
    stddev = 0 if len(recent_prices) < 2 else (sum((p - avg) ** 2 for p in recent_prices) / (len(recent_prices)-1)) ** 0.5

    # Use Bollinger band style threshold multiplier
    threshold = 2 * stddev

    # RSI filters for more selective entries
    if direction == "buy" and rsi > 30:  # only buy if RSI is oversold-ish
        return None
    if direction == "sell" and rsi < 70:  # only sell if RSI is overbought-ish
        return None

    # Evaluate signal strength and require stronger signals
    strength = evaluate_signal_strength(price, avg, threshold, direction)
    if strength < 0.7:
        return None

    entry_price = price
    atr_multiplier = 1.2

    # Set stop loss and take profit based on ATR
    if direction == "buy":
        stop_loss = entry_price - atr * atr_multiplier
        take_profit = entry_price + 2 * atr
    else:
        stop_loss = entry_price + atr * atr_multiplier
        take_profit = entry_price - 2 * atr

    stop_loss_distance = abs(entry_price - stop_loss)
    if stop_loss_distance == 0:
        return None

    # Calculate position size based on risk per trade and stop loss distance
    size = risk_per_trade / stop_loss_distance

    # Optional: cap max position size if desired, e.g.:
    # max_size = 100000  # example max units
    # size = min(size, max_size)

    # Minimum size constraint
    size = max(1, size)

    # Simulate trade exit
    exit_price, exit_reason = simulate_exit(index, candles, entry_price, take_profit, stop_loss, direction.upper(), atr)

    # Calculate profit factoring in trade fee
    profit = (exit_price - entry_price) * size if direction == "buy" else (entry_price - exit_price) * size
    profit -= trade_fee

    return Trade(
        time=candles[index]["time"],
        trade_type=direction.upper(),
        entry=entry_price,
        exit=exit_price,
        profit=profit,
        size=size,
        rsi=rsi,
        ma=ma50,
        atr=atr,
        signal_strength=strength,
        exit_reason=exit_reason
    )