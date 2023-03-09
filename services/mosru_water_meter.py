import time
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import config

username = config.mosru_username
password = config.mosru_password


# First time on deploy need to start with maximized mode to get User data, then enable headless
def create_driver(logger):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(r"user-data-dir=./User")
#     chrome_options.add_argument(r"user-data-dir=D:\my projects\bills-payment-bot\User")
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


def submit_meter_readings(driver, cold_value, hot_value):
    driver.get("https://www.mos.ru/services/pokazaniya-vodi-i-tepla/new/")
    time.sleep(3)

    def get_last_day_of_moth():
        current = datetime.now().date()
        next_month = current.replace(day=28) + timedelta(days=4)
        result = next_month - timedelta(days=next_month.day)
        return str(result)

    last_day = get_last_day_of_moth()
    cold_water_filed = driver.find_element(By.XPATH, f"//*[@id=\"indication[214280][{last_day}]\"]")
    cold_water_filed.send_keys(cold_value)

    hot_water_filed = driver.find_element(By.XPATH, f"//*[@id=\"indication[214281][{last_day}]\"]")
    hot_water_filed.send_keys(hot_value)

    driver.find_element(By.XPATH, "//*[@id=\"submit-meters\"]/button").click()
    time.sleep(3)


def run(logger, cold_value, hot_value):
    logger.info("Initiated Mos.ru water meter readings send")

    driver = create_driver(logger)
    log_in(driver, logger)
    submit_meter_readings(driver, cold_value, hot_value)

    logger.info("Mos.ru water meter readings sent")
    driver.close()


# run("675", "398")
