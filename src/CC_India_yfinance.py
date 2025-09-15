#!/usr/bin/env python3
"""
Compute ATM Collar strategy returns for the next three monthly expiries for all Nifty50 stocks
using yfinance (Yahoo Finance).

Output: Excel workbook with one sheet per expiry (sorted by flat_return% desc).

Requires: yfinance, pandas, openpyxl, psutil
"""
import os
import sys
import math
import time
import psutil
import pandas as pd
from datetime import date, datetime
from dateutil import parser as dateparser
import yfinance as yf

OUTPUT_XLSX = "nifty50_atm_collars_yf.xlsx"

# Use the same list you provided (kept here truncated for brevity; replace with your full list)
NIFTY50_SYMBOLS = [
'360ONE','ABB','ABCAPITAL','ADANIENSOL','ADANIENT','ADANIGREEN','ADANIPORTS',
'ALKEM','AMBER','AMBUJACEM','ANGELONE','APLAPOLLO','APOLLOHOSP','ASHOKLEY',
'ASIANPAINT','ASTRAL','AUBANK','AUROPHARMA','AXISBANK','BAJAJ-AUTO',
'BAJAJFINSV','BAJFINANCE','BANDHANBNK','BANKBARODA','BANKINDIA','BDL',
'BEL','BHARATFORG','BHARTIARTL','BHEL','BIOCON','BLUESTARCO','BOSCHLTD',
'BPCL','BRITANNIA','BSE','CAMS','CANBK','CDSL','CHOLAFIN','CIPLA','COALINDIA',
'COFORGE','COLPAL','CONCOR','CROMPTON','CUMMINSIND','CYIENT','DABUR','DALBHARAT',
'DELHIVERY','DIVISLAB','DIXON','DLF','DMART','DRREDDY','EICHERMOT','ETERNAL',
'EXIDEIND','FEDERALBNK','FORTIS','GAIL','GLENMARK','GMRAIRPORT','GODREJCP',
'GODREJPROP','GRASIM','HAL','HAVELLS','HCLTECH','HDFCAMC','HDFCBANK','HDFCLIFE',
'HEROMOTOCO','HFCL','HINDALCO','HINDPETRO','HINDUNILVR','HINDZINC','HUDCO',
'ICICIBANK','ICICIGI','ICICIPRULI','IDEA','IDFCFIRSTB','IEX','IGL','IIFL',
'INDHOTEL','INDIANB','INDIGO','INDUSINDBK','INDUSTOWER','INFY','INOXWIND','IOC',
'IRCTC','IREDA','IRFC','ITC','JINDALSTEL','JIOFIN','JSWENERGY','JSWSTEEL',
'JUBLFOOD','KALYANKJIL','KAYNES','KEI','KFINTECH','KOTAKBANK','KPITTECH',
'LAURUSLABS','LICHSGFIN','LICI','LODHA','LT','LTF','LTIM','LUPIN','M&M',
'MANAPPURAM','MANKIND','MARICO','MARUTI','MAXHEALTH','MAZDOCK','MCX','MFSL',
'MOTHERSON','MPHASIS','MUTHOOTFIN','NATIONALUM','NAUKRI','NBCC','NCC','NESTLEIND',
'NHPC','NMDC','NTPC','NUVAMA','NYKAA','OBEROIRLTY','OFSS','OIL','ONGC','PAGEIND',
'PATANJALI','PAYTM','PERSISTENT','PETRONET','PFC','PGEL','PHOENIXLTD','PIDILITIND',
'PIIND','PNB','PNBHOUSING','POLICYBZR','POLYCAB','POWERGRID','PPLPHARMA','PRESTIGE',
'RBLBANK','RECLTD','RELIANCE','RVNL','SAIL','SAMMAANCAP','SBICARD','SBILIFE','SBIN',
'SHREECEM','SHRIRAMFIN','SIEMENS','SOLARINDS','SONACOMS','SRF','SUNPHARMA','SUPREMEIND',
'SUZLON','SYNGENE','TATACHEM','TATACONSUM','TATAELXSI','TATAMOTORS','TATAPOWER',
'TATASTEEL','TATATECH','TCS','TECHM','TIINDIA','TITAGARH','TITAN','TORNTPHARM',
'TORNTPOWER','TRENT','TVSMOTOR','ULTRACEMCO','UNIONBANK','UNITDSPR','UNOMINDA',
'UPL','VBL','VEDL','VOLTAS','WIPRO','YESBANK','ZYDUSLIFE'
]

