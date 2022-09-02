pass_map = {0: '未通过', 1: '通过'}
status_map = {1: '未开始', 2: '上课中', 3: '已结课'}
check_in_map = {1: '通过', 2: '迟到', 3: '早退', 4: '缺勤'}


def kind_parse(data, prefix, key):
    kinds = []
    while data.get(prefix + str(len(kinds) + 1)):
        kinds.append(data.get(prefix + str(len(kinds) + 1))[key])
    return '-'.join(kinds)


def fore_parse(data):
    return {} if data is None else {
        i['id']: {
            '课程名称': i['courseName'],
            '课程类别': kind_parse(i, 'courseKind', 'kindName'),
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


def back_parse(data):
    return {} if data is None else {
        i['courseInfo']['id']: {
            '课程名称': i['courseInfo']['courseName'],
            '开课时间': i['courseInfo']['courseStartDate'] + ' 至 ' + i['courseInfo']['courseEndDate'],
            '开课地点': i['courseInfo']['coursePosition'],
            '授课教师': i['courseInfo']['courseTeacher'],
            '课程类别': kind_parse(i['courseInfo'], 'courseKind', 'kindName'),
            '课程作业': '有作业-' + ('已提交' if i['homework'] else '待提交') if i['courseInfo']['courseHomework'] else '无作业',
            '课程考勤': check_in_map[i['checkin']] if i['checkin'] in status_map else '待录入',
            '课程成绩': i['score'] if i['score'] else '待评估',
            '课程考核': pass_map[i['pass']] if i['pass'] in pass_map else '待考核',
            '课程状态': status_map.get(i['courseInfo']['status'])
        } for i in data
    }
