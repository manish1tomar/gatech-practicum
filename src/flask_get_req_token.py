from flask import Flask, request
from kiteconnect import KiteConnect

app = Flask(__name__)

# Your Kite API credentials
API_KEY = "5anytu7fiujo7jlp"
API_SECRET = "c9g8sylx47g7ec0uurqx5gnqzy8wlzbj"
kite = KiteConnect(api_key=API_KEY)

@app.route("/")
def home():
    login_url = kite.login_url()
    return f'<a href="{login_url}">Login to Zerodha</a>'

@app.route("/login")
def login():
    request_token = request.args.get("request_token")
    if not request_token:
        return "Login failed or token not received."

    try:
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        kite.set_access_token(data["access_token"])
        # Save access token
        with open("access_token.txt", "w") as f:
            f.write(data["access_token"])
        return "Login successful! Access token saved."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(port=8000)
