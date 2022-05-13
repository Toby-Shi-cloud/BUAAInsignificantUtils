import requests
from bs4 import BeautifulSoup
from utils.userInfo import get_user_info


def sso_login():
    session = requests.session()
    request = session.get('https://sso.buaa.edu.cn/login')
    soup = BeautifulSoup(request.text, 'html.parser')
    execution = soup.find(name='input', attrs={'name': 'execution'}, recursive=True)['value']
    username, password = get_user_info()
    session.post(url='https://sso.buaa.edu.cn/login', data={
        'username': username,
        'password': password,
        'execution': execution,
        '_eventId': 'submit',
    }, allow_redirects=False)
    cookies = requests.utils.dict_from_cookiejar(session.cookies)
    if len(cookies) == 0:
        print('^^^ sso login failed ^^^')
        exit(0)
    return cookies
