import re
import json
import base64
import requests
import datetime
from authorization.by_login import by_login
from authorization.sso_login import sso_login
from utils.by_parser import fore_parse, back_parse
from utils.by_crypto import md5_sign, sha1_sign, \
    create_rsa_key, rsa_encode, create_aes_key, aes_encode, aes_decode

default_aes_key = base64.b64decode('WW91clNvZnR3YXJlU2hpdA==')

standard_app_sign = {
    'date': '2022-09-02 22:18:43.537523',
    'sign': '6ad7e606dd032aeb277c9aed1308dc2d'
}

user_agent = {
    'fast': 'Y.J.Aickson',
    'full': ' '.join([
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'AppleWebKit/537.36 (KHTML, like Gecko)',
        'Chrome/98.0.4758.139', 'Safari/537.36'
    ])
}


def load_time(info):
    start, finish = info['选课时间'].split(' - ')
    start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    finish = datetime.datetime.strptime(finish, '%Y-%m-%d %H:%M:%S')
    return start, finish


class Selector:

    """
    如果设置了 fast_mode，将尽可能优化性能，如：
        不发送非必要的请求以节省时间
        使用更短的 User Agent 以减少请求长度
        使用固定的 AES 秘钥以节省轮秘钥生成时间
    """

    __try_query_times, __try_select_times, __try_unselect_times = 10, 1, 1

    def __init__(self, fast_mode=True):
        cookies, self.__token = by_login(sso_login())
        self.__user_agent = user_agent['fast' if fast_mode else 'full']
        request = requests.get('https://bykc.buaa.edu.cn/system/home', headers={
            'User-Agent': self.__user_agent
        }, cookies=cookies)
        match = re.search('app\\..+\\.js', request.text)
        request = requests.get('https://bykc.buaa.edu.cn/' + match.group(), headers={
            'User-Agent': self.__user_agent
        }, cookies=cookies)
        self.__sign = md5_sign(request.text.encode())
        self.__public_key = create_rsa_key(request.text)
        self.__default_aes_key, self.__default_cipher = (None, None) \
            if not fast_mode else create_aes_key(self.__public_key, assign=default_aes_key)
        if not fast_mode:
            self.get_user_profile()
            self.query_news_list()

    def __request(self, route, data=None):
        if self.__default_aes_key is None:
            aes_key, cipher = create_aes_key(self.__public_key)
            data = {} if data is None else data
        else:
            aes_key, cipher = self.__default_aes_key, self.__default_cipher
        common_headers = {
            'authtoken': self.__token,
            'User-Agent': self.__user_agent,
            'Content-Type': 'application/json',
            'ak': aes_key
        }
        if data is None:
            request = requests.post('https://bykc.buaa.edu.cn/sscv/' + route, headers=common_headers)
        else:
            data = json.dumps(data).encode()
            request = requests.post('https://bykc.buaa.edu.cn/sscv/' + route, headers={
                'sk': rsa_encode(self.__public_key, sha1_sign(data).encode()),
                'ts': str(round(datetime.datetime.now().timestamp() * 1000)),
                **common_headers
            }, data=base64.b64encode(aes_encode(cipher, data)))
        text = aes_decode(cipher, base64.b64decode(request.text))
        match = re.search('({.+})', text.decode('utf8').strip())
        return json.loads(match.group(1))

    def __current_course_query(self, has_selected, has_unselected):
        if not has_selected and not has_unselected:
            return {}
        buffer = fore_parse(self.__request('queryStudentSemesterCourseByPage', data={
            'pageNumber': 1,
            'pageSize': 20
        })['data']['content'])
        result = {}
        for i in buffer:
            start, finish = load_time(buffer[i])
            now = datetime.datetime.now()
            if start <= now < finish:
                if has_selected and buffer[i]['已选课程']:
                    result[i] = buffer[i]
                if has_unselected and not buffer[i]['已选课程']:
                    result[i] = buffer[i]
        return result

    def __query_course(self, cid):
        for _ in range(self.__try_select_times):
            response = fore_parse(self.__request('queryForeCourse')['data'])
            if cid in response.keys():
                return response[cid]
            response = fore_parse(self.__request('querySelectableCourse')['data'])
            if cid in response.keys():
                return response[cid]
        return None

    def get_frontend_sign(self):
        return {
            'date': str(datetime.datetime.now()),
            'sign': self.__sign
        }

    def get_user_profile(self):
        return self.__request('getUserProfile')['data']

    def query_news_list(self):
        return self.__request('queryNewsList', {})['data']

    def fore_course_query_old(self):
        result = None
        for _ in range(self.__try_select_times):
            response = fore_parse(self.__request('queryForeCourse')['data'])
            if result is None or len(result) < len(response):
                result = response
        return result

    def selectable_course_query_old(self):
        result = None
        for _ in range(self.__try_select_times):
            response = fore_parse(self.__request('querySelectableCourse')['data'])
            if result is None or len(result) < len(response):
                result = response
        return result

    def fore_course_query(self):
        buffer = fore_parse(self.__request('queryStudentSemesterCourseByPage', data={
            'pageNumber': 1,
            'pageSize': 20
        })['data']['content'])
        result = {}
        for i in buffer:
            if load_time(buffer[i])[0] > datetime.datetime.now():
                result[i] = buffer[i]
        return result

    def selectable_course_query(self):
        return self.__current_course_query(has_selected=False, has_unselected=True)

    def unselectable_course_query(self):
        return self.__current_course_query(has_selected=True, has_unselected=False)

    def current_chosen_course_query(self):
        return back_parse(self.__request('queryChosenCourse')['data'].get('courseList'))

    def history_chosen_course_query(self):
        return back_parse(self.__request('queryChosenCourse')['data'].get('historyCourseList'))

    def suggest_time(self, cid):
        info = self.__query_course(cid)
        if info is not None:
            start = load_time(info)[0]
            return {
                'login': start - datetime.timedelta(minutes=1, seconds=15),
                'start': start - datetime.timedelta(seconds=30),
                'finish': start + datetime.timedelta(minutes=4, seconds=30)
            }
        return None

    def select(self, cid):
        for _ in range(self.__try_select_times):
            content = self.__request('choseCourse', data={'courseId': cid})
            print(json.dumps(content, indent=4, ensure_ascii=False))
            if '成功' in content['errmsg']:
                return True
            if '已报名' in content['errmsg']:
                return True
        return False

    def unselect(self, cid):
        for _ in range(self.__try_unselect_times):
            content = self.__request('delChosenCourse', data={'id': cid})
            print(json.dumps(content, indent=4, ensure_ascii=False))
            if '成功' in content['errmsg']:
                return True
            if '未找到' in content['errmsg']:
                return True
        return False
