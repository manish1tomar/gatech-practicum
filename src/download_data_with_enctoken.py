import requests
import pandas as pd
from datetime import datetime

enctoken=+VniDV6nTfnu34fZ0hhSlR5S7ssz4DE8n0I6lM5OzE/Vr+ju1FL+VGsUDxI/8OAvj0Oy3HhQOz68wAiv8Fekish5l5k5U6jOutLGLgd4Sqq3F09bYbhQMA==
header = {
    "Authorization" : f"enctoken {enctoken}"
}
# "https://kite.zerodha.com/oms/instruments/historical/738561/5minute?user_id=TB3804&oi=1&from=2025-05-09&to=2025-05-13"