import time
from datetime import datetime

from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import config

username = config.mosru_username
password = config.mosru_password


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
    driver.get("https://login.mos.ru/sps/login/methods/password?bo=%2Fsps%2Foauth%2Fae%3Fscope%3Dprofile%2Bopenid%2Bcontacts%2Busr_grps%26response_type%3Dcode%26redirect_uri%3Dhttps%3A%2F%2Fwww.mos.ru%2Fapi%2Facs%2Fv1%2Flogin%2Fsatisfy%26client_id%3Dmos.ru")
    time.sleep(3)

    try:
        logged_in = driver.find_element(By.XPATH, "//*[@id=\"mos-dropdown-user\"]/span[2]").get_attribute("innerHTML")
        logger.success("Already logged in as " + logged_in)
    except:
        try:
            uname = driver.find_element("id", "login")
            uname.send_keys(username)

            pword = driver.find_element("id", "password")
            pword.send_keys(password)

            driver.find_element("id", "bind").click()
            time.sleep(3)


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
            global check_logs
            if not check_logs:
                check_logs = True


def get_cost(driver, logger):
    previous_month = (datetime.now() - relativedelta(months=1)).strftime("%m.%Y")
    current_month = datetime.now().strftime("%m.%Y")

    get_epd_url = "https://www.mos.ru/pgu/ru/app/guis/062301/#step_1"
    driver.get(get_epd_url)

    time.sleep(3)

    driver.find_element(By.XPATH, "//*[@id=\"data\"]/div/div[1]/div[4]/div/div/div[1]/div").click()
    start_period = driver.find_element("id", "372_from")
    start_period.send_keys(previous_month)

    driver.find_element(By.XPATH, "//*[@id=\"data\"]/div/div[1]/div[4]/div/div/div[2]/div").click()
    end_period = driver.find_element("id", "372_to")
    end_period.send_keys(current_month)

    driver.find_element(By.XPATH, "//*[@id=\"data\"]/div/div[1]/div[3]/button").click()

    time.sleep(3)

    cost = float(driver.find_element(By.XPATH, "//*[@id=\"step_2\"]/fieldset/div[2]/div[1]/div/div/div[1]/div[1]/div[2]/b").text.split("  ")[0])
    logger.success("Got cost")
    # print(cost.split("  ")[0])
    return cost


def run(logger):
    logger.info("Mos.ru parsing started")
    driver = create_driver(logger)
    log_in(driver, logger)
    cost = get_cost(driver, logger)

    if cost != 0:
        # заглушка
        payment_url = "https://gwaith.ru/"
        driver.close()
        return cost, payment_url
    else:
        payment_link = ""
        driver.close()
        return cost, payment_link


