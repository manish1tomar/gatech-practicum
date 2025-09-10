#!/usr/bin/env python3
import ccxt
import time
import math

# === CONFIGURATION ===
symbol = "XRP/USDT"
timeframe = "15m"
max_trades = 10
max_loss = 15.0
trade_size = 260  # 1 unit of XRP
exchange = ccxt.cryptocom()  # Example, update with your exchange

# === API KEYS ===
exchange.apiKey = "eRUhcDv9E7UGD7L1mwxSw2"
exchange.secret = "cxakp_cm7Hfn2p5vUSEhZmdVMcj5"

# === TRACKING ===
trade_count = 0
total_loss = 0.0
active_trades = []

import pandas as pd
import ta  # pip install ta

import pandas as pd

def supertrend(df, atr_period=10, multiplier=3):
    # True Range (TR)
    df['H-L'] = df['high'] - df['low']
    df['H-C'] = abs(df['high'] - df['close'].shift())
    df['L-C'] = abs(df['low'] - df['close'].shift())
    df['TR'] = df[['H-L','H-C','L-C']].max(axis=1)

    # ATR
    df['ATR'] = df['TR'].rolling(atr_period).mean()

    # Upper & Lower Bands
    hl2 = (df['high'] + df['low']) / 2
    df['UpperBand'] = hl2 + (multiplier * df['ATR'])
    df['LowerBand'] = hl2 - (multiplier * df['ATR'])

    # Supertrend
    df['Supertrend'] = True  # default bullish
    df['SupertrendValue'] = 0.0

    for i in range(atr_period, len(df)):
        if df['close'].iloc[i] > df['UpperBand'].iloc[i-1]:
            df.at[df.index[i], 'Supertrend'] = True
        elif df['close'].iloc[i] < df['LowerBand'].iloc[i-1]:
            df.at[df.index[i], 'Supertrend'] = False
        else:
            df.at[df.index[i], 'Supertrend'] = df['Supertrend'].iloc[i-1]

        # Supertrend value = corresponding band
        if df['Supertrend'].iloc[i]:
            df.at[df.index[i], 'SupertrendValue'] = df['LowerBand'].iloc[i]
        else:
            df.at[df.index[i], 'SupertrendValue'] = df['UpperBand'].iloc[i]

    # Map to "green"/"red"
    df['Supertrend'] = df['Supertrend'].map({True: "green", False: "red"})
    return df

def fetch_data():
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
    df = pd.DataFrame(ohlcv, columns=['time','open','high','low','close','volume'])
    df = supertrend(df, atr_period=10, multiplier=3)
    return df

while trade_count < max_trades and total_loss < max_loss:
    try:
        df = fetch_data()

        if len(df) < 3:
            continue

        # Last 3 candles
        prev2 = df['Supertrend'].iloc[-3]  # N-2
        prev1 = df['Supertrend'].iloc[-2]  # N-1
        curr  = df['Supertrend'].iloc[-1]  # N

        price = df['close'].iloc[-1]
        st_value = df['SupertrendValue'].iloc[-1]

        # BUY CONDITION: flipped red → green and sustained for 2 candles
        if prev2 == "red" and prev1 == "green" and curr == "green":
            stop_loss = math.floor(st_value * 100) / 100.0  # round down to 2 decimals

            # Place buy order
            order = exchange.create_market_buy_order(symbol, trade_size)
            trade_count += 1

            active_trades.append({
                "entry_price": price,
                "stop_loss": stop_loss,
                "amount": trade_size
            })

            print(f"[TRADE {trade_count}] BUY at {price}, SL={stop_loss}")

        else:
            print("condition not met")

        # === CHECK ACTIVE TRADES ===
        new_active = []
        for trade in active_trades:
            if price <= trade["stop_loss"]:
                # Stop loss hit
                loss = (trade["entry_price"] - trade["stop_loss"]) * trade["amount"]
                total_loss += loss
                print(f"STOP LOSS HIT at {price}, Loss={loss:.2f}, Total Loss={total_loss:.2f}")
            else:
                new_active.append(trade)
        active_trades = new_active

        # Safety exit
        if total_loss >= max_loss:
            print("Max loss reached. Stopping trading.")
            break

        time.sleep(60)  # wait before next check (adjust if needed)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
