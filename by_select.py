import json
import time
import datetime
from utils.by_selector import Selector, standard_app_sign


def check_frontend_sign():
    sign = Selector().get_frontend_sign()
    if sign['sign'] == standard_app_sign['sign']:
        print('MD5 检测通过，API 在掌握中')
    else:
        print('Warning: MD5 检测未通过，API 可能已被修改')
        print('标准 MD5:')
        print(json.dumps(standard_app_sign, indent=4, ensure_ascii=False))
        print('当前 MD5:')
        print(json.dumps(sign, indent=4, ensure_ascii=False))


def get_user_profile():
    """查看个人信息"""
    print(json.dumps(Selector().get_user_profile(), indent=4, ensure_ascii=False))


def query_news_list():
    """查看通知公告"""
    print(json.dumps(Selector().query_news_list(), indent=4, ensure_ascii=False))


def fore_course_query():
    """查看课程预告（还不可选课）"""
    print(json.dumps(Selector().fore_course_query(), indent=4, ensure_ascii=False))


def selectable_course_query():
    """查看当前可选择的课程"""
    print(json.dumps(Selector().selectable_course_query(), indent=4, ensure_ascii=False))


def unselectable_course_query():
    """查看当前可退选的课程"""
    print(json.dumps(Selector().unselectable_course_query(), indent=4, ensure_ascii=False))


def current_chosen_course_query():
    """查看本学期已选的课程"""
    print(json.dumps(Selector().current_chosen_course_query(), indent=4, ensure_ascii=False))


def history_chosen_course_query():
    """查看本学期之前已选的课程"""
    print(json.dumps(Selector().history_chosen_course_query(), indent=4, ensure_ascii=False))


def select(cid):
    """提供一个 id，立即选择 id 对应的课程直到成功或被手动终止，适用于当前可选择的课程"""
    selector = Selector()
    while not selector.select(cid):
        time.sleep(1)
    print('选课结束')


def unselect(cid):
    """提供一个 id，立即退选 id 对应的课程直到成功或被手动终止，适用于当前可退选的课程"""
    selector = Selector()
    while not selector.unselect(cid):
        time.sleep(1)
    print('退课结束')


def super_select(cid):
    """提供一个 id，智能选择 id 对应的课程，可自动停止，适用于预告的课程"""
    while True:
        suggest = Selector().suggest_time(cid)
        if suggest is None:
            time.sleep(30)
            continue
        print('[update] at: ' + str(datetime.datetime.now()) + ', update to:')
        print('\tlogin: ' + str(suggest['login']))
        print('\tstart: ' + str(suggest['start']))
        print('\tfinish: ' + str(suggest['finish']))
        if datetime.datetime.now() + datetime.timedelta(hours=12) < suggest['login']:
            time.sleep(3 * 60 * 60)
            continue
        if datetime.datetime.now() + datetime.timedelta(hours=6) < suggest['login']:
            time.sleep(60 * 60)
            continue
        if datetime.datetime.now() + datetime.timedelta(hours=2) < suggest['login']:
            time.sleep(30 * 60)
            continue
        break
    # -------------------------------------------------------------
    while suggest is None:
        time.sleep(10)
        suggest = Selector().suggest_time(cid)
    print('[freeze] at: ' + str(datetime.datetime.now()) + ', freeze to:')
    print('\tlogin: ' + str(suggest['login']))
    print('\tstart: ' + str(suggest['start']))
    print('\tfinish: ' + str(suggest['finish']))
    # -------------------------------------------------------------
    counter = 0
    while datetime.datetime.now() < suggest['login']:
        if counter % 300 == 0:
            print('[waiting] at: ' + str(datetime.datetime.now()))
        counter += 1
        time.sleep(1)
    selector = Selector()
    print('[login] at: ' + str(datetime.datetime.now()) + ', waiting ...')
    # -------------------------------------------------------------
    counter = 0
    while datetime.datetime.now() <= suggest['finish']:
        if datetime.datetime.now() >= suggest['start']:
            if selector.select(cid):
                print('选课成功')
                return
        else:
            if counter % 10 == 0:
                print('[ready] at: ' + str(datetime.datetime.now()))
            counter += 1
        time.sleep(1)
    print('未在限定时间完成选课')


if __name__ == '__main__':
    check_frontend_sign()
    while True:
        command = input('>>> ').split(' ')
        name = command[0]
        try:
            func = {
                'check_frontend_sign': check_frontend_sign,
                'get_user_profile': get_user_profile,
                'query_news_list': query_news_list,
                'fore_course_query': fore_course_query,
                'selectable_course_query': selectable_course_query,
                'unselectable_course_query': unselectable_course_query,
                'current_chosen_course_query': current_chosen_course_query,
                'history_chosen_course_query': history_chosen_course_query,
                'unselect': unselect,
                'select': select,
                'super_select': super_select,
                'exit': exit,
            }[name]
            if len(command) == 2:
                func(int(command[1]))
            else:
                func()
        except KeyError:
            if name:
                print(f'Command Not Found: {name}')
        except IndexError:
            print(f'function {name} need argument, but none given')
