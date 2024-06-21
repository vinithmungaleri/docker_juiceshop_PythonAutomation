import time
from selenium import webdriver
import pytest
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
import json
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
import requests
import pandas as pd


@pytest.fixture(scope='function')
def setup():
    global base_url, login_url, login_email_value, login_pwd_value
    try:
        with open('C:/Users/91768/PycharmProjects/JuiceShop/config.json', 'r') as json_file:
            config_data = json.load(json_file)

        base_url = config_data['base_url']
        login_url = config_data['login_url']
        login_email_value = config_data['login']['email']
        login_pwd_value = config_data['login']['password']

    except Exception as e:
        print("Exception occurred trying to access Config JSON file:", str(e))

    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument("disable-infobars")
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    driver.get(base_url)
    print("Entered into site:", base_url)
    dismiss_container_btn = wait.until(
        ec.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'close-dialog')]")))
    dismiss_container_btn.click()

    try:
        accept_cookies = driver.find_element(By.XPATH, "//a[text()='Me want it!']")
        accept_cookies.click()
    except NoSuchElementException:
        pass

    nav_account = driver.find_element(By.ID, "navbarAccount")
    nav_account.click()
    nav_login_btn = wait.until(ec.element_to_be_clickable((By.ID, "navbarLoginButton")))
    nav_login_btn.click()

    print("Redirecting to Login Page")
    assert driver.current_url == login_url
    assert driver.find_element(By.XPATH, "//h1[text() = 'Login']").text == 'Login'
    print("Entering Login Credentials")
    login_email = driver.find_element(By.ID, 'email')
    login_email.send_keys(login_email_value)
    login_pwd = driver.find_element(By.ID, 'password')
    login_pwd.send_keys(login_pwd_value)
    login_btn = wait.until(ec.element_to_be_clickable((By.ID, 'loginButton')))
    login_btn.click()
    wait.until(ec.visibility_of_element_located((By.XPATH, "//button[@aria-label='Show the shopping cart']")))
    print("Logged In...")
    yield driver
    driver.quit()


def test_add_card_details(setup):
    driver = setup
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)

    wait.until(ec.element_to_be_clickable((By.ID, 'navbarAccount'))).click()
    wait.until(ec.visibility_of_element_located(
        (By.XPATH, "//button[@aria-label='Show Orders and Payment Menu']"))).click()
    wait.until(ec.visibility_of_element_located(
        (By.XPATH, "//button[@aria-label='Go to saved payment methods page']"))).click()

    assert driver.current_url == "http://localhost:3000/#/saved-payment-methods"
    print("Entered Payment Methods Page")
    driver.find_element(By.XPATH, "//mat-expansion-panel").click()
    card_inp_fields = driver.find_elements(By.XPATH, "//mat-expansion-panel//mat-form-field//input")
    card_expiry_dropdown = driver.find_elements(By.XPATH, "//select")

    name = card_inp_fields[0]
    card_no = card_inp_fields[1]
    expiry_month = Select(card_expiry_dropdown[0])
    expiry_year = Select(card_expiry_dropdown[1])

    print("Entering Card Details")
    wait.until(ec.element_to_be_clickable(name))
    name.send_keys("Vinith Mungaleri")
    card_no.send_keys("1234123412341234")
    expiry_month.select_by_value("8")
    expiry_year.select_by_value("2080")
    print("Entered Card Details")

    actions.move_to_element(driver.find_element(By.ID, 'submitButton')).perform()
    wait.until(ec.element_to_be_clickable((By.ID, 'submitButton'))).click()
    print("Submitted New Card")


def test_add_to_cart(setup):
    driver = setup
    wait = WebDriverWait(driver, 10)
    add_btn_path = "//button//span[text()='Add to Basket']"
    wait.until(ec.visibility_of_all_elements_located((By.XPATH, add_btn_path)))
    add_cart_buttons = driver.find_elements(By.XPATH, add_btn_path)
    last_btn = add_cart_buttons[9]
    actions = ActionChains(driver)
    actions.move_to_element(last_btn).click().perform()
    cart_xpath = "//button[@aria-label='Show the shopping cart']//span[text()=' Your Basket']/following-sibling::span"
    actions.move_to_element(driver.find_element(By.XPATH, cart_xpath)).perform()
    cart_count = driver.find_element(By.XPATH, cart_xpath).text
    assert cart_count == "1"


def test_get_all_products(setup):
    driver = setup
    wait = WebDriverWait(driver, 10)

    item_name_path = "//div[@class='item-name']"
    item_price_path = "//div[@class='item-price']"
    prev_page_btn_path = "//button[@aria-label='Previous page']"
    next_page_btn_path = "//button[@aria-label='Next page']"

    prev_page_btn = driver.find_element(By.XPATH, prev_page_btn_path)
    next_page_btn = driver.find_element(By.XPATH, next_page_btn_path)

    product_details = {}
    while True:
        item_names = wait.until(ec.presence_of_all_elements_located((By.XPATH, item_name_path)))
        item_prices = wait.until(ec.presence_of_all_elements_located((By.XPATH, item_price_path)))
        for i in range(0, len(item_names)):
            product_details[item_names[i].text] = item_prices[i].text

        next_page_btn = driver.find_element(By.XPATH, next_page_btn_path)
        if next_page_btn.is_enabled():
            next_page_btn.click()
        else:
            break

    print("Total products found:", len(product_details))
    print(product_details)


