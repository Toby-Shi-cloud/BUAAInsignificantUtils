import re
import requests
import datetime
from authorization.jw_login import jw_login
from authorization.sso_login import sso_login

refresh, type_map = 8, {
    '一般专业': ('xslbxk', 'ZYL', 'J', 'xslbxk'), '核心专业': ('xslbxk', 'ZYL', 'I', 'xslbxk'),
    '一般通识': ('xsxk', 'TSL', 'D', 'qxrx'), '核心通识': ('xsxk', 'TSL', 'D', 'tsk')
}


def get_year_term():
    now = datetime.datetime.now()
    if now.month >= 8:
        return str(now.year) + '-' + str(now.year + 1), '1'
    elif now.month <= 4:
        return str(now.year - 1) + '-' + str(now.year), '2'
    else:
        return str(now.year - 1) + '-' + str(now.year), '3'


class Selector:
    """
    id: 课程编号，对应教务系统中的课程代码，形如 [ 'B2E333060' ]
    type: 课程类型，为 [ '一般专业' ] [ '核心专业' ] [ '一般通识' ] [ '核心通识' ] 中的一个
    teacher: 教师编号，当一门课程有多个老师开设时可以设置，默认值为 [ '001' ]
    """

    def __init__(self, c_id, c_type, teacher='001'):
        year, term = get_year_term()
        self.__cookies = jw_login(sso_login())
        self.__time_stamp = datetime.datetime.now()
        self.__page_url, self.__page_xkm, page_kclb, page_xklb = type_map[c_type]
        self.__token_template = {
            'kcdmpx': '', 'kcmcpx': '', 'rlpx': '', 'rwh': '', 'zy': '', 'qz': '',
            'pageXklb': page_xklb, 'pageXkmkdm': self.__page_xkm, 'pageKclb': page_kclb, 'pageKkxiaoqu': '',
            'pageKkyx': '', 'pageKcmc': '', 'pageYcctkc': '', 'pageXnxq': year + term
        }
        self.__select_template = {
            'kcdmpx': '', 'kcmcpx': '', 'rlpx': '', 'rwh': '-'.join([year, term, c_id, teacher]), 'zy': '', 'qz': '',
            'pageXklb': page_xklb, 'pageXkmkdm': self.__page_xkm, 'pageKclb': page_kclb, 'pageKkxiaoqu': '',
            'pageKkyx': '', 'pageKcmc': '', 'pageYcctkc': '', 'pageXnxq': year + term
        }

    def __submit_token(self):
        url = 'http' + '://jwxt.buaa.edu.cn:8080/ieas2.1/' + \
              self.__page_url + '/queryXsxk?pageXkmkdm=' + self.__page_xkm
        request = requests.get(url, cookies=self.__cookies)
        match = re.search('value="(0\\.\\d+)"', request.text)
        self.__token_template['token'] = '' if match is None else match.group(1)
        url = 'http' + '://jwxt.buaa.edu.cn:8080/ieas2.1/' + self.__page_url + '/queryXsxkList'
        request = requests.post(url=url, data=self.__token_template, cookies=self.__cookies)
        match = re.search('value="(0\\.\\d+)"', request.text)
        token = '' if match is None else match.group(1)
        return token

    def select(self):
        if self.__time_stamp + datetime.timedelta(minutes=refresh) <= datetime.datetime.now():
            self.__cookies = jw_login(sso_login())
            self.__time_stamp = datetime.datetime.now()
        self.__select_template['token'] = self.__submit_token()
        url = 'http' + '://jwxt.buaa.edu.cn:8080/ieas2.1/' + self.__page_url + '/saveXsxk'
        request = requests.post(url=url, data=self.__select_template, cookies=self.__cookies)
        match = re.search('alert\\(\'(.+)\'\\);', request.text)
        print('选课异常' if match is None else match.group(1))
