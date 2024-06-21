import time

from selenium import webdriver
import pytest
from selenium.webdriver.chrome.options import Options
import json
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import requests


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
    options.add_argument('--disable-notifications')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    driver.get(base_url)
    print("Entered into site:", base_url)
    dismiss_container_btn = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'close-dialog')]")))
    dismiss_container_btn.click()

    accept_cookies = driver.find_element(By.XPATH, "//a[text()='Me want it!']")
    accept_cookies.click()

    nav_account = driver.find_element(By.ID, "navbarAccount")
    nav_account.click()
    nav_login_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarLoginButton")))
    nav_login_btn.click()

    print("Redirecting to Login Page")
    assert driver.current_url == login_url
    assert driver.find_element(By.XPATH, "//h1[text() = 'Login']").text == 'Login'
    print("Entering Login Credentials")
    login_email = driver.find_element(By.ID, 'email')
    login_email.send_keys(login_email_value)
    login_pwd = driver.find_element(By.ID, 'password')
    login_pwd.send_keys(login_pwd_value)
    login_btn = wait.until(EC.element_to_be_clickable((By.ID, 'loginButton')))
    login_btn.click()
    nav_account = wait.until(EC.presence_of_element_located((By.ID, 'navbarAccount')))
    nav_account.click()

    logout_btn = wait.until(EC.visibility_of_element_located((By.ID, 'navbarLogoutButton')))
    print("Logged In...")
    assert logout_btn.is_displayed()
    yield driver
    driver.quit()


def test_add_card_details(setup):
    driver = setup
    wait = WebDriverWait(driver, 10)

    driver.refresh()  # To handle stale element exception
    wait.until(EC.element_to_be_clickable((By.ID, 'navbarAccount')))
    actions = ActionChains(driver)  # To handle Element click interception exception
    nav_account = driver.find_element(By.ID, "navbarAccount")
    actions.move_to_element(nav_account).click().perform()
    wait.until(
        EC.visibility_of_element_located((By.XPATH, "//button[@aria-label='Show Orders and Payment Menu']"))).click()
    wait.until(
        EC.visibility_of_element_located(
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
    wait.until(EC.element_to_be_clickable(name))
    name.send_keys("Vinith Mungaleri")
    card_no.send_keys("1234123412341234")
    expiry_month.select_by_value("8")
    card_expiry_dropdown[1].click()
    card_expiry_dropdown[1].send_keys(Keys.DOWN)
    card_expiry_dropdown[1].click()

    print("Entered Card Details")
    wait.until(EC.element_to_be_clickable((By.ID, 'submitButton'))).click()
    print("Submitted New Card")


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
