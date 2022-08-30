import base64
import json


def get_user_info():
    def __decode(text):
        return base64.b64decode(text.encode()).decode()

    try:
        """
        config.json：
            共计两个字段
            username 为用户名的 base64 编码结果
            password 为用户密码的 base64 编码结果
        """
        with open('./authorization/config.json', 'r') as file:
            content = json.loads(file.read())
            username, password = content.get('username'), content.get('password')
        return __decode(username), __decode(password)
    except IOError:
        print('error: config file failed to open')
        exit(0)
    except AttributeError:
        print('error: username or password not exist')
        exit(0)
    except json.decoder.JSONDecodeError:
        print('error: json file failed to parse')
        exit(0)
