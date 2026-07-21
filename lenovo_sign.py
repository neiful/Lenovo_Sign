import os
import base64
import logging
import random
import re
import time

import requests

USER_AGENT = [
    "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; zh-cn; PDYM20 Build/RP1A.200720.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.80 Mobile Safari/537.36 HeyTapBrowser/40.7.24.9",
]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__).info


def create_session():
    s = requests.Session()

    s.headers.update({
        "User-Agent": random.choice(USER_AGENT),
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    })

    return s


def login(username, password):

    session = create_session()

    try:

        session.get(
            "https://reg.lenovo.com.cn/auth/rebuildleid",
            timeout=15
        )

        session.get(
            "https://reg.lenovo.com.cn/auth/v1/login?ticket=5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3&ru=https%3A%2F%2Fmclub.lenovo.com.cn%2F",
            timeout=15
        )

        data = (
            f"account={username}"
            f"&password={base64.b64encode(password.encode()).decode()}"
            "&ps=1"
            "&ticket=5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3"
            "&codeid="
            "&code="
            "&slide=v2"
            "&applicationPlatform=2"
            "&shopId=1"
            "&os=web"
            "&deviceId=test"
            "&websiteCode=10000001"
        )

        r = session.post(
            "https://reg.lenovo.com.cn/auth/v2/doLogin",
            data=data,
            timeout=15,
        )

        try:
            j = r.json()
            logger(f"登录返回：{j}")
        except:
            logger("登录返回不是JSON")
            logger(r.text[:500])
            return None

        logger(f"Cookie：{session.cookies.get_dict()}")

        home = session.get(
            "https://mclub.lenovo.com.cn/",
            timeout=15,
            allow_redirects=True,
        )

        logger(f"首页URL：{home.url}")

        if "login" in home.url.lower():
            logger("登录失败，仍然跳转到了登录页。")
            return None

        logger("登录成功。")

        return session

    except Exception as e:
        logger(f"登录异常：{e}")
        return None


def sign(session):

    try:

        r = session.get(
            "https://mclub.lenovo.com.cn/signlist/",
            timeout=15,
        )

        logger(f"signlist状态：{r.status_code}")
        logger(f"signlist最终URL：{r.url}")

        tokens = re.findall(
            r'token\s*=\s*"(.*?)"',
            r.text,
        )

        if not tokens:

            logger("没有找到token！")

            logger("页面前1000字符：")
            print(r.text[:1000])

            return

        token = tokens[0]

        logger(f"token={token}")

        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://mclub.lenovo.com.cn",
            "Referer": "https://mclub.lenovo.com.cn/signlist/",
            "User-Agent": random.choice(USER_AGENT),
        }

        resp = session.post(
            "https://mclub.lenovo.com.cn/signadd",
            data={
                "_token": token,
                "memberSource": 1,
            },
            headers=headers,
            timeout=15,
        )

        logger(resp.text)

        try:
            j = resp.json()

            if j.get("success"):
                logger("签到成功！")
            else:
                logger(f"签到返回：{j}")

        except:
            logger("签到返回不是JSON")
            logger(resp.text)

        try:

            info = session.get(
                "https://mclub.lenovo.com.cn/signuserinfo",
                timeout=15,
            ).json()

            logger(f"signuserinfo={info}")

        except Exception as e:
            logger(f"获取用户信息失败：{e}")

        try:

            cal = session.get(
                "https://mclub.lenovo.com.cn/getsignincal",
                timeout=15,
            ).json()

            logger(f"getsignincal={cal}")

        except Exception as e:
            logger(f"获取签到信息失败：{e}")

    except Exception as e:

        logger(f"签到异常：{e}")


def main():

    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    if not username or not password:
        logger("没有读取到环境变量 USERNAME / PASSWORD")
        return

    for i in range(3):

        logger(f"开始登录，第{i+1}次尝试...")

        session = login(username, password)

        if session:

            sign(session)

            session.close()

            return

        time.sleep(5)

    logger("连续三次登录失败。")


if __name__ == "__main__":
    main()
