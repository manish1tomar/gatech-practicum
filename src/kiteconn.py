from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from kiteconnect import KiteConnect

api_key = "5anytu7fiujo7jlp"
api_secret = "c9g8sylx47g7ec0uurqx5gnqzy8wlzbj"
user_id = "TB3804"
password = "Monu@123"
pin = "784392"

kite = KiteConnect(api_key=api_key)
#kite.set_session_expiry_hook(True)
print(kite.login_url())
login_url = kite.login_url()

# Open browser and automate login
driver = webdriver.Chrome()
driver.get(login_url)

'''
7xhLJa2mdYi1cmCqxkhTkovu8Js3bXhf
'''
time.sleep(5)
driver.find_element(By.ID, "userid").send_keys(user_id)
driver.find_element(By.ID, "password").send_keys(password)
driver.find_element(By.CLASS_NAME, "actions").click()

time.sleep(5)
driver.find_element(By.ID, "userid").send_keys(pin)
driver.find_element(By.CLASS_NAME, "actions").click()
# Wait and extract request_token from redirected URL
time.sleep(10)
driver.find_element(By.XPATH, '//*[@id="container"]/div/div/form/div/button').click()
current_url = driver.current_url
print(current_url)
time.sleep(10)
driver.quit()

time.sleep(2)
import urllib.parse as urlparse
parsed = urlparse.urlparse(current_url)
time.sleep(2)
request_token = urlparse.parse_qs(parsed.query)["request_token"][0]

print("Access token:", data["access_token"])
# After generating token
with open("access_token.txt", "w") as f:
    f.write(data["access_token"])

# Later in code
with open("access_token.txt", "r") as f:
    access_token = f.read()
