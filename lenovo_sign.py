import os
import base64
import logging
import random
import re
import time
import requests


USER_AGENT = [
    "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro) AppleWebKit/537.36 Chrome/110 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; zh-cn; PDYM20 Build/RP1A.200720.011) AppleWebKit/537.36 Chrome/70 Mobile Safari/537.36"
]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__).info



def login(username,password):

    session=requests.Session()

    session.headers.update({

        "User-Agent":random.choice(USER_AGENT),

        "Content-Type":
        "application/x-www-form-urlencoded; charset=UTF-8"

    })


    try:

        session.get(
            "https://reg.lenovo.com.cn/auth/rebuildleid",
            timeout=15
        )


        session.get(
            "https://reg.lenovo.com.cn/auth/v1/login?ticket=5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3&ru=https%3A%2F%2Fmclub.lenovo.com.cn%2F",
            timeout=15
        )


        data = {

            "account":username,

            "password":
            base64.b64encode(
                password.encode()
            ).decode(),

            "ps":"1",

            "ticket":
            "5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3",

            "codeid":"",

            "code":"",

            "slide":"v2",

            "applicationPlatform":"2",

            "shopId":"1",

            "os":"web",

            "deviceId":
            "BIT%2F8ZTwWmvKpMsz3bQspIZRY9o9hK1Ce3zKIt5js7WSUgGQNnwvYmjcRjVHvJbQ00fe3T2wxgjZAVSdOYl8rrQ%3D%3D",

            "websiteCode":"10000001",

            "websiteName":
            "%25E5%2595%2586%25E5%259F%258E%25E7%25AB%2599",

            "forwardPageUrl":
            "https%3A%2F%2Fmclub.lenovo.com.cn%2F"

        }


        r=session.post(

            "https://reg.lenovo.com.cn/auth/v2/doLogin",

            data=data,

            timeout=15

        )


        result=r.json()


        if result.get("ret")!="0":

            logger(
                "登录失败: "+str(result)
            )

            return None



        logger(
            "联想账号登录成功"
        )


        # 给mclub建立session

        session.get(

            "https://mclub.lenovo.com.cn/",

            timeout=15

        )


        return session



    except Exception as e:

        logger(
            "登录异常:"+str(e)
        )

        return None





def sign(session):


    try:


        headers={

            "User-Agent":
            random.choice(USER_AGENT),

            "Accept":
            "text/html,application/xhtml+xml",

            "Referer":
            "https://mclub.lenovo.com.cn/"

        }


        page=session.get(

            "https://mclub.lenovo.com.cn/signlist/",

            headers=headers,

            timeout=15

        )


        token=re.findall(

            r'token\s*=\s*"([^"]+)"',

            page.text

        )


        if not token:

            logger(
                "获取签到token失败，可能登录状态失效"
            )

            return



        token=token[0]



        post_headers={


            "User-Agent":
            random.choice(USER_AGENT),


            "Accept":
            "application/json, text/javascript, */*; q=0.01",


            "Origin":
            "https://mclub.lenovo.com.cn",


            "Referer":
            "https://mclub.lenovo.com.cn/signlist/",


            "X-Requested-With":
            "XMLHttpRequest",


            "Content-Type":
            "application/x-www-form-urlencoded; charset=UTF-8"

        }



        result=session.post(

            "https://mclub.lenovo.com.cn/signadd",

            headers=post_headers,

            data={

                "_token":token,

                "memberSource":"1"

            },

            timeout=15

        )


        try:

            sign_result=result.json()


            if sign_result.get("success"):

                logger(
                    "今日签到成功"
                )

            else:

                logger(
                    "今日已经签到"
                )


        except:

            logger(
                "签到返回异常"
            )



        time.sleep(1)



        info=session.get(

            "https://mclub.lenovo.com.cn/signuserinfo",

            timeout=15

        ).json()



        if "res" in info:

            logger(
                "获取用户信息失败:"+str(info)
            )

            return



        logger(
            f"乐豆:{info.get('ledou')}"
        )


        logger(
            f"延保:{info.get('serviceAmount')}天"
        )



        calendar=session.get(

            "https://mclub.lenovo.com.cn/getsignincal",

            timeout=15

        ).json()



        try:

            days=calendar["signinCal"]["continueCount"]

            logger(
                f"连续签到:{days}天"
            )


        except:

            pass



    except Exception as e:

        logger(
            "签到异常:"+str(e)
        )





def main():


    username=os.environ.get("USERNAME")

    password=os.environ.get("PASSWORD")



    if not username or not password:

        logger(
            "没有设置USERNAME/PASSWORD"
        )

        return



    for i in range(3):


        session=login(
            username,
            password
        )


        if session:

            sign(session)

            return


        logger(
            f"第{i+1}次登录失败，等待重试"
        )


        time.sleep(5)



    logger(
        "全部登录失败"
    )




if __name__=="__main__":

    main()
