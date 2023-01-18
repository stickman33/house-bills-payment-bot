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


def create_driver(logger):
    chrome_options = webdriver.ChromeOptions()
# First time on deploy need to start with maximized mode to get User data, then enable headless
    # chrome_options.add_argument(r"user-data-dir=./User")
    chrome_options.add_argument(r"user-data-dir=D:\my projects\bills-payment-bot\User")
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--allow-profiles-outside-user-dir')
    chrome_options.add_argument('--enable-profile-shortcut-manager')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(30)
    logger.info("Created chrome driver")
    return driver


def log_in(logger, driver):
    driver.get("https://login.mos.ru/sps/login/methods/password?bo=%2Fsps%2Foauth%2Fae%3Fscope%3Dprofile%2Bopenid%2Bcontacts%2Busr_grps%26response_type%3Dcode%26redirect_uri%3Dhttps%3A%2F%2Fwww.mos.ru%2Fapi%2Facs%2Fv1%2Flogin%2Fsatisfy%26client_id%3Dmos.ru")
    time.sleep(3)

    try:
        logged_in = driver.find_element(By.XPATH, "//*[@id=\"mos-dropdown-user\"]/span[2]").get_attribute("innerHTML")
        logger.info("Already logged in as " + logged_in)
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
                logger.info("Login successful")
        except Exception as exc:
            logger.info(exc)


def submit_meter_readings(logger, driver, t1, t2, t3):
    get_url = "https://www.mos.ru/pgu2/counters"
    account = "71810-221-59"

    try:
        driver.get(get_url)
        time.sleep(3)

        account_number = driver.find_element(By.XPATH,
                                             "//*[@id=\"app\"]/div/div[1]/div[2]/div/form/div/div[1]/div[2]/div/div[2]/div/div/input")
        account_number.send_keys(account)

        driver.find_element(By.XPATH,
                            "//*[@id=\"app\"]/div/div[1]/div[2]/div/form/div/div[1]/div[2]/button").click()

        time.sleep(3)

        pok_t1 = driver.find_element(By.XPATH,
                                     "//*[@id=\"app\"]/div/div[1]/div[2]/div/form/div/div[2]/div[2]/div/div[3]/table/tbody/tr[1]/td[4]/div/input")
        pok_t1.send_keys(t1)

        pok_t2 = driver.find_element(By.XPATH,
                                     "//*[@id=\"app\"]/div/div[1]/div[2]/div/form/div/div[2]/div[2]/div/div[3]/table/tbody/tr[2]/td[4]/div/input")
        pok_t2.send_keys(t2)

        pok_t3 = driver.find_element(By.XPATH,
                                     "//*[@id=\"app\"]/div/div[1]/div[2]/div/form/div/div[2]/div[2]/div/div[3]/table/tbody/tr[3]/td[4]/div/input")
        pok_t3.send_keys(t3)

        time.sleep(3)
        # driver.find_element(By.XPATH, "//*[@id=\"app\"]/div/div[1]/div[2]/div/form/div/div[2]/div[2]/div/div[3]/button").click()

    except Exception as exc:
        logger.error(exc)


def run(logger, t1, t2, t3):
    logger.info("Initiated Mos.ru electricity meter readings send")

    driver = create_driver(logger)
    log_in(logger, driver)
    submit_meter_readings(logger, driver, t1, t2, t3)

    logger.info("Mos.ru electricity meter readings sent")
    driver.close()


# run("675", "398")
