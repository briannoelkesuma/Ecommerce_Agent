import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set a persistent profile directory (change this to your desired directory)
profile_path = "path/to/persistent/profile"  # Replace with your actual directory

# Configure Chrome options to use the persistent profile
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={profile_path}")

# Initialize Chrome driver with the persistent profile
driver = webdriver.Chrome(options=chrome_options)

try:
    # Navigate to the main page
    driver.get("https://tershine.com/")
    
    # Wait for and access the search box, then enter the product name
    clickable_search_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input.input"))
    )
    clickable_search_box.clear()
    clickable_search_box.send_keys("Dissolve - Kallavfettning 1 L")
    
    # Wait for the search results and click the first link
    search_results = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.search-result"))
    )
    first_link = WebDriverWait(search_results, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "li a"))
    )
    first_link.click()
    
    # Wait for product page to load and click the buy button
    product_page = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.action"))
    )
    buy_button = WebDriverWait(product_page, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.button.buy"))
    )
    buy_button.click()
    
    # Wait for cart pop up to load
    cart_pop_up = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "section.section.footer"))
    )
    
    # Optionally, check for free shipping information
    try:
        free_shipping_info = WebDriverWait(cart_pop_up, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.shipping-information__remaining"))
        )
        free_shipping_texts = free_shipping_info.text
    except:
        free_shipping_texts = "Eligible for free shipping"
    
    # Proceed to checkout
    checkout_products = WebDriverWait(cart_pop_up, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.button.is-fullwidth.buy"))
    )
    checkout_products.click()
    
    # At this point the payment page is loaded. You can print its URL:
    print("Payment URL:", driver.current_url)
    
    # The browser stays open with your persistent session. You can access the payment URL again later
    while True:
        time.sleep(1)
        
finally:
    # When you're done, you can close the driver.
    # driver.quit()  # Uncomment this line if you want to close the browser on exit.
    pass
