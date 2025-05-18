from trade import Trade
from simulator import simulate_exit

def should_enter_trade(index, candles, closes, price, ma50, atr, spread, direction, risk_per_trade, trade_fee, threshold, max_spread):
    # A simple breakout logic example
    if spread > max_spread:
        return None

    # Breakout condition
    breakout_level = max(c["high"] for c in candles[max(0, index-10):index])
    if direction == "buy" and price > breakout_level:
        entry_price = price
        stop_loss = entry_price - atr
        take_profit = entry_price + 2 * atr
    elif direction == "sell" and price < breakout_level:
        entry_price = price
        stop_loss = entry_price + atr
        take_profit = entry_price - 2 * atr
    else:
        return None

    stop_loss_distance = abs(entry_price - stop_loss)
    if stop_loss_distance == 0:
        return None

    size = risk_per_trade / stop_loss_distance
    size = max(1, size)

    exit_price, exit_reason = simulate_exit(index, candles, entry_price, take_profit, stop_loss, direction.upper(), atr)

    profit = (exit_price - entry_price) * size if direction == "buy" else (entry_price - exit_price) * size
    profit -= trade_fee

    return Trade(
        time=candles[index]["time"],
        trade_type=direction.upper(),
        entry=entry_price,
        exit=exit_price,
        profit=profit,
        size=size,
        rsi=None,
        ma=None,
        atr=atr,
        signal_strength=1.0,
        exit_reason=exit_reason
    )