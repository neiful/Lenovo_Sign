import os
import base64
import logging
import random
import re
import time
import requests


USER_AGENT = [
    "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; zh-cn; PDYM20 Build/RP1A.200720.011) AppleWebKit/537.36 Chrome/70.0 Mobile Safari/537.36"
]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__).info


LOGIN_TICKET = (
    "5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3"
)


SERVICE_URL = (
    "https://mclub.lenovo.com.cn/"
)



def create_session():

    s = requests.Session()

    s.headers.update({

        "User-Agent": random.choice(USER_AGENT),

        "Accept-Language":
            "zh-CN,zh;q=0.9"

    })

    return s



def login(username,password):


    session=create_session()


    try:


        # 初始化登录环境

        session.get(
            "https://reg.lenovo.com.cn/auth/rebuildleid",
            timeout=15
        )


        login_page=session.get(

            "https://reg.lenovo.com.cn/auth/v1/login"
            "?ticket="+LOGIN_TICKET
            "&ru=https%3A%2F%2Fmclub.lenovo.com.cn%2F",

            timeout=15

        )


        logger(
            f"登录页状态:{login_page.status_code}"
        )


        # 提交账号密码

        data={

            "account":username,

            "password":
                base64.b64encode(
                    password.encode()
                ).decode(),

            "ps":"1",

            "ticket":LOGIN_TICKET,

            "codeid":"",

            "code":"",

            "slide":"v2",

            "applicationPlatform":"2",

            "shopId":"1",

            "os":"web",

            "deviceId":"",

            "websiteCode":"10000001",

            "websiteName":
                "%25E5%2595%2586%25E5%259F%258E%25E7%25AB%2599",

            "forwardPageUrl":
                "https%253A%252F%252Fmclub.lenovo.com.cn%252F"

        }



        r=session.post(

            "https://reg.lenovo.com.cn/auth/v2/doLogin",

            data=data,

            timeout=15

        )



        result=r.json()


        logger(
            f"登录结果:{result.get('ret')} {result.get('msg')}"
        )


        if result.get("ret")!="0":

            logger(result)

            return None



        tgt=result.get("tgt")


        if not tgt:

            logger("没有获取TGT")

            return None



        logger("获取TGT成功")



        #
        # CAS关键步骤
        # 用TGT换service ticket
        #


        cas_headers={

            "User-Agent":
                random.choice(USER_AGENT),

            "Content-Type":
                "application/x-www-form-urlencoded"

        }



        service_ticket=session.post(

            "https://reg.lenovo.com.cn/auth/v1/tickets/"
            + tgt,

            data={

                "service":
                    SERVICE_URL

            },

            headers=cas_headers,

            timeout=15

        )



        logger(
            f"service ticket返回:{service_ticket.text[:100]}"
        )



        if service_ticket.status_code!=200:

            logger("获取service ticket失败")

            return None



        ticket=service_ticket.text.strip()



        #
        # 携带ticket访问mclub
        # 建立业务session
        #


        callback=session.get(

            SERVICE_URL
            +
            "?ticket="
            +
            ticket,

            allow_redirects=True,

            timeout=15

        )



        logger(
            f"mclub最终地址:{callback.url}"
        )


        logger(
            f"最终Cookie:{session.cookies.get_dict()}"
        )


        time.sleep(1)



        # 验证业务登录

        check=session.get(

            "https://mclub.lenovo.com.cn/signuserinfo",

            timeout=15

        )


        logger(
            f"登录验证:{check.text}"
        )



        if "Must login" in check.text:

            logger(
                "mclub没有建立登录态"
            )

            return None



        logger(
            "完整CAS登录成功"
        )


        return session



    except Exception as e:


        logger(
            f"登录异常:{e}"
        )

        return None




def sign(session):


    try:


        page=session.get(

            "https://mclub.lenovo.com.cn/signlist/",

            timeout=15

        )


        token_list=re.findall(

            r'token\s*=\s*"(.*?)"',

            page.text

        )


        if not token_list:


            logger("获取token失败")

            logger(page.text[:500])

            return



        token=token_list[0]


        logger(
            "token获取成功"
        )


        headers={


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


        data={

            "_token":token,

            "memberSource":"1"

        }



        r=session.post(

            "https://mclub.lenovo.com.cn/signadd",

            data=data,

            headers=headers,

            timeout=15

        )


        logger(
            r.text
        )



        try:

            result=r.json()

            if result.get("success"):

                logger("签到成功")

            else:

                logger("今天可能已经签到")


        except:

            pass



        info=session.get(

            "https://mclub.lenovo.com.cn/signuserinfo",

            timeout=15

        ).json()


        logger(
            f"乐豆:{info.get('ledou')}"
        )


        logger(
            f"延保:{info.get('serviceAmount')}"
        )



    except Exception as e:

        logger(
            f"签到异常:{e}"
        )



def main():


    username=os.getenv("USERNAME")

    password=os.getenv("PASSWORD")


    for i in range(3):


        logger(
            f"尝试 {i+1}/3"
        )


        session=login(

            username,

            password

        )


        if session:

            sign(session)

            return



        time.sleep(5)



    logger(
        "全部失败"
    )



if __name__=="__main__":

    main()
