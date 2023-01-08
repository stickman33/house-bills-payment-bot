import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import config

username = config.mgts_login
password = config.mgts_password

mgts_check_logs = False


def create_driver(logger):
    chrome_options = webdriver.ChromeOptions()
# First time on deploy need to start with maximized mode to get User data, then enable headless
    chrome_options.add_argument(r"user-data-dir=./User")
#     chrome_options.add_argument(r"user-data-dir=D:\my projects\bills-payment-bot\User")
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
    driver.get("https://auth.mgts.ru/login/b2c?feature=lk")
    time.sleep(3)

    try:
        logged_in = driver.find_element(By.CLASS_NAME, "account-info_title").get_attribute("innerHTML")\
            .replace(" ", "").replace("\n", "").replace("<div>", "").replace("</div>", " ").rstrip()
        logger.success("Already logged in as " + logged_in)
    except:
        try:
            uname = driver.find_element(By.NAME, "LoginForm[username]")
            uname.send_keys(username)
            driver.find_element(By.ID, "submit").click()
            time.sleep(1)

            pword = driver.find_element(By.NAME, "LoginForm[password]")
            pword.send_keys(password)

            driver.find_element(By.ID, "submit").click()
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
            global mgts_check_logs
            if not mgts_check_logs:
                mgts_check_logs = True


def get_cost(driver, logger):
    lk_url = "https://lk.mgts.ru/"
    driver.get(lk_url)
    time.sleep(3)

    cost = float(driver.find_element(By.XPATH, "/html/body/section/div[1]/div/div[2]/aside/div[1]/div[2]/div/span").text.replace(",", ".")) * -1
    logger.success("Got cost")
    return cost


def get_payment_url(driver, logger):
    lk_url = "https://lk.mgts.ru/"
    try:
        driver.get(lk_url)
    except Exception as exc:
        logger.error(exc)
    time.sleep(3)

    payment_url = driver.find_element(By.XPATH, "/html/body/section/div[1]/div/div[2]/aside/div[1]/a").get_attribute("href")
    logger.success("Got payment url")
    return payment_url


def run(logger):
    logger.info("Mgts parsing started")
    global mgts_check_logs
    mgts_check_logs = False

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

