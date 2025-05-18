import matplotlib.pyplot as plt
import csv

def plot_equity_curve(trades, initial_balance=1000):
    balance = initial_balance
    balance_history = [balance]

    for trade in trades:
        balance += trade.profit
        balance_history.append(balance)

    plt.figure(figsize=(12, 6))
    plt.plot(balance_history, marker='o')
    plt.title("Equity Curve")
    plt.xlabel("Trade Number")
    plt.ylabel("Balance (£)")
    plt.grid(True)
    plt.show()

def export_trades_to_csv(trades, filename="backtest_trades.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Time", "Type", "Entry Price", "Exit Price", "Profit (£)",
            "Size", "Signal Strength", "RSI", "MA", "ATR", "Exit Reason"
        ])
        for t in trades:
            writer.writerow([
                t.time,
                t.trade_type,
                f"{t.entry:.5f}",
                f"{t.exit:.5f}",
                f"{t.profit:.2f}",
                f"{t.size:.2f}",
                f"{t.signal_strength:.2f}",
                f"{t.rsi:.2f}",
                f"{t.ma:.5f}",
                f"{t.atr:.5f}",
                t.exit_reason
            ])