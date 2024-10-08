import time
from datetime import datetime

from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import config

username = config.mosru_username
password = config.mosru_password
mosru_check_logs = False


def create_driver(logger):
    chrome_options = webdriver.ChromeOptions()
# First time on deploy need to start with maximized mode to get User data, then enable headless
#     chrome_options.add_argument(r"user-data-dir=./User")
    chrome_options.add_argument(r"user-data-dir=D:\my projects\bills-payment-bot\User")
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
    driver.get("https://www.mos.ru/")
    # time.sleep(3)
    driver.implicitly_wait(5)

    try:
        logged_in = driver.find_element(By.XPATH, "//*[@id=\"mos-dropdown-user\"]/span[2]").get_attribute("innerHTML")
        logger.success("Already logged in as " + logged_in)

    except:
        auth = driver.find_element(By.XPATH, "//*[@id=\"mos-header\"]/div[2]/div/header/div[3]/button")
        driver.implicitly_wait(5)
        auth.click()
        # time.sleep(3)

        while driver.current_url != "https://login.mos.ru/sps/login/methods/password":
            login = driver.find_element(By.XPATH, "//*[@id=\"mus-selector\"]/section/div/div[2]/button")
            login.click()
            # time.sleep(3)
            driver.implicitly_wait(3)


        try:
            uname = driver.find_element("id", "login")
            uname.send_keys(username)

            pword = driver.find_element("id", "password")
            pword.send_keys(password)

            driver.find_element("id", "bind").click()
            time.sleep(3)
            # driver.implicitly_wait(3)


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
            global mosru_check_logs
            if not mosru_check_logs:
                mosru_check_logs = True


# def get_gkh_cost(driver, logger):
#     get_gkh_url = "https://pay.mos.ru/mospaynew/newportal/charges"
#     try:
#         driver.get(get_gkh_url)
#         driver.implicitly_wait(30)
#         cost = float(driver.find_element(By.XPATH, "//*[@id=\"payment-list\"]/div/div[2]/accordion/mospay-charges-body-list/mospay-accordion-charges-list/mospay-charges-epd/accordion-group/div/div[1]/div/div/header/div[2]/span").text.replace("₽", "").replace(" ", "").replace(",", "."))
#         logger.success("Got cost")
#         return cost
#     except NoSuchElementException:
#         return 0


def get_gkh_cost(driver, logger):
    previous_month = (datetime.now() - relativedelta(months=1)).strftime("%m.%Y")
    current_month = datetime.now().strftime("%m.%Y")

    get_url = "https://www.mos.ru/pgu/ru/app/guis/062301/#step_1"
    driver.get(get_url)

    time.sleep(3)

    driver.find_element(By.XPATH, "//*[@id=\"data\"]/div/div[1]/div[4]/div/div/div[1]/div").click()
    start_period = driver.find_element("id", "372_from")
    start_period.send_keys(previous_month)

    driver.find_element(By.XPATH, "//*[@id=\"data\"]/div/div[1]/div[4]/div/div/div[2]/div").click()
    end_period = driver.find_element("id", "372_to")
    end_period.send_keys(current_month)

    driver.find_element(By.XPATH, "//*[@id=\"data\"]/div/div[1]/div[3]/button").click()

    time.sleep(3)
    cost = float(driver.find_element(By.XPATH, "//*[@id=\"step_2\"]/fieldset/div[4]/table/tbody/tr[1]/th[2]/span").text.replace(" ", "").replace(",", "."))
    logger.success("Got cost")
    return cost


def get_electricity_cost(driver, logger):
    get_url = "https://www.mos.ru/pgu2/counters"
    account = "71810-221-59"

    try:
        driver.get(get_url)
        time.sleep(3)

        account_number = driver.find_element(By.XPATH,
                                             "//*[@id=\"app\"]/div/div[1]/div[2]/div/form/div/div[1]/div[2]/div/div[2]/div/div/input")
        account_number.send_keys(account)

        driver.find_element(By.XPATH, "//*[@id=\"app\"]/div/div[1]/div[2]/div/form/div/div[1]/div[2]/button").click()
    except Exception as exc:
        logger.error(exc)


def run(logger):
    logger.info("Mos.ru parsing started")
    driver = create_driver(logger)
    log_in(driver, logger)
    cost = get_gkh_cost(driver, logger)

    if cost != 0:
        payment_url = "https://pay.mos.ru/mospaynew/newportal/charges"
        driver.close()
        return cost, payment_url
    else:
        payment_link = ""
        driver.close()
        return cost, payment_link


