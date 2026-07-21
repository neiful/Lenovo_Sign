import os
import base64
import logging
import random
import re
import time
import requests
from urllib.parse import quote


USER_AGENT = [
    "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; zh-cn; PDYM20 Build/RP1A.200720.011) AppleWebKit/537.36 Chrome/70.0 Mobile Safari/537.36"
]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__).info


LOGIN_TICKET = "5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3"

SERVICE = "https://mclub.lenovo.com.cn/"


def create_session():

    session = requests.Session()

    session.headers.update({

        "User-Agent": random.choice(USER_AGENT),

        "Accept-Language":
            "zh-CN,zh;q=0.9"

    })

    return session



def login(username, password):

    session = create_session()

    try:

        # 初始化leid

        session.get(
            "https://reg.lenovo.com.cn/auth/rebuildleid",
            timeout=15
        )


        login_url = (
            "https://reg.lenovo.com.cn/auth/v1/login"
            "?ticket="
            + LOGIN_TICKET
            + "&ru="
            + quote(SERVICE)
        )


        r = session.get(
            login_url,
            timeout=15
        )


        logger(
            f"login page status:{r.status_code}"
        )


        data = {

            "account": username,

            "password":
                base64.b64encode(
                    password.encode()
                ).decode(),

            "ps": "1",

            "ticket": LOGIN_TICKET,

            "codeid": "",

            "code": "",

            "slide": "v2",

            "applicationPlatform": "2",

            "shopId": "1",

            "os": "web",

            "deviceId": "BIT%2F8ZTwWmvKpMsz3bQspIZRY9o9hK1Ce3zKIt5js7WSUgGQNnwvYmjcRjVHvJbQ00fe3T2wxgjZAVSdOYl8rrQ%3D%3D",

            "websiteCode": "10000001",

            "websiteName": "%25E5%2595%2586%25E5%259F%258E%25E7%25AB%2599",

            "forwardPageUrl":
                quote(SERVICE)

        }



        login_response = session.post(

            "https://reg.lenovo.com.cn/auth/v2/doLogin",

            data=data,

            timeout=15

        )


        result = login_response.json()


        logger(
            f"登录返回:{result}"
        )


        if result.get("ret") != "0":

            logger("账号密码登录失败")

            return None



        tgt = result.get("tgt")


        if not tgt:

            logger("没有TGT")

            return None


        logger("获取TGT成功")



        # CAS 获取service ticket


        ticket_response = session.post(

            "https://reg.lenovo.com.cn/auth/v1/tickets/" + tgt,

            data={

                "service": SERVICE

            },

            timeout=15

        )


        logger(
            f"service ticket:{ticket_response.text}"
        )


        if ticket_response.status_code != 200:

            return None



        service_ticket = ticket_response.text.strip()



        # 携带ticket访问mclub

        callback_url = (
            SERVICE
            + "?ticket="
            + service_ticket
        )


        callback = session.get(

            callback_url,

            allow_redirects=True,

            timeout=15

        )


        logger(
            f"mclub url:{callback.url}"
        )


        logger(
            f"Cookie:{session.cookies.get_dict()}"
        )



        time.sleep(1)



        # 验证mclub登录

        check = session.get(

            "https://mclub.lenovo.com.cn/signuserinfo",

            timeout=15

        )


        logger(
            f"登录验证:{check.text}"
        )


        if "Must login" in check.text:

            logger(
                "mclub没有建立session"
            )

            return None


        logger(
            "CAS登录成功"
        )


        return session



    except Exception as e:

        logger(
            f"登录异常:{e}"
        )

        return None




def sign(session):


    try:


        page = session.get(

            "https://mclub.lenovo.com.cn/signlist/",

            timeout=15

        )


        token_list = re.findall(

            r'token\s*=\s*"(.*?)"',

            page.text

        )


        if not token_list:

            logger("没有token")

            logger(page.text[:500])

            return



        token = token_list[0]


        logger(
            f"token:{token}"
        )


        headers = {


            "Host":
                "mclub.lenovo.com.cn",


            "Origin":
                "https://mclub.lenovo.com.cn",


            "Referer":
                "https://mclub.lenovo.com.cn/signlist/",


            "X-Requested-With":
                "XMLHttpRequest",


            "Content-Type":
                "application/x-www-form-urlencoded; charset=UTF-8",


            "User-Agent":
                random.choice(USER_AGENT)

        }



        data = {

            "_token": token,

            "memberSource": "1"

        }



        response = session.post(

            "https://mclub.lenovo.com.cn/signadd",

            headers=headers,

            data=data,

            timeout=15

        )


        logger(
            f"签到返回:{response.text}"
        )


        try:

            result=response.json()

            if result.get("success"):

                logger("签到成功")

            else:

                logger("签到失败或已经签到")


        except:

            pass



        info=session.get(

            "https://mclub.lenovo.com.cn/signuserinfo",

            timeout=15

        )


        logger(
            f"用户信息:{info.text}"
        )



    except Exception as e:

        logger(
            f"签到异常:{e}"
        )



def main():

    username=os.environ.get("USERNAME")

    password=os.environ.get("PASSWORD")


    if not username or not password:

        logger(
            "缺少账号密码"
        )

        return



    for i in range(3):

        logger(
            f"第{i+1}次尝试"
        )


        session=login(
            username,
            password
        )


        if session:

            sign(session)

            session.close()

            return


        time.sleep(5)



    logger(
        "全部失败"
    )



if __name__=="__main__":

    main()
