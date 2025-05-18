def simulate_exit(i, candles, entry_price, take_profit, initial_stop_loss, trade_type, atr, atr_multiplier=1.2):
    stop_loss = initial_stop_loss
    max_lookahead = 10  # how many candles to simulate into the future

    for j in range(1, max_lookahead + 1):
        if i + j >= len(candles):
            break

        candle = candles[i + j]
        high = candle['high']
        low = candle['low']

        if trade_type == "BUY":
            if high - entry_price >= 0.5 * atr:
                stop_loss = max(stop_loss, high - atr * atr_multiplier)
            if low <= stop_loss:
                return stop_loss, "stop_loss"
            if high >= take_profit:
                return take_profit, "take_profit"

        elif trade_type == "SELL":
            if entry_price - low >= 0.5 * atr:
                stop_loss = min(stop_loss, low + atr * atr_multiplier)
            if high >= stop_loss:
                return stop_loss, "stop_loss"
            if low <= take_profit:
                return take_profit, "take_profit"

    # If no TP/SL hit, exit at final candle
    exit_candle = candles[min(i + max_lookahead, len(candles) - 1)]
    return exit_candle['close'], "time_exit"