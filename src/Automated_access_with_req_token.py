from kiteconnect import KiteConnect

api_key = "5anytu7fiujo7jlp"
api_secret = "c9g8sylx47g7ec0uurqx5gnqzy8wlzbj"
user_id = "TB3804"
password = "Monu@123"

kite = KiteConnect(api_key=api_key)

# Exchange request token for access token
data = kite.generate_session(request_token="FNgvkR2Muw0tmjg8Nksegeo3Pnp4lSC6",api_secret=api_secret)
kite.set_access_token(data["access_token"])
print(kite.holdings())
print(kite.instruments())
