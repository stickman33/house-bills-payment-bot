import requests
from fake_useragent import UserAgent
from lxml import html

import config

login_url = 'https://adamant.housev.ru/lk/inner.php'
main_url = 'https://adamant.housev.ru/lk/'

user = UserAgent().random

login = config.adamant_login
password = config.adamant_password

header = {
    'user-agent': user
}

data = {
        'wlogin': login,
        'wpassw': password,
    }

adamant_check_logs = False


def get_tree(logger, session):
    try:
        session.post(login_url, data=data, headers=header)
        url_res = session.get(login_url, headers=header)
        tree = html.fromstring(url_res.content)
        logger.success("Got tree " + str(url_res.status_code))
        return tree
    except requests.exceptions.RequestException as exc:
        global adamant_check_logs
        if not adamant_check_logs:
            adamant_check_logs = True
        logger.error(exc)


def get_cost(logger, tree):
    get_cost_txt = tree.xpath('//form[@method="POST"]/table/tr[3]/td[2]/input/@value')
    try:
        for element in get_cost_txt:
            cost = float(element)
            logger.success("Parsed cost")
            return cost
    except Exception as exc:
        global adamant_check_logs
        if not adamant_check_logs:
            adamant_check_logs = True
        logger.error(exc)


def get_payment_url(logger, tree, session):
    try:
        get_payment_btn = tree.xpath('//form[@method="POST"]/@action')
        for element in get_payment_btn:
            payment_url = session.get(main_url + element, headers=header).url
            logger.success("Got payment url")
            return payment_url
    except requests.exceptions.RequestException as exc:
        global adamant_check_logs
        if not adamant_check_logs:
            adamant_check_logs = True
        logger.error(exc)


def run(logger):
    logger.info("Adamant parsing started")
    global adamant_check_logs
    adamant_check_logs = False
    session = requests.Session()

    tree = get_tree(logger, session)

    cost = get_cost(logger, tree)
    if cost != 0:
        payment_url = get_payment_url(logger, tree, session)
        return cost, payment_url
    else:
        payment_url = ""
        return cost, payment_url



