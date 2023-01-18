import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import config

login = config.adamant_login
password = config.adamant_password
adamant_check_logs = False


def create_driver(logger):
    chrome_options = webdriver.ChromeOptions()
    # First time on deploy need to start with maximized mode to get User data, then enable headless
    chrome_options.add_argument(r"user-data-dir=./User")
    # chrome_options.add_argument(r"user-data-dir=D:\my projects\bills-payment-bot\User")
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument("start-maximized")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--allow-profiles-outside-user-dir')
    chrome_options.add_argument('--enable-profile-shortcut-manager')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(30)
    logger.success("Created chrome driver")
    return driver


def log_in(driver, logger):
    try:
        login_url = "https://adamant.housev.ru/lk/"
        driver.get(login_url)
        time.sleep(1)

        uname = driver.find_element(By.NAME, "wlogin")
        uname.send_keys(login)

        pword = driver.find_element(By.NAME, "wpassw")
        pword.send_keys(password)

        driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div/form/input").click()
        time.sleep(1)

        WebDriverWait(driver=driver, timeout=10).until(
            lambda x: x.execute_script("return document.readyState === 'complete'")
        )

        error_message = "Incorrect username or password."

        errors = driver.find_elements(By.CLASS_NAME, "flash-error")

        if any(error_message in e.text for e in errors):
            # print("Login failed")
            logger.error("Login failed")
        else:
            # print("Login successful")
            logger.success("Login successful")
    except Exception as exc:
        logger.error(exc)
        global adamant_check_logs
        if not adamant_check_logs:
            adamant_check_logs = True


def get_cost(driver, logger):
    lk_url = "https://adamant.housev.ru/lk/inner.php"
    driver.get(lk_url)
    time.sleep(1)

    cost = float(driver.find_element(By.XPATH, "/html/body/div/div/div[3]/div/form/table/tbody/tr[3]/td[2]/input")
                 .get_attribute("value"))
    logger.success("Got cost")
    return cost


def get_payment_url(driver, logger):

    lk_url = "https://adamant.housev.ru/lk/inner.php"

    try:
        driver.get(lk_url)
    except Exception as exc:
        logger.error(exc)

    driver.find_element(By.XPATH, "/html/body/div/div/div[3]/div/form/input").click()
    time.sleep(1)

    current_tab = driver.current_window_handle
    all_tabs = driver.window_handles

    for tab in all_tabs:
        if tab != current_tab:
            driver.switch_to.window(tab)

    payment_url = driver.current_url
    logger.success("Got payment url")
    return payment_url


def run(logger):
    logger.info("adamant parsing started")
    global adamant_check_logs
    adamant_check_logs = False

    driver = create_driver(logger)
    log_in(driver, logger)
    cost = get_cost(driver, logger)

    if cost != 0:
        payment_url = get_payment_url(driver, logger)
        driver.close()
        return cost, payment_url
    else:
        payment_link = ""
        driver.close()
        return cost, payment_link


