import re
import rsa
import json
import time
import base64
import random
import string
import requests
import datetime
from hashlib import sha1, md5
from Crypto.Cipher import AES
from authorization.byLogin import by_login
from authorization.ssoLogin import sso_login
from cryptography.hazmat.primitives import padding

passMap = {0: '未通过', 1: '通过'}
statusMap = {1: '未开始', 2: '上课中', 3: '已结课'}
checkInMap = {1: '通过', 2: '迟到', 3: '早退', 4: '缺勤'}

standardAppSign = {
    'date': '2022-05-13 22:32:53.191211',
    'sign': 'FE0050BB433D4504A78C827F3772ACD1'
}


def parse_kind(data, prefix, key):
    kinds = []
    while data.get(prefix + str(len(kinds) + 1)):
        kinds.append(data.get(prefix + str(len(kinds) + 1))[key])
    return '-'.join(kinds)


def front_serialize(data):
    return {} if data is None else {
        i['id']: {
            '课程名称': i['courseName'],
            '课程类别': parse_kind(i, 'courseKind', 'kindName'),
            '开课地点': i['coursePosition'],
            '授课教师': i['courseTeacher'],
            '授课学院': i['courseBelongCollege']['collegeName'],
            '上课时间': i['courseStartDate'] + ' - ' + i['courseEndDate'],
            '选课校区': '、'.join(i['courseCampusList']) if i['courseCampusList'] else None,
            '选课学院': '、'.join(i['courseCollegeList']) if i['courseCampusList'] else None,
            '选课年级': '、'.join(i['courseTermList']) if i['courseCampusList'] else None,
            '选课时间': i['courseSelectStartDate'] + ' - ' + i['courseSelectEndDate'],
            '退选截止': i['courseCancelEndDate'],
            '课程作业': '有作业' if i['courseHomework'] else '无作业',
            '选课人数': str(i['courseCurrentCount']) + ' / ' + str(i['courseMaxCount']),
            '已选课程': i['selected']
        } for i in data
    }


def back_serialize(data):
    return {} if data is None else {
        i['courseInfo']['id']: {
            '课程名称': i['courseInfo']['courseName'],
            '开课时间': i['courseInfo']['courseStartDate'] + ' 至 ' + i['courseInfo']['courseEndDate'],
            '开课地点': i['courseInfo']['coursePosition'],
            '授课教师': i['courseInfo']['courseTeacher'],
            '课程类别': parse_kind(i['courseInfo'], 'courseKind', 'kindName'),
            '课程作业': '有作业-' + ('已提交' if i['homework'] else '待提交') if i['courseInfo']['courseHomework'] else '无作业',
            '课程考勤': checkInMap[i['checkin']] if i['checkin'] in statusMap else '待录入',
            '课程成绩': i['score'] if i['score'] else '待评估',
            '课程考核': passMap[i['pass']] if i['pass'] in passMap else '待考核',
            '课程状态': statusMap.get(i['courseInfo']['status'])
        } for i in data
    }


def aes_encode(cipher, data):
    fix = padding.PKCS7(128).padder()
    data = fix.update(data) + fix.finalize()
    return cipher.encrypt(data)


def aes_decode(cipher, data):
    fix = padding.PKCS7(128).unpadder()
    data = cipher.decrypt(data)
    return fix.update(data) + fix.finalize()


def load_time(info):
    start, finish = info['选课时间'].split(' - ')
    start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    finish = datetime.datetime.strptime(finish, '%Y-%m-%d %H:%M:%S')
    return start, finish


