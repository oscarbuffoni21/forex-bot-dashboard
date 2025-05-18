from backtester import Backtester
from visualizer import plot_equity_curve, export_trades_to_csv

def main():
    backtester = Backtester(
        pair="EUR_USD",
        granularity="M5",
        days=7,
        initial_balance=1000,
        risk_per_trade=100,
        trade_fee=5,
        max_spread=0.00038
    )

    trades = backtester.run()

    print(f"\n📊 Final Balance: £{backtester.balance:.2f}")
    print(f"Total Trades: {len(trades)}")
    print(f"Profit: £{backtester.balance - backtester.initial_balance:.2f}")
    if trades:
        win_rate = 100 * sum(1 for t in trades if t.profit > 0) / len(trades)
        print(f"Win Rate: {win_rate:.1f}%")

        for t in trades:
            print(
                f"📍 Time: {t.time} | Type: {t.trade_type} | Entry: {t.entry:.5f} → Exit: {t.exit:.5f} "
                f"| Size: {t.size:.2f} | Profit: £{t.profit:.2f} | RSI: {t.rsi:.2f} | MA: {t.ma:.5f} | ATR: {t.atr:.5f} | Exit: {t.exit_reason}"
            )

    export_trades_to_csv(trades)
    plot_equity_curve(trades, initial_balance=backtester.initial_balance)

if __name__ == "__main__":
    main()