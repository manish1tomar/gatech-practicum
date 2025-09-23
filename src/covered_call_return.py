import yfinance as yf
import datetime
import pandas as pd
import os
import psutil
import subprocess
import sys

output_file = "covered_call_yields.xlsx"

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
        "HOOD": 100,
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

def get_atm_call_yield(ticker, shares, target_expiry):
    stock = yf.Ticker(ticker)
    price = stock.history(period="1d")["Close"].iloc[-1]

    expirations = stock.options
    if target_expiry not in expirations:
        return None

    opt_chain = stock.option_chain(target_expiry)
    calls = opt_chain.calls
    calls["diff"] = abs(calls["strike"] - price)
    atm_call = calls.loc[calls["diff"].idxmin()]

    premium = atm_call["ask"]
    expiry_date = datetime.datetime.strptime(target_expiry, "%Y-%m-%d").date()
    days_to_expiry = (expiry_date - datetime.date.today()).days
    yield_pct = ((premium + atm_call["strike"] - price) / price) * 100
    annualized_yield = yield_pct * (365 / days_to_expiry) if days_to_expiry > 0 else 0

    return {
        "Ticker": ticker,
        "Stock Price": round(price, 2),
        "ATM Strike": atm_call["strike"],
        "Premium": round(premium, 2),
        "Expiry": target_expiry,
        "Days to Expiry": days_to_expiry,
        "Yield %": round(yield_pct, 2),
        "Annualized Yield %": round(annualized_yield, 2),
        "Stock Value": round(price * shares, 2),
        "Premium Income": round(premium * (shares // 100), 2),
    }

def build_dataframe(portfolio, expiry_date):
    results = []
    total_stock_value, total_premium = 0, 0

    for ticker, shares in portfolio.items():
        print(ticker, expiry_date)
        res = get_atm_call_yield(ticker, shares, expiry_date)
        if res:
            results.append(res)
            total_stock_value += res["Stock Value"]
            total_premium += res["Premium Income"]

    df = pd.DataFrame(results)

    if total_stock_value > 0:
        totals = {
            "Ticker": "TOTAL",
            "Stock Price": "",
            "ATM Strike": "",
            "Premium": "",
            "Expiry": "",
            "Days to Expiry": "",
            "Yield %": round((total_premium / total_stock_value) * 100, 2),
            "Annualized Yield %": "",
            "Stock Value": round(total_stock_value, 2),
            "Premium Income": round(total_premium, 2),
        }
        df = df.sort_values(by="Yield %", ascending=False)
        df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)

    return df

# --- Find next 3 Fridays ---
today = datetime.date.today()
fridays = []
for i in range(3):
    days_ahead = (4 - today.weekday()) % 7
    friday = today + datetime.timedelta(days=days_ahead + 7 * i)
    fridays.append(friday.strftime("%Y-%m-%d"))

# --- Find 2-month expiry ---
two_months = today + datetime.timedelta(days=60)
two_months_str = two_months.strftime("%Y-%m-%d")

# --- Find 3-month expiry ---
three_months = today + datetime.timedelta(days=90)
three_months_str = three_months.strftime("%Y-%m-%d")

# pick a representative ticker to fetch expirations
sample_ticker = yf.Ticker("AAPL")
expiries = sample_ticker.options

if two_months_str in expiries:
    final_2m_expiry = two_months_str
else:
    # fallback: pick last expiry in the same YYYY-MM month
    same_month_expiries = [d for d in expiries if d.startswith(two_months.strftime("%Y-%m"))]
    if same_month_expiries:
        final_2m_expiry = same_month_expiries[-1]
    else:
        # fallback: just pick the nearest available after 90 days
        later = [d for d in expiries if d > two_months_str]
        final_2m_expiry = later[0] if later else expiries[-1]

print("📅 Target Expirations:", fridays + [final_2m_expiry])

if three_months_str in expiries:
    final_3m_expiry = three_months_str
else:
    # fallback: pick last expiry in the same YYYY-MM month
    same_month_expiries = [d for d in expiries if d.startswith(three_months.strftime("%Y-%m"))]
    if same_month_expiries:
        final_3m_expiry = same_month_expiries[-1]
    else:
        # fallback: just pick the nearest available after 90 days
        later = [d for d in expiries if d > three_months_str]
        final_3m_expiry = later[0] if later else expiries[-1]

print("📅 Target Expirations:", fridays + [final_3m_expiry])

# --- Build DataFrames ---
dataframes = {}
for i, f in enumerate(fridays):
    df = build_dataframe(portfolio, f)
    if not df.empty:
        sheet_name = f"Week_{i+1}_{f}"
        dataframes[sheet_name] = df

# Add 2-month expiry sheet
df_2m = build_dataframe(portfolio, final_2m_expiry)
if not df_2m.empty:
    dataframes[f"3M_{final_2m_expiry}"] = df_2m

# Add 3-month expiry sheet
df_3m = build_dataframe(portfolio, final_3m_expiry)
if not df_3m.empty:
    dataframes[f"3M_{final_3m_expiry}"] = df_3m

# --- Close Excel if open ---
close_excel_if_open(os.path.abspath(output_file))

# --- Save to multiple sheets ---
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    for sheet, df in dataframes.items():
        df.to_excel(writer, index=False, sheet_name=sheet)

print(f"\n✅ Exported to {output_file} with {len(dataframes)} sheets")

# --- Open Excel file ---
if sys.platform.startswith("win"):
    os.startfile(output_file)
elif sys.platform == "darwin":
    subprocess.call(["open", output_file])
else:
    subprocess.call(["xdg-open", output_file])
