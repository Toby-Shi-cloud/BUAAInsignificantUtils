import re
import json
import requests
from authorization.td_login import td_login
from authorization.sso_login import sso_login

if __name__ == '__main__':
    cookies = td_login(sso_login())
    request = requests.get('http://10.212.28.38/main.php?module=stu&title=stu_sun_score', cookies=cookies)
    reflect = {'1': '秋季学期', '2': '春季学期'}
    pattern = '<td>(\\d+-\\d+)</td>\\s*<td>(\\d+)</td>\\s*<td>(\\d+)</td>\\s*<td>-</td>'
    info = [{'学期': i[0] + ' ' + reflect[i[1]], 'TD次数': i[2]} for i in re.findall(pattern, request.text)]
    print(json.dumps(info, indent=4, ensure_ascii=False))
