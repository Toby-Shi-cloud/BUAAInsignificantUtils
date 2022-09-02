import requests
import requests.utils
from utils.userInfo import get_user_info


def app_login():
    session = requests.session()
    session.get('https://app.buaa.edu.cn/uc/wap/login')
    username, password = get_user_info()
    session.post(url='https://app.buaa.edu.cn/uc/wap/login/check', data={
        'username': username,
        'password': password
    })
    cookies = requests.utils.dict_from_cookiejar(session.cookies)
    if len(cookies) == 0:
        print('error: app login failed')
        exit(0)
    return cookies
