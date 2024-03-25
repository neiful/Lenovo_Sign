import os
import base64
import json
import logging
import random
import re
from sys import exit

import requests
import toml
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

USER_AGENT = [
    "Mozilla/5.0 (Linux; U; Android 11; zh-cn; PDYM20 Build/RP1A.200720.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.80 Mobile Safari/537.36 HeyTapBrowser/40.7.24.9",
    "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36"
]

def login(username, password):
    session.headers = {
    "user-agent": ua,
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    session.get(url="https://reg.lenovo.com.cn/auth/rebuildleid")
    session.get(
        url="https://reg.lenovo.com.cn/auth/v1/login?ticket=5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3&ru=https%3A%2F%2Fmclub.lenovo.com.cn%2F"
    )
    data = f"account={username}&password={base64.b64encode(str(password).encode()).decode()}\
        &ps=1&ticket=5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3&codeid=&code=&slide=v2&applicationPlatform=2&shopId=\
            1&os=web&deviceId=BIT%2F8ZTwWmvKpMsz3bQspIZRY9o9hK1Ce3zKIt5js7WSUgGQNnwvYmjcRjVHvJbQ00fe3T2wxgjZAVSd\
                OYl8rrQ%3D%3D&t=1655187183738&websiteCode=10000001&websiteName=%25E5%2595%2586%25E5%259F%258E%25E\
                    7%25AB%2599&forwardPageUrl=https%253A%252F%252Fmclub.lenovo.com.cn%252F"
    login_response = session.post(
        url="https://reg.lenovo.com.cn/auth/v2/doLogin", data=data
    )
    if login_response.json().get("ret") == "1":
        logger(f"{username}账号或密码错误")
        return None
    #ck_dict = dict_from_cookiejar(session.cookies)
    #config["cookies"][username] = f"{ck_dict}"
    #toml.dump(config, open(config_file, "w"))
    #session.cookies = cookiejar_from_dict(ck_dict)
    return session

def sign(session):
    res = session.get(url="https://mclub.lenovo.com.cn/signlist/")
    token = re.findall('token\s=\s"(.*?)"', res.text)[0]
    data = f"_token={token}&memberSource=1"
    headers = {
        "Host": "mclub.lenovo.com.cn",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "origin": "https://mclub.lenovo.com.cn",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": ua
        + "/lenovoofficialapp/16554342219868859_10128085590/newversion/versioncode-1000080/",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "referer": "https://mclub.lenovo.com.cn/signlist?pmf_group=in-push&pmf_medium=app&pmf_source=Z00025783T000",
        "accept-language": "zh-CN,en-US;q=0.8",
    }
    sign_response = session.post(
        "https://mclub.lenovo.com.cn/signadd", data=data, headers=headers
    )
    sign_days = (
        session.get(url="https://mclub.lenovo.com.cn/getsignincal")
        .json()
        .get("signinCal")
        .get("continueCount")
    )
    logger(f"连续登陆{continueCount}天。\n")
    sign_user_info = session.get("https://mclub.lenovo.com.cn/signuserinfo")
    serviceAmount = sign_user_info.json().get("serviceAmount")
    logger(f"延保有{serviceAmount}天。\n")
    ledou = sign_user_info.json().get("ledou")
    logger(f"乐豆有{ledou}个。\n")
    session.close()
    if sign_response.json().get("success"):
        logger(f"账号签到成功！n")
    else:
        logger(f"账号今天已经签到。\n")

def main():
    global logger, config_file, config, ua, username
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
    )
    logger = logging.getLogger(__name__).info
    config_file = r"config.toml"
    config = toml.load(config_file)
    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')
    if not (ua := config.get("browser").get("ua")):
        ua = random.choice(USER_AGENT)
        config["browser"]["ua"] = ua
    session = login(username, password)
    sign(session)
if __name__ == "__main__":
    main()

