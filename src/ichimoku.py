#!/usr/bin/env python3
"""
Ichimoku-based trading bot for XRP/USD on Crypto.com

Enhancements:
- Keeps trading repeatedly whenever entry conditions reoccur.
- Stops trading permanently when cumulative loss reaches $15.

Requirements:
  pip install ccxt pandas numpy python-dotenv
"""

import os
import time
import math
from dataclasses import dataclass
from typing import Tuple
import winsound

import numpy as np
import pandas as pd
import ccxt

# --------------------- Config ---------------------
SYMBOL = "XRP/USD"
AMOUNT = 275              # quantity of XRP to buy each trade
TIMEFRAME = "2h"
CANDLE_LIMIT = 300
POLL_INTERVAL = 60
STOP_MONITOR_INTERVAL = 5

API_KEY = os.getenv("CRYPTOCOM_API_KEY", "")
API_SECRET = os.getenv("CRYPTOCOM_API_SECRET", "")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "false"   # false = dry-run

# Global P&L tracker
TOTAL_LOSS_LIMIT = 15.0
total_loss = 0.0


def alarm():
    winsound.Beep(1000, 1000)


# ---------------- Ichimoku helpers ----------------
@dataclass
class IchimokuValues:
    tenkan: float
    kijun: float
    senkou_a_now: float
    senkou_b_now: float
    chikou_vs_cloud_ok: bool


def ichimoku(df: pd.DataFrame) -> IchimokuValues:
    highs = df['high']
    lows = df['low']
    closes = df['close']

    tenkan = (highs.rolling(9).max() + lows.rolling(9).min()) / 2
    kijun = (highs.rolling(26).max() + lows.rolling(26).min()) / 2
    span_b = (highs.rolling(52).max() + lows.rolling(52).min()) / 2
    span_a = (tenkan + kijun) / 2

    shift = 26
    if len(df) <= 78 + shift:
        raise ValueError("Not enough candles for Ichimoku (need > 104).")

    tenkan_now = float(tenkan.iloc[-1])
    kijun_now = float(kijun.iloc[-1])
    span_a_now = float(span_a.iloc[-1])
    span_b_now = float(span_b.iloc[-1])

    chikou_idx = -shift
    close_26_back = float(closes.iloc[chikou_idx])
    span_a_26_back = float(span_a.iloc[chikou_idx])
    span_b_26_back = float(span_b.iloc[chikou_idx])
    chikou_ok = close_26_back > max(span_a_26_back, span_b_26_back)

    return IchimokuValues(
        tenkan=tenkan_now,
        kijun=kijun_now,
        senkou_a_now=span_a_now,
        senkou_b_now=span_b_now,
        chikou_vs_cloud_ok=chikou_ok,
    )


def ichimoku_buy_conditions(df: pd.DataFrame) -> Tuple[bool, IchimokuValues, float]:
    values = ichimoku(df)
    last_close = float(df['close'].iloc[-1])

    price_above_cloud = last_close > max(values.senkou_a_now, values.senkou_b_now)
    tenkan_above_kijun = values.tenkan > values.kijun
    recent_cloud_green = values.senkou_a_now > values.senkou_b_now
    chikou_above_cloud = values.chikou_vs_cloud_ok
    price_above_tenkan = (math.floor(last_close * 100.0) / 100.0) > values.tenkan

    all_ok = price_above_cloud and tenkan_above_kijun and recent_cloud_green \
             and chikou_above_cloud and price_above_tenkan

    stop_loss = math.floor(values.tenkan * 100.0) / 100.0

    return all_ok, values, stop_loss


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
    return pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])


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
    """Monitor price and trigger stop-loss. Returns PnL (profit or loss)."""
    global total_loss

    print(f"Monitoring stop-loss for {symbol} ... Entry={entry_price}")
    while True:
        try:
            df = fetch_ohlcv_df(ex, symbol, TIMEFRAME, CANDLE_LIMIT)
            _, _, stop_price = ichimoku_buy_conditions(df)

            ticker = ex.fetch_ticker(symbol)
            last = float(ticker['last']) if ticker.get('last') else None
            if last is None:
                time.sleep(STOP_MONITOR_INTERVAL)
                continue

            print(f"[Stop Monitor] Last={last}, Stop={stop_price}")
            if last <= stop_price:
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
            ok, values, stop_price = ichimoku_buy_conditions(df)
            last_close = float(df['close'].iloc[-1])

            print("\nChecking conditions...")
            print(f"Latest close={last_close}, Tenkan={values.tenkan}, Kijun={values.kijun}, Stop={stop_price}")

            if ok:
                print("Conditions satisfied. Buying...")
                order = place_market_buy(ex, SYMBOL, AMOUNT)
                entry_price = order['price']
                alarm()
                pnl = dynamic_stop_monitor(ex, SYMBOL, AMOUNT, entry_price)
                print(f"Total cumulative loss so far: {total_loss:.2f}")

            else:
                print(f"Conditions NOT met. Sleeping {POLL_INTERVAL}s")
                time.sleep(POLL_INTERVAL)

        except Exception as e:
            print("Error during loop:", e)
            time.sleep(POLL_INTERVAL)

    print(f"Stopping trading. Cumulative loss reached {total_loss:.2f}")


if __name__ == "__main__":
    main()
