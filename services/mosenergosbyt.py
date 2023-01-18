import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import config

login = config.mosenergosbyt_login
password = config.mosenergosbyt_password

mosenergosbyt_check_logs = False


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
    driver.get("https://my.mosenergosbyt.ru/auth")
    time.sleep(3)

    try:
        logged_in = driver.find_element(By.XPATH,
                                        "//*[@id=\"id22012\"]/div/div[1]/div/div[2]/div/div/p[1]").get_attribute(
            "innerHTML") \
                    + " " + driver.find_element(By.XPATH,
                                                "//*[@id=\"id22012\"]/div/div[1]/div/div[2]/div/div/p[2]").get_attribute(
            "innerHTML")
        logger.success("Already logged in as " + logged_in)
    except:
        try:
            time.sleep(3)

            uname = driver.find_element("name", "login")
            uname.send_keys(login)

            pword = driver.find_element("name", "password")
            pword.send_keys(password)

            driver.find_element("name", "remember").click()
            driver.find_element(By.XPATH, "//*[@id=\"root\"]/div/div[1]/div[2]/div/div[2]/div/form/div/button[1]/span[1]").click()

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
            global mosenergosbyt_check_logs
            if not mosenergosbyt_check_logs:
                mosenergosbyt_check_logs = True


def get_cost(driver, logger):
    try:
        get_epd_url = "https://my.mosenergosbyt.ru/"
        driver.get(get_epd_url)
        time.sleep(3)
        cost = float(driver.find_element(By.XPATH,
                                         "//*[@id=\"authPage\"]/div[1]/div[1]/div/div[2]/div/div[1]/div/div[1]/div/div/div/button[1]/span/p/span/span").text.replace(
            ",", "."))
        logger.success("Got cost")
        return cost
    except Exception as exc:
        logger.error(exc)
        global mosenergosbyt_check_logs
        if not mosenergosbyt_check_logs:
            mosenergosbyt_check_logs = True


def run(logger):
    logger.info("Mosenergosbyt parsing started")
    global mosenergosbyt_check_logs
    mosenergosbyt_check_logs = False
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

