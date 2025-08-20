from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
import time
import os

# Path to downloaded .xpi file
EXTENSION_XPI = r"C:\Users\PC\Downloads\check_us_visa_slots-4.6.5.1.xpi"

# Access code you want to input
ACCESS_CODE = "BV6KNI"

# Firefox options
options = Options()
options.add_argument("-start-debugger-server")
profile = FirefoxProfile()

# Install the extension
profile.add_extension(extension=EXTENSION_XPI)

# Launch Firefox
driver = webdriver.Firefox(options=options)
driver = webdriver.Firefox()

try:
    # Step 1: Load the extension’s page directly (if known)
    EXTENSION_INTERNAL_PAGE = "moz-extension://<extension-uuid>/popup.html"  # You'll need to update this manually
    print("Now opening extension's internal page (you must find correct moz-extension URL manually)...")
    time.sleep(5)

    # Firefox does not expose extension UUIDs to Selenium; use this as a placeholder:
    # In practice, you’ll need to manually inspect the UUID or hardcode it
    # For now, just open the US visa scheduling website as a fallback
    driver.get("https://abc.com/")
    time.sleep(3)

    # (Optional) Once you know extension URL:
    # driver.get("moz-extension://<uuid>/popup.html")

    # If popup form is shown:
    # input_box = driver.find_element(By.ID, "access-code-input")
    # input_box.send_keys(ACCESS_CODE)
    # submit_button = driver.find_element(By.ID, "submit-access-code")
    # submit_button.click()

    print("Access code process would go here.")

except Exception as e:
    print("Error:", e)

finally:
    input("Press Enter to quit...")
    driver.quit()
