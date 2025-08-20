import asyncio
import hmac
import hashlib
import time
import json
import pandas as pd
import httpx

API_KEY = "sJcEWzqfnybNACcxj5aHQV"
API_SECRET = "cxakp_c9Jzz49r7masxHKRJryNj7"

BASE_URL = "https://api.crypto.com/v2"

# Stochastic parameters
K_PERIOD = 14
D_PERIOD = 3

# Quantity and pair
PAIR = "CRO_USDT"
QUANTITY = 10

async def get_candles(pair, interval="1h", limit=50):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_URL}/public/get-candlestick",
            params={"instrument_name": pair, "timeframe": interval, "count": limit},
        )
        r.raise_for_status()
        data = r.json()
        #print(data)
        candles = data["result"]["data"]
        # Oldest first
        candles.reverse()
        df = pd.DataFrame(candles)
        df.columns = ["o", "h", "l", "c", "v", "timestamp"]
        df = df.astype(float)
        return df

'''def compute_stochastic(df):
    low_min = df["l"].rolling(window=K_PERIOD).min()
    high_max = df["h"].rolling(window=K_PERIOD).max()
    df["%K"] = 100 * (df["c"] - low_min) / (high_max - low_min)
    df["%D"] = df["%K"].rolling(window=D_PERIOD).mean()
    return df.dropna()
    '''

def compute_stochastic(df, k_period=14, d_period=3):
    """
    df: DataFrame with columns ['o', 'h', 'l', 'c']
    Returns DataFrame with '%K' and '%D' columns.
    """
    # Ensure candles are sorted oldest first
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Rolling min/max over previous k_period candles, excluding the current
    lowest_low = df["l"].shift(1).rolling(window=k_period).min()
    highest_high = df["h"].shift(1).rolling(window=k_period).max()

    # %K
    df["%K"] = 100 * (df["c"] - lowest_low) / (highest_high - lowest_low)

    # %D = moving average of %K
    df["%D"] = df["%K"].rolling(window=d_period).mean()
    return df


def create_auth_headers(api_key, api_secret, params):
    t = int(time.time() * 1000)
    param_str = ""
    if params:
        param_str = json.dumps(params, separators=(",", ":"), sort_keys=True)
    sig_payload = f"{t}{api_key}{param_str}"
    signature = hmac.new(
        bytes(api_secret, "utf-8"),
        msg=bytes(sig_payload, "utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return {
        "Content-Type": "application/json",
    }, {
        "id": t,
        "method": "",
        "api_key": api_key,
        "sig": signature,
        "nonce": t,
        "params": params or {}
    }

async def place_test_order(pair, price, quantity):
    async with httpx.AsyncClient() as client:
        params = {
            "instrument_name": pair,
            "side": "BUY",
            "type": "LIMIT",
            "price": str(price),
            "quantity": str(quantity),
            "time_in_force": "GOOD_TILL_CANCEL"
        }
        headers, payload = create_auth_headers(API_KEY, API_SECRET, params)
        payload["method"] = "private/create-order"

        r = await client.post(BASE_URL, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()

async def run_bot(_pair_):
    #print(f"Analysis for {_pair_}")
    df = await get_candles(PAIR)

    df = compute_stochastic(df)
    #print("Stochastic", df)
    #print("df.iloc", df.iloc[-1])

    current = df.iloc[-1]
    previous = df.iloc[-2]
    two_back = df.iloc[-3]
    three_back = df.iloc[-4]

    #print(f"Current %K: {current['%K']:.2f}")
    #print(f"Two candles back %K: {previous['%K']:.2f}")
    #print(f"Two candles back %K: {two_back['%K']:.2f}")
    #print(f"Three candles back %K: {three_back['%K']:.2f}")

    if two_back["%K"] < 50 and current["%K"] > 70:
        print(f"✅ Condition met: Placing test order...{_pair_}")
        #response = await place_test_order(PAIR, current["c"], QUANTITY)
        #print("Order Response:", response)
    elif previous["%K"] < 50 and current["%K"] > 70:
        print(f"✅ Condition met: Placing test order...{_pair_}")
        #response = await place_test_order(PAIR, current["c"], QUANTITY)
        #print("Order Response:", response)
    elif three_back["%K"] < 50 and current["%K"] > 70:
        print(f"✅ Condition met: Placing test order...{_pair_}")
        #response = await place_test_order(PAIR, current["c"], QUANTITY)
        #print("Order Response:", response)
    else:
        #print("❌ Condition not met. No order placed.")
        pass

if __name__ == "__main__":
    for pr in ['XRP-USD', 'ADAUSD-PERP', 'ADA_USD', 'ALGO_USD', 'AVAXUSD-PERP', 'AVAX_USD', 'BCH_USD', 'BTCUSD-PERP', 'BTC_USD', 'CROUSD-PERP', 'CRO_USD', 'DOGEUSD-PERP', 'DOGE_USD', 'DOT_USD', 'ENAUSD-PERP', 'ENA_USD', 'ETHUSD-PERP', 'ETH_USD', 'GALA_USD', 'HBAR_USD', 'LINKUSD-PERP', 'LINK_USD', 'LTCUSD-PERP', 'LTC_USD', 'NEARUSD-PERP', 'PEPE_USD', 'PUMPUSD-PERP', 'SHIB_USD', 'SOLUSD-PERP', 'SOL_USD', 'SUIUSD-PERP', 'SUI_USD', 'THETAUSD-PERP', 'TRUMP_USD', 'UNI_USD', 'USDT_USD', 'WIF_USD', 'XLM_USD', 'XRPUSD-PERP', 'XRP_USD']:
        asyncio.run(run_bot(pr))
