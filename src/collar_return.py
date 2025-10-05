import yfinance as yf
import pandas as pd
import datetime
import os
import sys, psutil
import subprocess

# -------------------------------
# Function to calculate collar yield
# -------------------------------
def get_collar_yield(ticker, shares, target_expiry, protection=0.95):
    stock = yf.Ticker(ticker)
    price = stock.history(period="1d")["Close"].iloc[-1]

    expirations = stock.options
    if target_expiry not in expirations:
        return None

    opt_chain = stock.option_chain(target_expiry)

    # --- ATM CALL ---
    calls = opt_chain.calls
    calls["diff"] = abs(calls["strike"] - price)
    atm_call = calls.loc[calls["diff"].idxmin()]

    # --- PROTECTION PUT ---
    puts = opt_chain.puts
    target_put_strike = price * protection
    puts["diff"] = abs(puts["strike"] - target_put_strike)
    ntm_put = puts.loc[puts["diff"].idxmin()]

    # Premiums
    call_premium = atm_call["bid"]
    put_premium = ntm_put["ask"]

    expiry_date = datetime.datetime.strptime(target_expiry, "%Y-%m-%d").date()
    days_to_expiry = (expiry_date - datetime.date.today()).days

    # Collar return calculation
    upside = atm_call["strike"] - price if atm_call["strike"] > price else 0
    net_premium = call_premium - put_premium
    net_return = ((atm_call["strike"] + call_premium) - (price + put_premium)) / (price + put_premium)
    max_loss = ((ntm_put["strike"] + call_premium) - (price + put_premium)) / (price + put_premium)
    annualized_return = net_return * (365 / days_to_expiry) if days_to_expiry > 0 else 0

    return {
        "Ticker": ticker,
        "Stock Price": round(price, 2),
        "ATM Call Strike": atm_call["strike"],
        "ATM Call Premium": round(call_premium, 2),
        f"Put Strike (~{int(protection*100)}%)": ntm_put["strike"],
        "Put Premium": round(put_premium, 2),
        "Expiry": target_expiry,
        "Days to Expiry": days_to_expiry,
        "Collar Return %": round(net_return*100, 2),
        "Max Loss %": round(max_loss * 100, 2),
        "Annualized Return %": round(annualized_return, 2),
        "Stock Value": round(price * shares, 2),
        "Net Premium Income": round(net_premium * (shares // 100), 2),
        "Protection Level": f"{int(protection*100)}%"
    }

# -------------------------------
# Build DataFrame for portfolio
# -------------------------------
def build_dataframe(portfolio, expiry_date, protection=0.95):
    results = []
    total_stock_value, total_premium = 0, 0

    for ticker, shares in portfolio.items():
        try:
            res = get_collar_yield(ticker, shares, expiry_date, protection=protection)
        except:
            pass
        if res:
            results.append(res)
            total_stock_value += res["Stock Value"]
            total_premium += res["Net Premium Income"]

    df = pd.DataFrame(results)

    if total_stock_value > 0 and not df.empty:
        totals = {
            "Ticker": "TOTAL",
            "Stock Price": "",
            "ATM Call Strike": "",
            "ATM Call Premium": "",
            f"Put Strike (~{int(protection*100)}%)": "",
            "Put Premium": "",
            "Expiry": "",
            "Days to Expiry": "",
            "Collar Return %": "",
            "Annualized Return %": "",
            "Stock Value": round(total_stock_value, 2),
            "Net Premium Income": round(total_premium, 2),
            "Protection Level": f"{int(protection*100)}%"
        }
        df = df.sort_values(by="Collar Return %", ascending=False)
        df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)

    return df

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

# -------------------------------
# Save results into Excel
# -------------------------------
def save_to_excel(portfolio, expiries, protections=[0.90, 0.95, 0.98], filename="collar_strategy.xlsx"):
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        for expiry in expiries:
            for prot in protections:
                df = build_dataframe(portfolio, expiry, protection=prot)
                sheet_name = f"{expiry}_Collar_{int(prot*100)}%"
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"✅ Results saved to {filename}")

    # --- Auto-open Excel ---
    if sys.platform.startswith("win"):
        os.startfile(filename)
    elif sys.platform == "darwin":
        subprocess.call(["open", filename])
    else:
        subprocess.call(["xdg-open", filename])

# -------------------------------
# Example Run
# -------------------------------
if __name__ == "__main__":
    #portfolio = {"AAPL": 100, "MSFT": 100, "NVDA": 100}
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
        , 'FNF': 100, "CIEN": 100, "TPR": 100, "QTUM":100
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
        , 'VNOM': 100, 'CMI':100,
    }

    close_excel_if_open(os.path.abspath("collar_strategy.xlsx"))

    # --- Get expiries ---
    first_ticker = list(portfolio.keys())[0]
    stock = yf.Ticker(first_ticker)
    expirations = stock.options

    # Next 3 expiries
    next_expiries = list(expirations[:3])

    # Find ~90d expiry (±20)
    today = datetime.date.today()
    target_days = 90
    min_days, max_days = 60, 120
    chosen_expiry = None
    for exp in expirations:
        exp_date = datetime.datetime.strptime(exp, "%Y-%m-%d").date()
        days = (exp_date - today).days
        if min_days <= days <= max_days:
            chosen_expiry = exp
            break

    # Add to list if found
    if chosen_expiry and chosen_expiry not in next_expiries:
        next_expiries.append(chosen_expiry)

    print("📅 Target Expirations:", next_expiries)

    save_to_excel(portfolio, next_expiries)
