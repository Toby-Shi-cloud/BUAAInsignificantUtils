import re
import json
import requests
from authorization.app_login import app_login

if __name__ == '__main__':
    result = {}
    request = requests.get('https://app.buaa.edu.cn/buaanet/wap/default/index', cookies=app_login())
    for i in re.findall('<div class="btn">.*?<br>\\s*<span>.*?</span>\\s*<span>.*?</span><br>', request.text):
        ans = re.search('<div class="btn">(.*?)<br>\\s*<span>(.*?)</span>\\s*<span>(.*?)</span><br>', i)
        name, use, tot = ans.group(1), ans.group(2), ans.group(3)
        use = use.split('：')
        tot = tot.split('：')
        result[name] = {
            use[0].strip(): use[1].strip(),
            tot[0].strip(): tot[1].strip()
        }
    print(json.dumps(result, indent=4, ensure_ascii=False))
