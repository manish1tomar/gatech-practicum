'''import ccxt

exchange = ccxt.cryptocom({
    "apiKey": "eRUhcDv9E7UGD7L1mwxSw2",
    "secret": "cxakp_cm7Hfn2p5vUSEhZmdVMcj5",
})

print('crypto' in ccxt.exchanges)
print('cryptocom' in ccxt.exchanges)
print(exchange.fetch_balance())

order = exchange.create_market_buy_order("XRP/USD", 1)
print(order)
'''
import yfinance as yf

ticker = "AAPL"
stock = yf.Ticker(ticker)
insider_df = stock.insider_transactions

print(insider_df)
