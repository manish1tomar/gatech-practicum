import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ------------------------------
# PARAMETERS
# ------------------------------
ticker = "AAPL"  # Change stock ticker here
start_date = "2024-01-01"  # Start of timeframe
end_date = "2025-09-10"    # End of timeframe

# ------------------------------
# FETCH INSIDER DATA
# ------------------------------
stock = yf.Ticker(ticker)

# yfinance provides insider transactions (if available)
insider_df = stock.insider_transactions
if insider_df is None or insider_df.empty:
    print("No insider data found for this ticker in yfinance.")


if insider_df is None or insider_df.empty:
    raise ValueError(f"No insider data available for {ticker}")

# Clean and filter timeframe
insider_df = insider_df.reset_index()

# Clean and filter timeframe
insider_df = insider_df.dropna(subset=['Start Date', 'Value'])
insider_df['Start Date'] = pd.to_datetime(insider_df['Start Date'], errors='coerce')
insider_df = insider_df.dropna(subset=['Start Date'])

# Filter timeframe
insider_df = insider_df[(insider_df['Start Date'] >= start_date) & (insider_df['Start Date'] <= end_date)]

# Filter for Buy/Sell
insider_df = insider_df[insider_df['Transaction'].isin(['P - Purchase', 'S - Sale'])]
insider_df['Action'] = insider_df['Transaction'].map(lambda x: 'Buy' if 'Purchase' in x else 'Sell')

# Now proceed with grouping → plotting

# Keep relevant columns
# Use the correct Value column
df = insider_df[['Start Date', 'Value', 'Action']].copy()
df.rename(columns={'Start Date': 'Date'}, inplace=True)

# Fix date type
df['Date'] = pd.to_datetime(df['Date'])

# Group by date/action
daily_stats = df.groupby(['Date', 'Action'])['Value'].sum().unstack(fill_value=0)

# Ensure Buy/Sell columns exist
for col in ['Buy', 'Sell']:
    if col not in daily_stats.columns:
        daily_stats[col] = 0

# Sort by date
daily_stats = daily_stats.sort_index()

# Add cumulative + net
daily_stats['Cum_Buy'] = daily_stats['Buy'].cumsum()
daily_stats['Cum_Sell'] = daily_stats['Sell'].cumsum()
daily_stats['Net_Change'] = daily_stats['Buy'] - daily_stats['Sell']
daily_stats['Cum_Net'] = daily_stats['Net_Change'].cumsum()

# ------------------------------
# VISUALIZATION
# ------------------------------
plt.style.use("seaborn-v0_8")

fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot cumulative buys/sells
ax1.plot(daily_stats.index, daily_stats['Cum_Buy'], label='Cumulative Buy ($)', color='green', linewidth=2)
ax1.plot(daily_stats.index, daily_stats['Cum_Sell'], label='Cumulative Sell ($)', color='red', linewidth=2)

# Secondary axis: Net Change
ax2 = ax1.twinx()
ax2.plot(daily_stats.index, daily_stats['Cum_Net'], label='Cumulative Net ($)', color='blue', linestyle="--", linewidth=2)

# Formatting
ax1.set_title(f"Insider Transactions for {ticker} ({start_date} to {end_date})", fontsize=14, fontweight='bold')
ax1.set_xlabel("Date")
ax1.set_ylabel("Cumulative Buy/Sell ($)")
ax2.set_ylabel("Cumulative Net ($)")

# Rotate x-axis labels
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b-%Y"))
plt.setp(ax1.get_xticklabels(), rotation=30, ha="right")

# Legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.tight_layout()
plt.show()
