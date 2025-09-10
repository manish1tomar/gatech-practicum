"""
ATM Covered Call Returns for NIFTY & BANKNIFTY Weekly Options (next 4 expiries)

- Uses nsepython to fetch option chain
- Finds the next 4 weekly expiries
- Calculates flat and if-called returns (% and annualized)
- Computes absolute profit per lot (₹) using correct lot sizes
- Saves results into Excel with each expiry in a separate tab
"""

import os
import sys
import math
import psutil
import pandas as pd
from datetime import date
from dateutil import parser as dateparser
from nsepython import option_chain

OUTPUT_XLSX = "nifty_banknifty_weekly_covered_calls.xlsx"

INDEX_LIST = {
    "NIFTY": 50,       # lot size 50
    "BANKNIFTY": 15    # lot size 15
}

# -------------------------------
# Helpers
# -------------------------------

def pick_next_weeklies(oc_data, count=4):
    expiries = oc_data.get("records", {}).get("expiryDates") or []
    parsed = []
    for s in expiries:
        try:
            dt = dateparser.parse(s, dayfirst=True)
            parsed.append((dt, s))
        except Exception:
            continue
    parsed.sort(key=lambda x: x[0])
    return [s for _, s in parsed[:count]]

def nearest_strike(strikes, underlying):
    return min(strikes, key=lambda k: abs(k - underlying))

def compute_returns(stock_price, strike, premium, days_to_expiry):
    intrinsic = max(stock_price - strike, 0.0)
    time_value = premium - intrinsic
    net_debit = stock_price - premium
    if net_debit <= 0:
        return float('nan'), float('nan'), float('nan'), float('nan')
    flat_ret = time_value / net_debit
    if_called_ret = ((strike - stock_price) + premium) / net_debit
    # Annualized
    flat_ann = (1 + flat_ret) ** (365/days_to_expiry) - 1 if days_to_expiry else float('nan')
    if_called_ann = (1 + if_called_ret) ** (365/days_to_expiry) - 1 if days_to_expiry else float('nan')
    return flat_ret, if_called_ret, flat_ann, if_called_ann

def days_between(d1, d2):
    return (d2 - d1).days

# -------------------------------
# Excel handling
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

    for sym, lot in INDEX_LIST.items():
        try:
            oc = option_chain(sym)
            records = oc.get("records", {})
            underlying = float(records.get("underlyingValue") or 0.0)
            print(f"{sym} underlying: {underlying}")

            expiries = pick_next_weeklies(oc, count=4)
            strikes = sorted({float(d["strikePrice"]) for d in records.get("data", [])})

            for exp_str in expiries:
                k = nearest_strike(strikes, underlying)
                row = next((r for r in records.get("data", [])
                            if r["strikePrice"] == k and r["expiryDate"] == exp_str and r.get("CE")), None)
                if not row:
                    continue
                ce = row["CE"]
                premium = float(ce.get("lastPrice") or ce.get("closePrice") or 0.0)

                try:
                    exp_dt = dateparser.parse(exp_str, dayfirst=True).date()
                    dte = max(1, days_between(date.today(), exp_dt))
                except Exception:
                    exp_dt, dte = None, None

                flat_ret, if_called_ret, flat_ann, if_called_ann = compute_returns(underlying, k, premium, dte)

                # Absolute rupee profit per lot
                flat_abs = round(flat_ret * underlying * lot, 2)
                if_called_abs = round(if_called_ret * underlying * lot, 2)

                all_rows.append({
                    "symbol": sym,
                    "lot_size": lot,
                    "underlying": round(underlying, 2),
                    "expiry": exp_str,
                    "strike_atm": k,
                    "premium": round(premium, 2),
                    "flat_return%": round(flat_ret * 100, 3),
                    "if_called_return%": round(if_called_ret * 100, 3),
                    "flat_ann%": round(flat_ann * 100, 2),
                    "if_called_ann%": round(if_called_ann * 100, 2),
                    "flat_abs_₹": flat_abs,
                    "if_called_abs_₹": if_called_abs,
                    "days_to_expiry": dte,
                    "data_timestamp": records.get("timestamp")
                })

        except Exception as e:
            print(f"[ERR] {sym}: {e}")
            continue

    if not all_rows:
        print("No data found.")
        return

    df = pd.DataFrame(all_rows)
    df["expiry_dt"] = pd.to_datetime(df["expiry"], format="%d-%b-%Y", errors="coerce")

    close_excel_if_open(OUTPUT_XLSX)
    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        for exp in sorted(df["expiry"].unique()):
            subdf = df[df["expiry"] == exp].copy()
            subdf = subdf.sort_values("flat_return%", ascending=False)
            subdf.drop(columns=["expiry_dt"], inplace=True)
            subdf.to_excel(writer, sheet_name=exp, index=False)

    print(f"Saved -> {OUTPUT_XLSX}")
    open_excel(OUTPUT_XLSX)

if __name__ == "__main__":
    main()
