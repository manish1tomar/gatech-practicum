#!/usr/bin/env python3
"""
Buy 1 XRP/USD on Crypto.com when Ichimoku conditions are met, then place a stop loss
at the Kijun-sen ("red line") rounded DOWN to one decimal place.

Now modified to:
- Check conditions every 60 seconds.
- Continuously update the stop price with the latest Ichimoku values.

Requirements:
  pip install ccxt pandas numpy python-dotenv

Environment variables (or replace inline):
  CRYPTOCOM_API_KEY
  CRYPTOCOM_API_SECRET
  DRY_RUN=true   # set to 'false' to actually place orders

Notes:
- Timeframe is 1h by default; you can change TIMEFRAME.
- This script uses CCXT's unified API for Crypto.com (exchange id: 'cryptocom').
- Stop-loss placement is enforced by a fallback monitor (no native API stop support).
- Example code for educational purposes; use at your own risk.
"""
from __future__ import annotations
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
SYMBOL = "XRP/USD"            # Crypto.com spot symbol via CCXT
AMOUNT = 260                  # Buy exactly 1 XRP
TIMEFRAME = "15m"              # Candle timeframe used for Ichimoku
CANDLE_LIMIT = 300            # Fetch enough candles for Ichimoku (>= 78)
POLL_INTERVAL = 60            # seconds, re-check Ichimoku conditions
STOP_MONITOR_INTERVAL = 5     # seconds, for fallback stop monitoring

API_KEY = os.getenv("CRYPTOCOM_API_KEY", "oER5Gcykjw7YRh542EkM5B")
API_SECRET = os.getenv("CRYPTOCOM_API_SECRET", "cxakp_E3TQJPUHhYtWMn7JwhmCq8")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "false"

def alarm():
    # Frequency = 1000 Hz, Duration = 1000 ms (1 second)
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
    print("chikou_ok", close_26_back, "cloud", max(span_a_26_back, span_b_26_back))
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

    if not price_above_cloud:
        print("Price below cloud")
    if not tenkan_above_kijun:
        print("Blue below Red")
    if not recent_cloud_green:
        print("Cloud is Red")
    if not chikou_above_cloud:
        print("Lagging Green is below/under cloud")

    all_ok = price_above_cloud and tenkan_above_kijun and recent_cloud_green and chikou_above_cloud

    stop_loss = math.floor(values.kijun * 100.0) / 100.0

    return all_ok, values, stop_loss

# ---------------- Exchange helpers ----------------

def make_exchange() -> ccxt.Exchange:
    ex = ccxt.cryptocom({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'},
    })
    return ex


def fetch_ohlcv_df(ex: ccxt.Exchange, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
    ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df


def place_market_buy(ex: ccxt.Exchange, symbol: str, amount: float):
    print(f"Placing MARKET BUY {amount} {symbol} ... DRY_RUN={DRY_RUN}")
    if DRY_RUN:
        return {'id': 'DRY_RUN_BUY', 'info': {'note': 'dry run buy'}}
    order = ex.create_market_buy_order(symbol, amount)
    print("Buy order placed:", order.get('id'))
    return order


def dynamic_stop_monitor(ex: ccxt.Exchange, symbol: str, amount: float):
    if DRY_RUN:
        print("[DRY RUN] Skipping dynamic stop monitor loop.")
        return

    print(f"Starting dynamic stop monitor for {symbol} ...")
    while True:
        try:
            df = fetch_ohlcv_df(ex, symbol, TIMEFRAME, CANDLE_LIMIT)
            _, values, stop_price = ichimoku_buy_conditions(df)

            ticker = ex.fetch_ticker(symbol)
            last = float(ticker['last']) if ticker.get('last') is not None else None
            if last is None:
                time.sleep(STOP_MONITOR_INTERVAL)
                continue

            print(f"[Stop Monitor] Last: {last}, Updated stop: {stop_price}")
            if last <= stop_price:
                print(f"Price {last} <= stop {stop_price}. Selling {amount} {symbol} market...")
                ex.create_market_sell_order(symbol, amount)
                print("Stop executed via dynamic stop monitor.")
                break
            time.sleep(STOP_MONITOR_INTERVAL)
        except Exception as e:
            print("Monitor error:", e)
            time.sleep(STOP_MONITOR_INTERVAL)

# ---------------- Main flow ----------------

def main():
    ex = make_exchange()
    markets = ex.load_markets()
    if SYMBOL not in markets:
        raise RuntimeError(f"Symbol {SYMBOL} not found on Crypto.com. Example available: {list(markets.keys())[:5]}")

    while True:
        try:
            df = fetch_ohlcv_df(ex, SYMBOL, TIMEFRAME, CANDLE_LIMIT)
            ok, values, stop_price = ichimoku_buy_conditions(df)
            last_close = float(df['close'].iloc[-1])

            print("\nChecking conditions...")
            print("Latest close:", last_close)
            print("Tenkan (conv):", values.tenkan)
            print("Kijun  (base):", values.kijun)
            print("SenkouA now  :", values.senkou_a_now)
            print("SenkouB now  :", values.senkou_b_now)
            print("Chikou>cloud :", values.chikou_vs_cloud_ok)
            print("Stop-loss @  :", stop_price)

            if ok:
                print("All Ichimoku conditions satisfied. Proceeding to buy...")
                order = place_market_buy(ex, SYMBOL, AMOUNT)
                alarm()
                dynamic_stop_monitor(ex, SYMBOL, AMOUNT)
                break  # exit loop after trade completes
            else:
                print("Conditions NOT met. Will check again in", POLL_INTERVAL, "seconds.")
                time.sleep(POLL_INTERVAL)
        except Exception as e:
            print("Error during loop:", e)
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
