import json

import requests
from fake_useragent import UserAgent

import config

login_url = "https://lkk.mosobleirc.ru/api/tenants-registration/v2/login"
main_url = "https://lkk.mosobleirc.ru/api/api/clients/personal-accounts/summary"
payment_service_url = "https://lkk.mosobleirc.ru/api/api/clients/payments/utilities/rbs"

user = UserAgent().random

login = config.mosobleirc_login
password = config.mosobleirc_password

header = {
    "user-agent": user
}

login_data = {
    "loginMethod": "PERSONAL_OFFICE",
    "phone": login,
    "password": password,
}

payment_form = {
    "configurationItemId": 89081,
    "emailForReceipt": "ussread@ya.ru",
    "platform": "PERSONAL_OFFICE",
}

mosobleirc_check_logs = False


def get_token(logger, session):
    try:
        result = session.post(login_url, json=login_data, headers=header, timeout=10)
        post_data = json.loads(result.text)
        token = post_data["token"]
        logger.success("Got token " + str(result.status_code))
        return token
    except requests.exceptions.RequestException as exc:
        global mosobleirc_check_logs
        if not mosobleirc_check_logs:
            mosobleirc_check_logs = True
        logger.error(exc)


def get_cost(logger, session):
    try:
        header["x-auth-tenant-token"] = get_token(logger, session)
        url_res = session.get(main_url, headers=header, timeout=10)
        get_data = json.loads(url_res.text)
        if len(get_data) != 0:
            cost = float(get_data[0]["sum"] * -1)
            payment_form["sumRublesDotKopeks"] = cost
            logger.success(f"Got cost {cost}. Code {str(url_res.status_code)}")
            return cost
        else:
            logger.success("Got cost " + str(url_res.status_code))
            return 0
    except requests.exceptions.RequestException as exc:
        global mosobleirc_check_logs
        if not mosobleirc_check_logs:
            mosobleirc_check_logs = True
        logger.error(exc)


def get_payment_url(logger, session):
    try:
        url_res = session.post(payment_service_url, json=payment_form, headers=header, timeout=10)
        get_data = json.loads(url_res.text)
        if "formUrl" in get_data:
            payment_url = get_data["formUrl"]
            logger.success(f"Got payment url {str(url_res.status_code)}")
            return payment_url
    except requests.exceptions.RequestException as exc:
        global mosobleirc_check_logs
        if not mosobleirc_check_logs:
            mosobleirc_check_logs = True
        logger.error(exc)


def run(logger):
    logger.info("MosOblEIRC parsing started")
    global mosobleirc_check_logs
    mosobleirc_check_logs = False
    session = requests.Session()

    cost = get_cost(logger, session)
    if cost != 0:
        payment_url = get_payment_url(logger, session)
        return cost, payment_url
    else:
        payment_link = ""
        return cost, payment_link
