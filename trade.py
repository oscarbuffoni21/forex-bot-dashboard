class Trade:
    def __init__(self, time, trade_type, entry, exit, profit, size, rsi, ma, atr, signal_strength, exit_reason):
        self.time = time
        self.trade_type = trade_type
        self.entry = entry
        self.exit = exit
        self.profit = profit
        self.size = size
        self.rsi = rsi
        self.ma = ma
        self.atr = atr
        self.signal_strength = signal_strength
        self.exit_reason = exit_reason

    def to_dict(self):
        return {
            "time": self.time,
            "type": self.trade_type,
            "entry": self.entry,
            "exit": self.exit,
            "profit": self.profit,
            "size": self.size,
            "rsi": self.rsi,
            "ma": self.ma,
            "atr": self.atr,
            "strength": self.signal_strength,
            "exit_reason": self.exit_reason,
        }