import yfinance as yf
import pandas as pd
import numpy as np

# -------------------------------
# Supertrend Calculation Function
# -------------------------------
def supertrend(df, period=7, multiplier=3):
    df['TR'] = np.maximum(df['High'] - df['Low'],
                np.maximum(abs(df['High'] - df['Close'].shift()),
                           abs(df['Low'] - df['Close'].shift())))
    df['ATR'] = df['TR'].rolling(period).mean()

    hl2 = (df['High'] + df['Low']) / 2
    df['UpperBand'] = hl2 + multiplier * df['ATR']
    df['LowerBand'] = hl2 - multiplier * df['ATR']

    supertrend = np.ones(len(df), dtype=bool)

    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['UpperBand'].iloc[i - 1]:
            supertrend[i] = True
        elif df['Close'].iloc[i] < df['LowerBand'].iloc[i - 1]:
            supertrend[i] = False
        else:
            supertrend[i] = supertrend[i - 1]
            if supertrend[i] and df['LowerBand'].iloc[i] < df['LowerBand'].iloc[i - 1]:
                df.loc[df.index[i], 'LowerBand'] = df['LowerBand'].iloc[i - 1]
            if not supertrend[i] and df['UpperBand'].iloc[i] > df['UpperBand'].iloc[i - 1]:
                df.loc[df.index[i], 'UpperBand'] = df['UpperBand'].iloc[i - 1]

    df['Supertrend'] = supertrend

    return df


# -------------------------------
# Get data from yfinance
# -------------------------------
def get_data(symbol, interval="1d", period="1y"):
    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.history(interval=interval, period=period)
    if df.empty:
        return pd.DataFrame()
    return df[['Open','High','Low','Close']]


# -------------------------------
# Scan all stocks for Supertrend
# -------------------------------
def scan_supertrend(timeframe="1d", target_market_cap_usd = 0, limit=50):
    # NSE stock list
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    symbols = pd.read_csv(url)['SYMBOL'].tolist()

    results = []
    for sym in symbols[:limit]:
        try:
            # Get the ticker object
            ticker = yf.Ticker(sym)

            # Get the company's info
            info = ticker.info

            # Retrieve the market cap
            try:
                market_cap = info.get('marketCap', None)
            except Exception as e:
                print(e)
            # Check if market cap data is available
            if market_cap is not None:
                # Check if the market cap is below the target
                if market_cap > target_market_cap_usd:
                    # adjust period depending on timeframe
                    if timeframe in ["1m","2m","5m","15m","30m","60m","90m","1h"]:
                        period = "60d"   # intraday data limited
                    elif timeframe in ["1d","5d"]:
                        period = "1y"
                    elif timeframe in ["1wk"]:
                        period = "5y"
                    elif timeframe in ["1mo","3mo"]:
                        period = "10y"
                    else:
                        period = "1y"

                    df = get_data(sym, interval=timeframe, period=period)
                    if df.empty or len(df) < 20:
                        continue

                    df = supertrend(df)
                    #print(df.head())
                    if df['Supertrend'].iloc[-5:].all():   # ✅ Latest candle is green
                        results.append(sym)

        except Exception as e:
            print(f"Error for {sym}: {e}")
            continue

    return results


if __name__ == "__main__":
    # Set the target market cap in INR
    target_market_cap_inr = 2000 * 10 ** 7

    # Example: Daily scan
    daily = scan_supertrend("1d", target_market_cap_inr, limit=100)
    print("✅ Stocks with Supertrend GREEN on Daily timeframe:", daily)

    # Example: Weekly scan
    weekly = scan_supertrend("1wk", target_market_cap_inr, limit=100)
    print("✅ Stocks with Supertrend GREEN on Weekly timeframe:", weekly)

    # Example: 15 min scan
    min15 = scan_supertrend("15m", target_market_cap_inr, limit=50)
    print("✅ Stocks with Supertrend GREEN on 15-min timeframe:", min15)