class Selector:
    __try_query_time, __try_select_time, __try_unselect_time = 10, 1, 1

    """
    如果设置了 use_random_key，每次请求会使用随机的 AES 秘钥，隐蔽性更好
    如果没有设置 use_random_key，每次请求省去了轮秘钥生成的时间，性能更高
    """

    def __init__(self, use_random_key=False):
        cookies, self.__token = by_login(sso_login())
        request = requests.get('http://bykc.buaa.edu.cn/system/home', headers={
            'User-Agent': 'Y.J.Aickson'
        }, cookies=cookies)
        match = re.search('app\..+\.js', request.text)
        request = requests.get('http://bykc.buaa.edu.cn/' + match.group(), headers={
            'User-Agent': 'Y.J.Aickson'
        }, cookies=cookies)
        match = re.search('RSA_PUBLIC_KEY="(.+?)"', request.text)
        self.sign = md5(request.text.encode()).hexdigest().upper()
        key = ['-----BEGIN PUBLIC KEY-----', match.group(1), '-----END PUBLIC KEY-----']
        default = base64.b64decode('WW91clNvZnR3YXJlU2hpdA==')
        self.__publicKey = rsa.PublicKey.load_pkcs1_openssl_pem('\n'.join(key).encode())
        self.__default_aesKey = None if use_random_key else base64.b64encode(rsa.encrypt(default, self.__publicKey))
        self.__default_cipher = None if use_random_key else AES.new(default, AES.MODE_ECB)
        self.get_user_profile()
        self.query_news_list()

    def __get_encode_info(self):
        if self.__default_aesKey is None:
            key = ''.join(random.sample(string.ascii_letters + string.digits, 16)).encode()
            aes_key = base64.b64encode(rsa.encrypt(key, self.__publicKey))
            cipher = AES.new(key, AES.MODE_ECB)
            return aes_key, cipher
        return self.__default_aesKey, self.__default_cipher

    def __request(self, route, data=None):
        aes_key, cipher = self.__get_encode_info()
        if data is not None:
            data = json.dumps(data).encode()
            sha_sign = base64.b64encode(rsa.encrypt(sha1(data).hexdigest().encode(), self.__publicKey))
            request = requests.post('http://bykc.buaa.edu.cn/sscv/' + route, headers={
                'auth_token': self.__token,
                'User-Agent': 'Y.J.Aickson',
                'Content-Type': 'application/json',
                'ak': aes_key,
                'sk': sha_sign,
                'ts': str(round(time.time() * 1000))
            }, data=base64.b64encode(aes_encode(cipher, data)))
        else:
            request = requests.post('http://bykc.buaa.edu.cn/sscv/' + route, headers={
                'auth_token': self.__token,
                'User-Agent': 'Y.J.Aickson',
                'Content-Type': 'application/json',
                'ak': aes_key
            })
        text = aes_decode(cipher, base64.b64decode(request.text))
        match = re.search('({.+})', text.decode('utf8').strip())
        return json.loads(match.group(1))

    def __current_course_query(self, has_selected, has_unselected):
        if not has_selected and not has_unselected:
            return {}
        buffer = front_serialize(self.__request('queryStudentSemesterCourseByPage', data={
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

    def get_frontend_sign(self):
        return {
            'date': str(datetime.datetime.now()),
            'sign': self.sign
        }

    def get_user_profile(self):
        return self.__request('getUserProfile')['data']

    def query_news_list(self):
        return self.__request('queryNewsList', {})['data']

    def fore_course_query_old(self):
        result = None
        for _ in range(self.__try_select_time):
            response = front_serialize(self.__request('queryForeCourse')['data'])
            if result is None or len(result) < len(response):
                result = response
        return result

    def fore_course_query(self):
        buffer = front_serialize(self.__request('queryStudentSemesterCourseByPage', data={
            'pageNumber': 1,
            'pageSize': 20
        })['data']['content'])
        result = {}
        for i in buffer:
            if load_time(buffer[i])[0] > datetime.datetime.now():
                result[i] = buffer[i]
        return result

    def selectable_course_query_old(self):
        result = None
        for _ in range(self.__try_select_time):
            response = front_serialize(self.__request('querySelectableCourse')['data'])
            if result is None or len(result) < len(response):
                result = response
        return result

    def selectable_course_query(self):
        return self.__current_course_query(has_selected=False, has_unselected=True)

    def unselectable_course_query(self):
        return self.__current_course_query(has_selected=True, has_unselected=False)

    def current_chosen_course_query(self):
        return back_serialize(self.__request('queryChosenCourse')['data'].get('courseList'))

    def history_chosen_course_query(self):
        return back_serialize(self.__request('queryChosenCourse')['data'].get('historyCourseList'))

    def query_info(self, cid):
        for _ in range(self.__try_select_time):
            response = front_serialize(self.__request('queryForeCourse')['data'])
            if cid in response.keys():
                return response[cid]
            response = front_serialize(self.__request('querySelectableCourse')['data'])
            if cid in response.keys():
                return response[cid]
        return None

    def suggest_time(self, cid):
        info = self.query_info(cid)
        if info is not None:
            start = load_time(info)[0]
            return {
                'login': start - datetime.timedelta(minutes=1, seconds=15),
                'start': start - datetime.timedelta(seconds=30),
                'finish': start + datetime.timedelta(minutes=4, seconds=30)
            }
        return None

    def select(self, cid):
        for _ in range(self.__try_select_time):
            content = self.__request('choseCourse', data={'courseId': cid})
            print(json.dumps(content, indent=4, ensure_ascii=False))
            if '成功' in content['errmsg']:
                return True
            if '已报名' in content['errmsg']:
                return True
        return False

    def unselect(self, cid):
        for _ in range(self.__try_unselect_time):
            content = self.__request('delChosenCourse', data={'id': cid})
            print(json.dumps(content, indent=4, ensure_ascii=False))
            if '成功' in content['errmsg']:
                return True
            if '未找到' in content['errmsg']:
                return True
        return False
