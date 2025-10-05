import yfinance as yf
import datetime
import pandas as pd
import os
import psutil
import subprocess
import sys

output_file = "credit_spreads.xlsx"

# --- Kill Excel if file is open ---
def close_excel_if_open(filename):
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if proc.info["name"] and "EXCEL" in proc.info["name"].upper():
                open_files = proc.open_files()
                for f in open_files:
                    if filename in f.path:
                        print(f"⚠️ Closing Excel (PID {proc.info['pid']}) because {filename} is open...")
                        proc.terminate()
                        proc.wait(timeout=5)
                        return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    return False

# --- Portfolio ---
portfolio = {
        "BMNR": 100, "PLTR": 100, "ANET": 100, "ALAB": 100, "AMAT": 100, "SBET": 100, "NGD": 100, "OPEN": 100,
        "HOOD": 100, "LAC":100, "NVT":100,
        "JOBY": 100, "SOFI": 100, "QS": 100, "VRT": 100, "E": 100, "AMD": 100, "NVDA": 100, "AVGO": 100,
        "COIN": 100, "GRAB": 100, "CRWV": 100, "INTC": 100, "NIO": 100, "HD": 100, "ETHA": 100, "VVPR": 100,
        "HIMS": 100, "ENPH": 100, "PANW": 100, "MSFT": 100, "MSTR": 100, "IBIT": 100, "GOOGL": 100, "AMZN": 100,
        "RUN": 100, "LLY": 100, "UNH": 100, "KWEB": 100, "SLV": 100, "NIO": 100, "OSCR": 100, "CRCL": 100, "BBAI": 100,
        "AFRM": 100,
        "SPY": 100, "NBIS": 100, "RICK": 100, "RKLB": 100, 'VKTX': 100, "APP": 100, "APLD": 100, "CELH": 100,
        "DUOL": 100, "V": 100, "AAPL": 100, "JPM": 100, "C": 100, "VZ": 100, "RKLB": 100,
        "ASTS": 100, "EOG": 100, "BROS": 100, "ABCL": 100, "MRVL": 100, "AXON": 100, "ELF": 100, "ORCL": 100,
        "CSCO": 100, "LLY": 100,
        "NVO": 100, "TTWO": 100, "META": 100, "CRWD": 100, "NFLX": 100, "CRM": 100, "PYPL": 100, "MU": 100, "NU": 100,
        "NOW": 100, "MELI": 100,
        "SHOP": 100, "TTD": 100, "TSM": 100, "LULU": 100, "RDDT": 100, "TSLA": 100, "SOUN": 100, "TGT": 100,
        "RGTI": 100, "ZM": 100, "TLRY": 100,
        "SG": 100, "ACHR": 100, "SHOP": 100, "DELL": 100, "MDB": 100, "OKTA": 100, "GS": 100, "VST": 100, "SQQQ": 100,
        "SSYS": 100, "QUBT": 100,
        "IONQ": 100, "APTV": 100, "AI": 100, "FIG": 100, "AEO": 100, "DOCU": 100, "ACGL": 100, "B": 100, "RGLD": 100,
        "ARHS": 100, "CROX": 100, "BLDR": 100, "GPN": 100,
        "ODP": 100, "TLN": 100, "CEG": 100, "VST": 100, "ADBE": 100, "STZ": 100, "FIVE": 100, "FMX": 100, "IREN": 100,
        "SOXL": 100,
        "ROBN": 100, "NVDL": 100, "ERO": 100, "SAND": 100, "LCID": 100, "DLO": 100, "TSLL": 100, 'NVO': 100, "OKLO": 100
        , 'ARHS': 100, "PLUG": 100, "INTC": 100, "FN": 100, "U": 100, "SNDK": 100, "MANH": 100, "LITE": 100,
        "CRDO": 100, "FLEX": 100, "GWRE": 100
        , 'FNF': 100, "CIEN": 100, "TPR": 100
        , 'NBXG': 100
        , 'NAC': 100
        , 'BMEZ': 100
        , 'MEGI': 100
        , 'CROX': 100
        , 'BLDR': 100
        , 'FCFS': 100
        , 'AR': 100
        , 'APD': 100
        , 'LB': 100
        , 'UGI': 100
        , 'FIX': 100
        , 'HSY': 100
        , 'MSFT': 100
        , 'MCD': 100
        , 'AXP': 100
        , 'EA': 100
        , 'AZO': 100
        , 'ASML': 100
        , 'COKE': 100
        , 'GOOGL': 100
        , 'GIB': 100
        , 'GPN': 100
        , 'CBOE': 100
        , 'LNSTY': 100
        , 'ICE': 100
        , 'CME': 100
        , 'ZM': 100
        , 'ADBE': 100
        , 'QLYS': 100
        , 'SEMR': 100
        , 'WRB': 100
        , 'AFG': 100
        , 'TRV': 100
        , 'RNR': 100
        , 'BRK-B': 100
        , 'MKL': 100
        , 'ACGL': 100
        , 'ACGL': 100
        , 'V': 100
        , 'B': 100
        , 'CTRA': 100
        , 'FRU.TO': 100
        , 'VNOM': 100
    }

