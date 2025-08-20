import ccxt

exchange = ccxt.cryptocom({
    "apiKey": "oER5Gcykjw7YRh542EkM5B",
    "secret": "cxakp_E3TQJPUHhYtWMn7JwhmCq8",
    "enableRateLimit": True,
})

print('crypto' in ccxt.exchanges)
print('cryptocom' in ccxt.exchanges)
print(exchange.fetch_balance())
