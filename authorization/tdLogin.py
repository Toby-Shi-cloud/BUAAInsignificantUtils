import requests


def td_login(sso_cookies):
    session = requests.session()
    session.get('http://10.212.28.38/index.php?schoolno=10006', cookies=sso_cookies)
    sso_cookies = requests.utils.dict_from_cookiejar(session.cookies)
    return sso_cookies
