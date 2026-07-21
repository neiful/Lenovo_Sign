import os
import base64
import logging
import random
import re
import time
import requests


USER_AGENT = [
    "Mozilla/5.0 (Linux; U; Android 11; zh-cn; PDYM20 Build/RP1A.200720.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.80 Mobile Safari/537.36 HeyTapBrowser/40.7.24.9",

    "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36"
]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__).info



LOGIN_TICKET = "5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3"



def login(username, password):

    session = requests.Session()


    session.headers.update({

        "user-agent":
            random.choice(USER_AGENT),

        "Content-Type":
            "application/x-www-form-urlencoded; charset=UTF-8"

    })


    try:

        # 初始化

        session.get(
            "https://reg.lenovo.com.cn/auth/rebuildleid",
            timeout=15
        )


        session.get(
            "https://reg.lenovo.com.cn/auth/v1/login?ticket="
            + LOGIN_TICKET
            + "&ru=https%3A%2F%2Fmclub.lenovo.com.cn%2F",
            timeout=15
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

            "deviceId":
            "BIT%2F8ZTwWmvKpMsz3bQspIZRY9o9hK1Ce3zKIt5js7WSUgGQNnwvYmjcRjVHvJbQ00fe3T2wxgjZAVSdOYl8rrQ%3D%3D",

            "websiteCode": "10000001",

            "websiteName":
            "%25E5%2595%2586%25E5%259F%258E%25E7%25AB%2599",

            "forwardPageUrl":
            "https%3A%2F%2Fmclub.lenovo.com.cn%2F"

        }


        response = session.post(

            "https://reg.lenovo.com.cn/auth/v2/doLogin",

            data=data,

            timeout=15

        )


        result=response.json()



        if result.get("ret") != "0":

            logger(
                "登录失败：" + str(result.get("msg"))
            )

            return None



        logger(
            "登录成功"
        )



        # 建立mclub session

        session.get(

            "https://mclub.lenovo.com.cn/",

            headers={

                "User-Agent":
                    random.choice(USER_AGENT),

                "Referer":
                    "https://reg.lenovo.com.cn/"

            },

            timeout=15

        )


        return session



    except Exception as e:

        logger(
            "登录异常：" + str(e)
        )

        return None





def get_token(session):


    headers={

        "Host":
            "mclub.lenovo.com.cn",

        "User-Agent":
            random.choice(USER_AGENT),

        "Referer":
            "https://mclub.lenovo.com.cn/",

        "Accept":
            "text/html,application/xhtml+xml"

    }


    r=session.get(

        "https://mclub.lenovo.com.cn/signlist/",

        headers=headers,

        timeout=15

    )


    token=re.findall(

        r'token\s*=\s*"([^"]+)"',

        r.text

    )


    if token:

        return token[0]


    return None





def sign(session):


    for i in range(3):


        token=get_token(session)


        if token:

            break


        logger(
            "获取签到token失败，重新建立session..."
        )


        time.sleep(2)



    if not token:

        logger(
            "签到失败：无法获取token"
        )

        return



    headers={


        "Host":
            "mclub.lenovo.com.cn",


        "pragma":
            "no-cache",


        "cache-control":
            "no-cache",


        "accept":
            "application/json, text/javascript, */*; q=0.01",


        "origin":
            "https://mclub.lenovo.com.cn",


        "x-requested-with":
            "XMLHttpRequest",


        "user-agent":
            random.choice(USER_AGENT)
            +
            "/lenovoofficialapp/16554342219868859_10128085590/newversion/versioncode-1000080/",


        "content-type":
            "application/x-www-form-urlencoded; charset=UTF-8",


        "referer":
            "https://mclub.lenovo.com.cn/signlist?pmf_group=in-push&pmf_medium=app&pmf_source=Z00025783T000",


        "accept-language":
            "zh-CN,en-US;q=0.8"

    }


    result=session.post(

        "https://mclub.lenovo.com.cn/signadd",

        headers=headers,

        data={

            "_token":token,

            "memberSource":"1"

        },

        timeout=15

    )



    try:

        data=result.json()


        if data.get("success"):

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



    try:


        info=session.get(

            "https://mclub.lenovo.com.cn/signuserinfo",

            timeout=15

        ).json()



        logger(
            "乐豆：" + str(info.get("ledou"))
        )


        logger(
            "延保：" + str(info.get("serviceAmount")) + "天"
        )



        cal=session.get(

            "https://mclub.lenovo.com.cn/getsignincal",

            timeout=15

        ).json()



        days=cal.get(
            "signinCal",
            {}
        ).get(
            "continueCount"
        )


        logger(
            "连续签到：" + str(days) + "天"
        )


    except Exception as e:

        logger(
            "获取用户信息失败：" + str(e)
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


        session=login(
            username,
            password
        )


        if session:

            sign(session)

            session.close()

            return



        logger(
            f"第{i+1}次登录失败"
        )


        time.sleep(5)



    logger(
        "全部尝试失败"
    )





if __name__=="__main__":

    main()import os
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