# -------------------------------
# Helpers
# -------------------------------

def pick_next_three_expiries_from_yf(options_list):
    # yfinance returns expiries as ['YYYY-MM-DD', ...] already sorted ascending
    if not options_list:
        return []
    return options_list[:3]

def nearest_strike(strikes, underlying):
    return min(strikes, key=lambda k: abs(k - underlying))

def days_between(d1, d2):
    return (d2 - d1).days

def compute_collar_returns(stock_price, strike, call_prem, put_prem, days_to_expiry):
    # net_debit: buy stock, sell call (receive call_prem), buy put (pay put_prem)
    net_debit = stock_price - call_prem + put_prem
    if net_debit <= 0 or days_to_expiry is None or days_to_expiry <= 0:
        return float('nan'), float('nan'), float('nan'), float('nan'), float('nan'), float('nan')

    # Flat return (stock unchanged)
    flat_ret = (call_prem - put_prem) / net_debit

    # If called away (stock > strike)
    if_called_ret = ((strike - stock_price) + (call_prem - put_prem)) / net_debit

    # If stock crashes below put strike (worst case)
    if_put_ret = ((strike - stock_price) + (call_prem - put_prem)) / net_debit

    # Annualized
    try:
        flat_ann = (1 + flat_ret) ** (365.0/days_to_expiry) - 1
        if_called_ann = (1 + if_called_ret) ** (365.0/days_to_expiry) - 1
        if_put_ann = (1 + if_put_ret) ** (365.0/days_to_expiry) - 1
    except Exception:
        flat_ann = if_called_ann = if_put_ann = float('nan')

    return flat_ret, if_called_ret, if_put_ret, flat_ann, if_called_ann, if_put_ann

# -------------------------------
# Excel helpers
# -------------------------------

def close_excel_if_open(file_path):
    # Only attempt on Windows; try to close any Excel process holding the file
    try:
        file_abspath = os.path.abspath(file_path).lower()
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            name = proc.info.get('name') or ''
            if "excel" in name.lower():
                try:
                    for f in proc.open_files():
                        if f.path.lower() == file_abspath:
                            proc.terminate()
                            proc.wait(timeout=5)
                            print("Closed Excel process holding the file.")
                            return
                except Exception:
                    continue
    except Exception:
        pass

def open_excel(file_path):
    if sys.platform.startswith("win"):
        try:
            os.startfile(file_path)
        except Exception as e:
            print("Could not open Excel:", e)
    else:
        print("Excel auto-open supported only on Windows.")

# -------------------------------
# Main
# -------------------------------