def get_credit_spread(ticker, shares):
    stock = yf.Ticker(ticker)
    price = stock.history(period="1d")["Close"].iloc[-1]

    expirations = stock.options
    if not expirations:
        return None

    today = datetime.date.today()

    # --- Find 12M expiry ---
    twelve_months = today + datetime.timedelta(days=365)
    exp_12m = None
    for d in expirations:
        if d >= twelve_months.strftime("%Y-%m-%d"):
            exp_12m = d
            break
    if not exp_12m:
        exp_12m = expirations[-1]

    # --- Find 3M expiry ---
    three_months = today + datetime.timedelta(days=90)
    exp_3m = None
    for d in expirations:
        if d >= three_months.strftime("%Y-%m-%d"):
            exp_3m = d
            break
    if not exp_3m:
        exp_3m = expirations[-1]

    # --- Get option chains ---
    long_calls = stock.option_chain(exp_12m).calls
    short_calls = stock.option_chain(exp_3m).calls

    if long_calls.empty or short_calls.empty:
        return None

    # crude proxy for ~0.7 delta: closest ITM strike
    long_calls["moneyness"] = long_calls["strike"] / price
    long_calls["diff70"] = abs(long_calls["moneyness"] - 1.0)
    long_opt = long_calls.loc[long_calls["diff70"].idxmin()]

    long_strike = long_opt["strike"]
    long_premium = long_opt["ask"]

    # short strike = nearest strike ABOVE (long_strike + long_premium)
    target_strike = long_strike + long_premium
    short_calls_above = short_calls[short_calls["strike"] >= target_strike]

    if short_calls_above.empty:
        short_opt = short_calls.iloc[-1]  # fallback: highest strike available
    else:
        short_opt = short_calls_above.iloc[0]

    short_strike = short_opt["strike"]
    short_premium = short_opt["bid"]

    net_credit = short_premium - long_premium
    return_pct = (short_premium / long_premium * 100) if long_premium > 0 else None

    return {
        "Ticker": ticker,
        "Stock Price": round(price, 2),
        "Long Expiry": exp_12m,
        "Long Strike (~0.7Δ)": long_strike,
        "Long Premium Paid": round(long_premium, 2),
        "Short Expiry": exp_3m,
        "Short Strike (≥ L+P)": short_strike,
        "Short Premium Received": round(short_premium, 2),
        "Net Credit (Credit>0)": round(net_credit, 2),
        "Return %": round(return_pct, 2) if return_pct else 0
    }

def build_dataframe(portfolio):
    results = []
    for ticker, shares in portfolio.items():
        print("Processing", ticker)
        res = get_credit_spread(ticker, shares)
        if res:
            results.append(res)

    df = pd.DataFrame(results)

    # sort descending by Return %
    df = df.sort_values(by="Return %", ascending=False)
    return df

# --- Build Data ---
df = build_dataframe(portfolio)

# --- Close Excel if open ---
close_excel_if_open(os.path.abspath(output_file))

# --- Save to Excel ---
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="CreditSpreads")

print(f"\n✅ Exported to {output_file} with {len(df)} tickers")

# --- Open Excel file ---
if sys.platform.startswith("win"):
    os.startfile(output_file)
elif sys.platform == "darwin":
    subprocess.call(["open", output_file])
else:
    subprocess.call(["xdg-open", output_file])
