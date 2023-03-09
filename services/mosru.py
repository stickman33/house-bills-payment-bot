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


# First time on deploy need to start with maximized mode to get User data, then enable headless
def create_driver(logger):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(r"user-data-dir=./User")
    # chrome_options.add_argument(r"user-data-dir=D:\my projects\bills-payment-bot\User")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--headless=new')
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
    time.sleep(5)
    # driver.implicitly_wait(5)

    try:
        logged_in = driver.find_element(By.XPATH, "//*[@id=\"mos-dropdown-user\"]/span[2]").get_attribute("innerHTML")
        driver.implicitly_wait(5)
        logger.success("Already logged in as " + logged_in)

    except:
        auth = driver.find_element(By.XPATH, "//*[@id=\"mos-header\"]/div[2]/div/header/div[3]/button")
        driver.implicitly_wait(5)
        # time.sleep(5)

        auth.click()

        while "login.mos.ru/sps/login/methods/password" not in driver.current_url:
            try:
                delete = driver.find_element("//*[@id=\"mus-selector\"]/section/div/div[1]/div/div/button")
                driver.implicitly_wait(3)
                # time.sleep(3)
                delete.click()
            except:
                login = driver.find_element(By.XPATH, "//*[@id=\"mus-selector\"]/section/div/div[2]/button")
                # time.sleep(3)
                driver.implicitly_wait(3)
                login.click()
            # time.sleep(3)
            # driver.implicitly_wait(3)

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
    try:
        cost = float(driver.find_element(By.XPATH, "//*[@id=\"step_2\"]/fieldset/div[4]/table/tbody/tr[1]/th[2]/span").text.replace(" ", "").replace(",", "."))
        logger.success("Got cost")
        return cost
    except (ValueError, NoSuchElementException):
        logger.success("Got cost")
        return 0


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
        time.sleep(3)

        try:
            cost = float(driver.find_element(By.XPATH, "//*[@id=\"app\"]/div/div[1]/div[2]/div/form/div/div[2]/div[2]/div/div[3]/div/p[1]/span").text)
            time.sleep(3)
            logger.success("Got cost")
            return cost
        except NoSuchElementException:
            logger.success("Got cost")
            return 0

    except Exception as exc:
        logger.error(exc)


def run(logger):
    logger.info("Mos.ru parsing started")
    driver = create_driver(logger)
    log_in(driver, logger)
    cost_dict = {"ЕПД": get_gkh_cost(driver, logger), "Электроэнергия": get_electricity_cost(driver, logger)}

    for cost in cost_dict.values():
        if cost != 0:
            payment_url = "https://pay.mos.ru/mospaynew/newportal/charges"
            driver.close()
            return cost_dict, payment_url
        else:
            payment_url = ""
            driver.close()
            return cost_dict, payment_url


