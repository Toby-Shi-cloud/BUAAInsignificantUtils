import re
import json
import requests
from authorization.app_login import app_login

if __name__ == '__main__':
    result = {}
    request = requests.get(r'https://app.buaa.edu.cn/buaanet/wap/default/index', cookies=app_login())
    for i in re.findall(r'<div class="btn">.*?<br>\s*<span>.*?</span>\s*<span>.*?</span><br>', request.text):
        ans = re.search(r'<div class="btn">(.*?)<br>\s*<span>(.*?)</span>\s*<span>(.*?)</span><br>', i)
        name, use, tot = ans.group(1), ans.group(2), ans.group(3)
        use = use.split('：')
        tot = tot.split('：')
        result[name] = {
            use[0].strip(): use[1].strip(),
            tot[0].strip(): tot[1].strip()
        }
    for i in re.findall(r'<div class="btn">.*?<br>\s*<!--.*?-->\s*<!--.*?-->\s*<span>.*?</span>', request.text):
        ans = re.search(r'<div class="btn">(.*?)<br>\s*<!--.*?-->\s*<!--.*?-->\s*<span>(.*?)</span>', i)
        name, res = ans.group(1), ans.group(2)
        res = res.split('：')
        result[name] = {
            res[0].strip(): res[1].strip()
        }
    print(json.dumps(result, indent=4, ensure_ascii=False))
