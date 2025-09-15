#!/usr/bin/env python3
"""
SuperTrend-based trading bot for XRP/USD on Crypto.com

Enhancements:
- Enters trade as soon as SuperTrend turns green with 1 candle close confirmation.
- Re-enters when signal occurs again.
- Stops trading permanently when cumulative loss reaches $15.
"""

import os
import time
import winsound
import pandas as pd
import numpy as np
import ccxt

# --------------------- Config ---------------------
SYMBOL = "XRP/USD"
AMOUNT = 275              # quantity of XRP to buy each trade
TIMEFRAME = "15m"
CANDLE_LIMIT = 200
POLL_INTERVAL = 60
STOP_MONITOR_INTERVAL = 5

API_KEY = os.getenv("CRYPTOCOM_API_KEY", "")
API_SECRET = os.getenv("CRYPTOCOM_API_SECRET", "")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "false"

# Global P&L tracker
TOTAL_LOSS_LIMIT = 15.0
total_loss = 0.0


def alarm():
    winsound.Beep(1000, 1000)


# ---------------- Indicator: SuperTrend ----------------
def atr(df: pd.DataFrame, period: int = 14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0):
    """
    Returns DataFrame with SuperTrend direction (+1=green, -1=red) and value.
    """
    atr_val = atr(df, period)
    hl2 = (df['high'] + df['low']) / 2

    upperband = hl2 + (multiplier * atr_val)
    lowerband = hl2 - (multiplier * atr_val)

    final_upperband = upperband.copy()
    final_lowerband = lowerband.copy()

    for i in range(1, len(df)):
        if df['close'].iloc[i - 1] > final_upperband.iloc[i - 1]:
            final_upperband.iloc[i] = min(upperband.iloc[i], final_upperband.iloc[i - 1])
        else:
            final_upperband.iloc[i] = upperband.iloc[i]

        if df['close'].iloc[i - 1] < final_lowerband.iloc[i - 1]:
            final_lowerband.iloc[i] = max(lowerband.iloc[i], final_lowerband.iloc[i - 1])
        else:
            final_lowerband.iloc[i] = lowerband.iloc[i]

    st = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)

    for i in range(len(df)):
        if i == 0:
            st.iloc[i] = upperband.iloc[i]
            direction.iloc[i] = -1
        else:
            if df['close'].iloc[i] > final_upperband.iloc[i - 1]:
                direction.iloc[i] = 1
                st.iloc[i] = final_lowerband.iloc[i]
            elif df['close'].iloc[i] < final_lowerband.iloc[i - 1]:
                direction.iloc[i] = -1
                st.iloc[i] = final_upperband.iloc[i]
            else:
                direction.iloc[i] = direction.iloc[i - 1]
                if direction.iloc[i] == 1:
                    st.iloc[i] = final_lowerband.iloc[i]
                else:
                    st.iloc[i] = final_upperband.iloc[i]

    df['supertrend'] = st
    df['st_direction'] = direction
    return df


def supertrend_buy_signal(df: pd.DataFrame):
    """
    Returns True if SuperTrend just turned green (direction=1) and closed.
    """
    if len(df) < 2:
        return False
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return prev['st_direction'] == -1 and last['st_direction'] == 1


# ---------------- Exchange helpers ----------------
def make_exchange() -> ccxt.Exchange:
    return ccxt.cryptocom({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'},
    })


def fetch_ohlcv_df(ex: ccxt.Exchange, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
    ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df = supertrend(df)  # compute supertrend
    return df


def place_market_buy(ex: ccxt.Exchange, symbol: str, amount: float):
    print(f"Placing MARKET BUY {amount} {symbol} ... DRY_RUN={DRY_RUN}")
    if DRY_RUN:
        return {'id': 'DRY_RUN_BUY', 'price': 0.50}
    order = ex.create_market_buy_order(symbol, amount)
    price = float(order.get('average', 0) or ex.fetch_ticker(symbol)['last'])
    return {'id': order.get('id'), 'price': price}


def place_market_sell(ex: ccxt.Exchange, symbol: str, amount: float):
    print(f"Selling {amount} {symbol} ... DRY_RUN={DRY_RUN}")
    if DRY_RUN:
        return {'id': 'DRY_RUN_SELL', 'price': 0.49}
    order = ex.create_market_sell_order(symbol, amount)
    price = float(order.get('average', 0) or ex.fetch_ticker(symbol)['last'])
    return {'id': order.get('id'), 'price': price}


# ---------------- Trading logic ----------------
def dynamic_stop_monitor(ex: ccxt.Exchange, symbol: str, amount: float, entry_price: float):
    """Monitor price against SuperTrend as dynamic stop."""
    global total_loss

    print(f"Monitoring trade... Entry={entry_price}")
    while True:
        try:
            df = fetch_ohlcv_df(ex, symbol, TIMEFRAME, CANDLE_LIMIT)
            last = df.iloc[-1]
            stop_price = last['supertrend']

            ticker = ex.fetch_ticker(symbol)
            last_price = float(ticker['last']) if ticker.get('last') else None
            if last_price is None:
                time.sleep(STOP_MONITOR_INTERVAL)
                continue

            print(f"[Stop Monitor] Last={last_price}, Stop={stop_price}")
            if last_price <= stop_price:
                sell_order = place_market_sell(ex, symbol, amount)
                exit_price = sell_order['price']
                pnl = (exit_price - entry_price) * amount
                print(f"Trade closed. PnL={pnl:.2f}")
                if pnl < 0:
                    total_loss += abs(pnl)
                return pnl
            time.sleep(STOP_MONITOR_INTERVAL)
        except Exception as e:
            print("Monitor error:", e)
            time.sleep(STOP_MONITOR_INTERVAL)


# ---------------- Main loop ----------------
def main():
    global total_loss
    ex = make_exchange()
    ex.load_markets()

    while total_loss < TOTAL_LOSS_LIMIT:
        try:
            df = fetch_ohlcv_df(ex, SYMBOL, TIMEFRAME, CANDLE_LIMIT)

            if supertrend_buy_signal(df):
                print("SuperTrend turned GREEN! Buying...")
                order = place_market_buy(ex, SYMBOL, AMOUNT)
                entry_price = order['price']
                alarm()
                pnl = dynamic_stop_monitor(ex, SYMBOL, AMOUNT, entry_price)
                print(f"Cumulative loss so far: {total_loss:.2f}")
            else:
                print(f"No signal yet. Sleeping {POLL_INTERVAL}s")
                time.sleep(POLL_INTERVAL)

        except Exception as e:
            print("Error during loop:", e)
            time.sleep(POLL_INTERVAL)

    print(f"Stopping trading. Cumulative loss reached {total_loss:.2f}")


if __name__ == "__main__":
    main()
