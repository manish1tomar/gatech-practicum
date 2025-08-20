# cxakp_c9Jzz49r7masxHKRJryNj7
import requests
import hashlib
import hmac
import time
import json

# --- Configuration (Replace with your actual API Key and Secret) ---
API_KEY = "sJcEWzqfnybNACcxj5aHQV"
SECRET_KEY = "cxakp_c9Jzz49r7masxHKRJryNj7"
BASE_URL = "https://api.crypto.com/exchange/v1" # Production API endpoint

# --- Helper function for signing requests ---
def sign_request(method, id, api_key, params, nonce):
    # Sort parameters by key
    param_string = ""
    if params:
        sorted_params = sorted(params.items())
        for k, v in sorted_params:
            param_string += f"{k}{v}"

    payload = f"{method}{id}{api_key}{param_string}{nonce}"
    signature = hmac.new(
        bytes(SECRET_KEY, "utf-8"),
        bytes(payload, "utf-8"),
        hashlib.sha256
    ).hexdigest()
    return signature

# --- Example: Get Account Balance ---
def get_account_balance():
    method = "private/user-balance"
    nonce = int(time.time() * 1000) # Milliseconds timestamp
    request_id = 1 # A unique ID for your request

    params = {} # No parameters needed for user-balance

    signature = sign_request(method, request_id, API_KEY, params, nonce)

    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "id": request_id,
        "method": method,
        "api_key": API_KEY,
        "params": params,
        "nonce": nonce,
        "sig": signature
    }

    try:
        response = requests.post(f"{BASE_URL}/private/user-balance", headers=headers, json=body)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        print("Account Balance:", json.dumps(data, indent=4))
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching balance: {e}")
        return None

# --- Example: Place a Limit Buy Order ---
def place_limit_buy_order(instrument_name, price, quantity):
    method = "private/create-order"
    nonce = int(time.time() * 1000)
    request_id = 2

    params = {
        "instrument_name": instrument_name,
        "type": "LIMIT",
        "side": "BUY",
        "price": price,
        "quantity": quantity
    }

    signature = sign_request(method, request_id, API_KEY, params, nonce)

    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "id": request_id,
        "method": method,
        "api_key": API_KEY,
        "params": params,
        "nonce": nonce,
        "sig": signature
    }

    try:
        response = requests.post(f"{BASE_URL}/private/create-order", headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        print("Order Placement Response:", json.dumps(data, indent=4))
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error placing order: {e}")
        return None

if __name__ == "__main__":
    # Get account balance
    get_account_balance()

    # Example: Place a small limit buy order for BTC_USDT (adjust price and quantity carefully!)
    # place_limit_buy_order("BTC_USDT", 60000.00, 0.0001) # Uncomment to test placing an order