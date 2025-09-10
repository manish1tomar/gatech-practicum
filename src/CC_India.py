"""
Compute ATM Collar strategy returns for the next three monthly expiries for all Nifty50 stocks
using nsepython.

Enhancements:
- Results sorted by flat return % (descending).
- Each expiry in its own Excel tab.
- Annualized return columns added.

Requires: nsepython, pandas, openpyxl, psutil
"""

import os
import sys
import math
import psutil
import pandas as pd
from datetime import date
from dateutil import parser as dateparser
from nsepython import option_chain

OUTPUT_XLSX = "nifty50_atm_collars.xlsx"

NIFTY50_SYMBOLS = [
    "ADANIENT","ADANIPORTS","APOLLOHOSP","ASIANPAINT","AXISBANK","BAJAJ-AUTO",
    "BAJFINANCE","BAJAJFINSV","BHARTIARTL","BPCL","BRITANNIA","CIPLA","COALINDIA",
    "DIVISLAB","DRREDDY","EICHERMOT","GRASIM","HCLTECH","HDFCBANK","HDFCLIFE",
    "HEROMOTOCO","HINDALCO","HINDUNILVR","ICICIBANK","INDUSINDBK","INFY","ITC",
    "JSWSTEEL","KOTAKBANK","LT","LTIM","M&M","MARUTI","NESTLEIND","NTPC","ONGC",
    "POWERGRID","RELIANCE","SBILIFE","SBIN","SHRIRAMFIN","SUNPHARMA","TATACONSUM",
    "TATAMOTORS","TATASTEEL","TCS","TECHM","TITAN","ULTRACEMCO","WIPRO"
]

# -------------------------------
# Helpers
# -------------------------------

def pick_next_three_expiries(oc_data):
    expiries = oc_data.get("records", {}).get("expiryDates") or []
    parsed = []
    for s in expiries:
        try:
            dt = dateparser.parse(s, dayfirst=True)
            parsed.append((dt, s))
        except Exception:
            continue
    parsed.sort(key=lambda x: x[0])
    return [s for _, s in parsed[:3]]


def nearest_strike(strikes, underlying):
    return min(strikes, key=lambda k: abs(k - underlying))


def days_between(d1, d2):
    return (d2 - d1).days


def compute_collar_returns(stock_price, strike, call_prem, put_prem, days_to_expiry):
    net_debit = stock_price - call_prem + put_prem
    if net_debit <= 0:
        return float('nan'), float('nan'), float('nan'), float('nan'), float('nan'), float('nan')

    # Flat return (stock unchanged)
    flat_ret = (call_prem - put_prem) / net_debit

    # If called away (stock > strike)
    if_called_ret = ((strike - stock_price) + (call_prem - put_prem)) / net_debit

    # If stock crashes below put strike (worst case)
    if_put_ret = ((strike - stock_price) + (call_prem - put_prem)) / net_debit

    # Annualized
    flat_ann = (1 + flat_ret) ** (365/days_to_expiry) - 1 if days_to_expiry else float('nan')
    if_called_ann = (1 + if_called_ret) ** (365/days_to_expiry) - 1 if days_to_expiry else float('nan')
    if_put_ann = (1 + if_put_ret) ** (365/days_to_expiry) - 1 if days_to_expiry else float('nan')

    return flat_ret, if_called_ret, if_put_ret, flat_ann, if_called_ann, if_put_ann


# -------------------------------
# Excel helpers
# -------------------------------

def close_excel_if_open(file_path):
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if "excel" in proc.info['name'].lower():
                for file in proc.open_files():
                    if file.path.lower() == os.path.abspath(file_path).lower():
                        proc.terminate()
                        proc.wait(timeout=5)
                        print("Closed Excel process holding the file.")
                        return
        except Exception:
            continue


def open_excel(file_path):
    if sys.platform.startswith("win"):
        os.startfile(file_path)
    else:
        print("Excel auto-open supported only on Windows.")


# -------------------------------
# Main
# -------------------------------

def main():
    all_rows = []

    for sym in NIFTY50_SYMBOLS:
        try:
            oc = option_chain(sym)
            records = oc.get("records", {})
            underlying = float(records.get("underlyingValue") or 0.0)
            if not underlying or math.isnan(underlying):
                print(f"[WARN] No underlying for {sym}")
                continue

            expiries = pick_next_three_expiries(oc)
            if not expiries:
                print(f"[WARN] No expiries for {sym}")
                continue

            strikes = sorted({float(d["strikePrice"]) for d in records.get("data", [])})

            for exp_str in expiries:
                k = nearest_strike(strikes, underlying)
                row = next((r for r in records.get("data", []) if r["strikePrice"] == k and r["expiryDate"] == exp_str and r.get("CE")), None)
                putrow = next((r for r in records.get("data", []) if r["strikePrice"] == k and r["expiryDate"] == exp_str and r.get("PE")), None)
                if not row or not putrow:
                    continue

                ce = row["CE"]
                pe = putrow["PE"]
                call_prem = float(ce.get("lastPrice") or ce.get("closePrice") or 0.0)
                put_prem = float(pe.get("lastPrice") or pe.get("closePrice") or 0.0)

                try:
                    exp_dt = dateparser.parse(exp_str, dayfirst=True).date()
                    dte = max(1, days_between(date.today(), exp_dt))
                except Exception:
                    exp_dt, dte = None, None

                flat_ret, if_called_ret, if_put_ret, flat_ann, if_called_ann, if_put_ann = compute_collar_returns(
                    underlying, k, call_prem, put_prem, dte)

                all_rows.append({
                    "symbol": sym,
                    "underlying": round(underlying, 2),
                    "expiry": exp_str,
                    "strike_atm": k,
                    "call_premium": round(call_prem, 2),
                    "put_premium": round(put_prem, 2),
                    "flat_return%": round(flat_ret*100, 3),
                    "if_called_return%": round(if_called_ret*100, 3),
                    "if_put_return%": round(if_put_ret*100, 3),
                    "flat_ann%": round(flat_ann*100, 2),
                    "if_called_ann%": round(if_called_ann*100, 2),
                    "if_put_ann%": round(if_put_ann*100, 2),
                    "days_to_expiry": dte,
                    "data_timestamp": records.get("timestamp")
                })

            print(f"{sym} done")

        except Exception as e:
            print(f"[ERR] {sym}: {e}")
            continue

    if not all_rows:
        print("No data collected. Exiting.")
        return

    df = pd.DataFrame(all_rows)
    df["expiry_dt"] = pd.to_datetime(df["expiry"], format="%d-%b-%Y", errors="coerce")

    # Close Excel if open
    close_excel_if_open(OUTPUT_XLSX)

    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        for exp in sorted(df["expiry"].unique()):
            subdf = df[df["expiry"] == exp].copy()
            # Sort reverse by flat_return%
            subdf = subdf.sort_values("flat_return%", ascending=False)
            subdf.drop(columns=["expiry_dt"], inplace=True)
            subdf.to_excel(writer, sheet_name=exp, index=False)

    print(f"Saved -> {OUTPUT_XLSX}")

    open_excel(OUTPUT_XLSX)


if __name__ == "__main__":
    main()
