from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize the WebDriver
service = Service(executable_path="./testing/chromedriver.exe")
driver = webdriver.Chrome(service=service)

try:
    # Open the target URL
    driver.get('http://localhost:8501/')

    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'choice'))
    )

    # Find the choice div and buttons
    choice_div = driver.find_element(By.CLASS_NAME, 'choice')
    buttons = choice_div.find_elements(By.TAG_NAME, 'a')

    for button in buttons:
        try:
            button.click()
            print(f"Clicked on button: {button.text}")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(5)
            driver.back()
            time.sleep(5)
        except Exception as e:
            print(f"Failed to click on button: {button.text} due to {e}")

    time.sleep(5)

finally:
    # Quit the WebDriver
    driver.quit()