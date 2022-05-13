import requests


def by_login(sso_cookies):
    session = requests.session()
    session.headers.update({'User-Agent': 'Y.J.Aickson'})
    request = session.get('http://bykc.buaa.edu.cn/sscv/casLogin', cookies=sso_cookies)
    sso_cookies = requests.utils.dict_from_cookiejar(session.cookies)
    token = request.url.split('=')
    token = token[len(token) - 1]
    return sso_cookies, token
