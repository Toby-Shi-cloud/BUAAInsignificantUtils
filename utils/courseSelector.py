import re
import requests
from authorization.jwLogin import jw_login
from authorization.ssoLogin import sso_login

typeMap = {
    '一般专业': ('xslbxk', 'ZYL', 'J', 'xslbxk'), '核心专业': ('xslbxk', 'ZYL', 'I', 'xslbxk'),
    '一般通识': ('xsxk', 'TSL', 'D', 'qxrx'), '核心通识': ('xsxk', 'TSL', 'D', 'tsk')
}


class Selector:
    """
    year: 学年，字面意思，例如 [ 2021-2022学年 ] 写作 [ '2021-2022' ]
    term: 学期，字面意思，例如 [ 秋季学期 ] 或 [ 第一学期 ] 写作 [ '1' ]
    id: 课程编号，对应教务系统中的课程代码，形如 [ 'B2E333060' ]
    type: 课程类型，为 [ '一般专业' ] [ '核心专业' ] [ '一般通识' ] [ '核心通识' ] 中的一个
    teacher: 教师编号，当一门课程有多个老师开设时可以设置，默认值为 [ '001' ]
    """

    def __init__(self, year, term, c_id, c_type, teacher='001'):
        self.__cookies = jw_login(sso_login())
        self.__pageUrl, self.__pageXkm, pageKclb, pageXklb = typeMap[c_type]
        self.__tokenTemplate = {
            'kcdmpx': '', 'kcmcpx': '', 'rlpx': '', 'rwh': '', 'zy': '', 'qz': '',
            'pageXklb': pageXklb, 'pageXkmkdm': self.__pageXkm, 'pageKclb': pageKclb, 'pageKkxiaoqu': '',
            'pageKkyx': '', 'pageKcmc': '', 'pageYcctkc': '', 'pageXnxq': year + term
        }
        self.__selectTemplate = {
            'kcdmpx': '', 'kcmcpx': '', 'rlpx': '', 'rwh': '-'.join([year, term, c_id, teacher]), 'zy': '', 'qz': '',
            'pageXklb': pageXklb, 'pageXkmkdm': self.__pageXkm, 'pageKclb': pageKclb, 'pageKkxiaoqu': '',
            'pageKkyx': '', 'pageKcmc': '', 'pageYcctkc': '', 'pageXnxq': year + term
        }

    def __submit_token(self):
        url = 'http://jwxt.buaa.edu.cn:8080/ieas2.1/' + self.__pageUrl + '/queryXsxk?pageXkmkdm=' + self.__pageXkm
        request = requests.get(url, cookies=self.__cookies)
        match = re.search('value="(0\.\d+)"', request.text)
        self.__tokenTemplate['token'] = '' if match is None else match.group(1)
        url = 'http://jwxt.buaa.edu.cn:8080/ieas2.1/' + self.__pageUrl + '/queryXsxkList'
        request = requests.post(url=url, data=self.__tokenTemplate, cookies=self.__cookies)
        match = re.search('value="(0\.\d+)"', request.text)
        token = '' if match is None else match.group(1)
        return token

    def select(self):
        self.__selectTemplate['token'] = self.__submit_token()
        url = 'http://jwxt.buaa.edu.cn:8080/ieas2.1/' + self.__pageUrl + '/saveXsxk'
        request = requests.post(url=url, data=self.__selectTemplate, cookies=self.__cookies)
        match = re.search('alert\(\'(.+)\'\);', request.text)
        print('选课异常' if match is None else match.group(1))
