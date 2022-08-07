#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import re
import base64
import toml
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def sign(username, password):
    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36 Edg/103.0.5060.42",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    session.get(url="https://reg.lenovo.com.cn/auth/rebuildleid")
    session.get(
        url="https://reg.lenovo.com.cn/auth/v1/login?ticket=5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3&ru=https%3A%2F%2Fmclub.lenovo.com.cn%2F"
    )
    data = f"account={username}&password={base64.b64encode(str(password).encode()).decode()}&ps=1&ticket=5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3&codeid=&code=&slide=v2&applicationPlatform=2&shopId=1&os=web&deviceId=BIT%2F8ZTwWmvKpMsz3bQspIZRY9o9hK1Ce3zKIt5js7WSUgGQNnwvYmjcRjVHvJbQ00fe3T2wxgjZAVSdOYl8rrQ%3D%3D&t=1655187183738&websiteCode=10000001&websiteName=%25E5%2595%2586%25E5%259F%258E%25E7%25AB%2599&forwardPageUrl=https%253A%252F%252Fmclub.lenovo.com.cn%252F"
    login_response = session.post(
        url="https://reg.lenovo.com.cn/auth/v2/doLogin", data=data
    )
    if login_response.json().get("ret") == "1":
        logger.error(f"{username}账号或密码错误")
        return
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
        "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; PCRT00 Build/LMY48Z; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36/lenovoofficialapp/16554342219868859_10128085590/newversion/versioncode-1000080/",
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
    sign_user_info = session.get("https://mclub.lenovo.com.cn/signuserinfo")
    serviceAmount = sign_user_info.json().get("serviceAmount")
    ledou = sign_user_info.json().get("ledou")
    if sign_response.json().get("success"):
        logger.info(
            f"账号{username}签到成功！总共签到天数为{sign_days}天, 共有乐豆{ledou}个, 共有延保{serviceAmount}天"
        )
    else:
        logger.error(
            f"账号{username}今天已经签到！总共签到天数为{sign_days}天, 共有乐豆{ledou}个, 共有延保{serviceAmount}天"
        )
    session.close()


def main_handler(event, context):
    account = toml.load("config.toml").get("ACCOUNT")
    if not account:
        return
    for username, password in account.items():
        sign(username, password)


if __name__ == "__main__":
    main_handler()