def main():
    all_rows = []

    for sym in NIFTY50_SYMBOLS:
        yf_ticker = f"{sym}.NS"  # Yahoo India suffix
        try:
            t = yf.Ticker(yf_ticker)
            # Get underlying price robustly
            underlying = None
            try:
                info = t.fast_info if hasattr(t, "fast_info") else t.info
                # try multiple possible fields
                underlying = info.get('last_price') or info.get('regularMarketPrice') or info.get('previousClose')
            except Exception:
                pass

            # fallback to history close
            if underlying is None:
                try:
                    hist = t.history(period="1d")
                    if not hist.empty:
                        underlying = float(hist['Close'].iloc[-1])
                except Exception:
                    pass

            if underlying is None or math.isnan(float(underlying)):
                print(f"[WARN] No underlying for {yf_ticker}")
                continue
            underlying = float(underlying)

            options_list = t.options  # list of expiries as 'YYYY-MM-DD'
            expiries = pick_next_three_expiries_from_yf(options_list)
            if not expiries:
                print(f"[WARN] No expiries for {yf_ticker}")
                continue

            # For each expiry, fetch option chain DataFrames
            for exp in expiries:
                try:
                    oc = t.option_chain(exp)
                    calls = oc.calls
                    puts = oc.puts
                    # strike column named 'strike' in yfinance
                    strikes = sorted(set(calls['strike'].astype(float).tolist() + puts['strike'].astype(float).tolist()))
                    if not strikes:
                        continue
                    k = nearest_strike(strikes, underlying)

                    # find the call and put rows matching strike
                    ce_rows = calls[calls['strike'] == k]
                    pe_rows = puts[puts['strike'] == k]
                    if ce_rows.empty or pe_rows.empty:
                        # If exact match not found (float equality), use nearest in DataFrame
                        try:
                            ce_row = calls.iloc[(calls['strike'] - k).abs().argsort()[:1]].iloc[0]
                            pe_row = puts.iloc[(puts['strike'] - k).abs().argsort()[:1]].iloc[0]
                        except Exception:
                            continue
                    else:
                        ce_row = ce_rows.iloc[0]
                        pe_row = pe_rows.iloc[0]

                    # prefer 'lastPrice', else 'bid'/'ask' midpoint, else 'lastPrice' fallback 0.0
                    def pick_premium(row):
                        for col in ('lastPrice', 'Last Price', 'last_trade_price', 'lastprice'):
                            if col in row and pd.notna(row[col]):
                                return float(row[col])
                        # try midpoint of bid/ask if available
                        if 'bid' in row and 'ask' in row and pd.notna(row['bid']) and pd.notna(row['ask']):
                            return (float(row['bid']) + float(row['ask'])) / 2.0
                        # else 0
                        return 0.0

                    call_prem = pick_premium(ce_row)
                    put_prem = pick_premium(pe_row)

                    # compute DTE
                    try:
                        exp_dt = datetime.strptime(exp, "%Y-%m-%d").date()
                        dte = max(1, days_between(date.today(), exp_dt))
                    except Exception:
                        dte = None

                    flat_ret, if_called_ret, if_put_ret, flat_ann, if_called_ann, if_put_ann = compute_collar_returns(
                        underlying, k, call_prem, put_prem, dte)

                    all_rows.append({
                        "symbol": sym,
                        "yf_ticker": yf_ticker,
                        "underlying": round(underlying, 2),
                        "expiry": exp,
                        "expiry_dt": exp,
                        "strike_atm": k,
                        "call_premium": round(call_prem, 2),
                        "put_premium": round(put_prem, 2),
                        "flat_return%": round(flat_ret * 100, 3) if not math.isnan(flat_ret) else float('nan'),
                        "if_called_return%": round(if_called_ret * 100, 3) if not math.isnan(if_called_ret) else float('nan'),
                        "if_put_return%": round(if_put_ret * 100, 3) if not math.isnan(if_put_ret) else float('nan'),
                        "flat_ann%": round(flat_ann * 100, 2) if not math.isnan(flat_ann) else float('nan'),
                        "if_called_ann%": round(if_called_ann * 100, 2) if not math.isnan(if_called_ann) else float('nan'),
                        "if_put_ann%": round(if_put_ann * 100, 2) if not math.isnan(if_put_ann) else float('nan'),
                        "days_to_expiry": dte,
                    })
                    # polite pause to avoid throttling
                    time.sleep(0.2)
                except Exception as e:
                    print(f"[WARN] {yf_ticker} expiry {exp} -> {e}")
                    continue

            print(f"{yf_ticker} done (underlying {underlying})")
        except Exception as e:
            print(f"[ERR] {yf_ticker}: {e}")
            continue

    if not all_rows:
        print("No data collected. Exiting.")
        return

    df = pd.DataFrame(all_rows)
    # Ensure expiry strings are parsed if possible
    df["expiry_dt"] = pd.to_datetime(df["expiry_dt"], format="%Y-%m-%d", errors="coerce")

    # Close Excel if open
    close_excel_if_open(OUTPUT_XLSX)

    # Write each expiry to its own sheet
    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        for exp in sorted(df["expiry"].unique()):
            subdf = df[df["expiry"] == exp].copy()
            # Sort reverse by flat_return%
            subdf = subdf.sort_values("flat_return%", ascending=False)
            # optionally reorder columns
            cols = ["symbol","yf_ticker","underlying","expiry","days_to_expiry","strike_atm",
                    "call_premium","put_premium","flat_return%","flat_ann%","if_called_return%","if_called_ann%",
                    "if_put_return%","if_put_ann%"]
            cols = [c for c in cols if c in subdf.columns]
            subdf = subdf[cols]
            # Excel sheet names can't exceed 31 characters: shorten if needed
            sheet_name = exp if len(exp) <= 31 else exp[:31]
            subdf.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Saved -> {OUTPUT_XLSX}")
    open_excel(OUTPUT_XLSX)


if __name__ == "__main__":
    main()