def test_api_add_unique_card():
    api_url = "http://localhost:3000/api/Cards"
    new_card = {
        'cardNum': "1111111111112001",
        'expMonth': 9,
        'expYear': 2080,
        "fullName": "test_card"
    }

    existing_cards = get_cards(api_url)
    if existing_cards:
        if verify_new_card(existing_cards, new_card):
            post_card(api_url, new_card)
        else:
            print("Card Already Exists")
    else:
        print("No Existing cards found")
        post_card(api_url, new_card)


def verify_new_card(existing_cards, new_card):
    for existing_card in existing_cards:
        existing_card_name = existing_card['fullName']
        existing_card_no = existing_card['cardNum']
        existing_card_month = existing_card['expMonth']
        existing_card_year = existing_card['expYear']
        if existing_card_no[-4:-1] == new_card['cardNum'][-4:-1] and new_card['expMonth'] == existing_card_month and new_card['expYear'] == existing_card_year and existing_card_name == new_card['fullName']:
            return False
    return True


def get_cards(url):

    headers = {
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdGF0dXMiOiJzdWNjZXNzIiwiZGF0YSI6eyJpZCI6MjIsInVzZXJuYW1lIjoiIiwiZW1haWwiOiJ0ZXN0YWRtaW5AZ21haWwuY29tIiwicGFzc3dvcmQiOiIwZTc1MTcxNDFmYjUzZjIxZWU0MzliMzU1YjVhMWQwYSIsInJvbGUiOiJjdXN0b21lciIsImRlbHV4ZVRva2VuIjoiIiwibGFzdExvZ2luSXAiOiIwLjAuMC4wIiwicHJvZmlsZUltYWdlIjoiL2Fzc2V0cy9wdWJsaWMvaW1hZ2VzL3VwbG9hZHMvZGVmYXVsdC5zdmciLCJ0b3RwU2VjcmV0IjoiIiwiaXNBY3RpdmUiOnRydWUsImNyZWF0ZWRBdCI6IjIwMjQtMDYtMjAgMDk6NDc6MzguNDAyICswMDowMCIsInVwZGF0ZWRBdCI6IjIwMjQtMDYtMjAgMDk6NDc6MzguNDAyICswMDowMCIsImRlbGV0ZWRBdCI6bnVsbH0sImlhdCI6MTcxODg3Njg3MX0.v_ue5LKlLWN42mq9itza5d0J6xpt4IZFcFCTtOCiUXeLKqBkTqsVXoxsuU6dfgfC9Oy_zQtHkFFqljqCtjuC1rlYumQNUKcJMdPjcBxQtH3MdmIB0HoJdd2G1rlmVJgqFaoOPx03wc2i6GTmynBw37aIolc3kiTpIVNx38x-RDg'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json()["status"] == "success":
        existing_cards = response.json()["data"]
        return existing_cards
    else:
        print("Request to GET Failed with status code", str(response.status_code) + str(response.json()))
        return None


def post_card(url, card_json):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdGF0dXMiOiJzdWNjZXNzIiwiZGF0YSI6eyJpZCI6MjIsInVzZXJuYW1lIjoiIiwiZW1haWwiOiJ0ZXN0YWRtaW5AZ21haWwuY29tIiwicGFzc3dvcmQiOiIwZTc1MTcxNDFmYjUzZjIxZWU0MzliMzU1YjVhMWQwYSIsInJvbGUiOiJjdXN0b21lciIsImRlbHV4ZVRva2VuIjoiIiwibGFzdExvZ2luSXAiOiIwLjAuMC4wIiwicHJvZmlsZUltYWdlIjoiL2Fzc2V0cy9wdWJsaWMvaW1hZ2VzL3VwbG9hZHMvZGVmYXVsdC5zdmciLCJ0b3RwU2VjcmV0IjoiIiwiaXNBY3RpdmUiOnRydWUsImNyZWF0ZWRBdCI6IjIwMjQtMDYtMjAgMDk6NDc6MzguNDAyICswMDowMCIsInVwZGF0ZWRBdCI6IjIwMjQtMDYtMjAgMDk6NDc6MzguNDAyICswMDowMCIsImRlbGV0ZWRBdCI6bnVsbH0sImlhdCI6MTcxODg3Njg3MX0.v_ue5LKlLWN42mq9itza5d0J6xpt4IZFcFCTtOCiUXeLKqBkTqsVXoxsuU6dfgfC9Oy_zQtHkFFqljqCtjuC1rlYumQNUKcJMdPjcBxQtH3MdmIB0HoJdd2G1rlmVJgqFaoOPx03wc2i6GTmynBw37aIolc3kiTpIVNx38x-RDg',
    }

    response = requests.post(url, headers=headers, json=card_json)
    if response.status_code == 201 and response.json()["status"] == "success":
        print("New card added successfully:")
        print(response.json()["data"])
    else:
        print("Failed to add card with status code", response.status_code)
        print("Error:", response.json())