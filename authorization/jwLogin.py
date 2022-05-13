import requests


def jw_login(sso_cookies):
    session = requests.session()
    session.get(url='http://jwxt.buaa.edu.cn:8080/ieas2.1/welcome', cookies=sso_cookies)
    sso_cookies = requests.utils.dict_from_cookiejar(session.cookies)
    sso_cookies = {'JSESSIONID': sso_cookies['JSESSIONID']}
    return sso_cookies
