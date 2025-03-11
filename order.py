import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
profile_path = "path/to/persistent/profile"  # ensure this matches the profile used in add_product_to_cart
chrome_options.add_argument(f"--user-data-dir={profile_path}")
driver = webdriver.Chrome(options=chrome_options)
try:
    # Navigate to the cart page (or the main site if cart state is preserved)
    driver.get("https://tershine.com/sv/checkout")

    WebDriverWait(driver, 10).until(EC.url_contains("checkout"))
    checkout_url = driver.current_url
    while True:
        time.sleep(1)
except Exception as ex:
    checkout_url = "Error retrieving checkout URL: " + str(ex)
finally:
    driver.quit()