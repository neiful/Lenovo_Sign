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
            "text/html,application/xhtml+xml",

        # 避免拿到 CDN/浏览器缓存的旧页面，导致 token 是过期的
        "Cache-Control":
            "no-cache",

        "Pragma":
            "no-cache"

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



# 统一给"数据接口"用的 AJAX 请求头，模拟真实浏览器行为
# （之前 signuserinfo / getsignincal 完全没带这些头，是导致
#  间歇性拿不到 JSON / 字段为 None 的主要原因）
def ajax_headers():

    return {

        "Host":
            "mclub.lenovo.com.cn",

        "User-Agent":
            random.choice(USER_AGENT),

        "Referer":
            "https://mclub.lenovo.com.cn/signlist",

        "Accept":
            "application/json, text/javascript, */*; q=0.01",

        "X-Requested-With":
            "XMLHttpRequest",

        "Accept-Language":
            "zh-CN,en-US;q=0.8"

    }



def safe_json(response, label):
    """尝试解析 JSON，失败时打印原始返回内容（截断）方便排查，而不是直接抛异常吞掉信息。"""

    try:

        return response.json()

    except Exception as e:

        logger(
            label + " 解析JSON失败：" + str(e)
            + "｜HTTP状态码：" + str(response.status_code)
            + "｜原始内容（前200字符）：" + response.text[:200]
        )

        return None



def submit_sign(session, token):
    """用给定token提交一次签到请求，返回解析后的JSON（失败返回None）。"""

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

    return safe_json(result, "签到(signadd)")



def sign(session):


    token = None

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



    data = submit_sign(session, token)

    if data is not None:

        msg = str(data.get("msg") or data.get("message") or "")

        # CSRF mismatch 意味着提交时token已失效，重新获取一次新token再试一次，
        # 而不是直接判定失败（这是之前偶发失败的主要原因之一）
        if (not data.get("success")) and "csrf" in msg.lower():

            logger(
                "签到token失效（CSRF mismatch），重新获取token后重试一次..."
            )

            time.sleep(2)

            fresh_token = get_token(session)

            if fresh_token:

                data = submit_sign(session, fresh_token)

                msg = str(data.get("msg") or data.get("message") or "") if data else ""

            else:

                logger(
                    "重试时仍无法获取token"
                )

        if data is None:

            pass  # safe_json 已经打印过详细错误了

        elif data.get("success"):

            logger(
                "今日签到成功"
            )

        elif "已" in msg or "重复" in msg or "duplicate" in msg.lower():

            # 明确是"今天已经签过了"这种提示，才归类为已签到
            logger(
                "今日已经签到过了（服务器提示：" + msg + "）"
            )

        else:

            # 其它情况一律视为真正的签到失败（如参数错误、被风控拦截等），
            # 单独打印出来方便排查
            logger(
                "签到失败：" + (msg if msg else "未知错误，原始返回：" + str(data))
            )



    time.sleep(1.5)



    try:


        # 刚签到成功时，服务器的乐豆/延保/连续天数可能还没同步过来，
        # 这里做几次重试，每次间隔递增，直到拿到非空数据
        info = None
        ledou = None
        service_amount = None

        for attempt in range(4):

            time.sleep(2 + attempt * 2)

            info_resp = session.get(

                "https://mclub.lenovo.com.cn/signuserinfo",

                headers=ajax_headers(),

                timeout=15

            )

            info = safe_json(info_resp, "用户信息(signuserinfo)")

            if info:

                ledou = info.get("ledou")
                service_amount = info.get("serviceAmount")

            if ledou is not None or service_amount is not None:

                break

            logger(
                "用户信息暂未同步（乐豆/延保为空），" + str(2 + (attempt + 1) * 2) + "秒后重试..."
            )


        logger(
            "乐豆：" + str(ledou)
        )

        logger(
            "延保：" + str(service_amount) + "天"
        )


        cal = None
        days = None

        for attempt in range(4):

            cal_resp = session.get(

                "https://mclub.lenovo.com.cn/getsignincal",

                headers=ajax_headers(),

                timeout=15

            )

            cal = safe_json(cal_resp, "签到日历(getsignincal)")

            if cal:

                days=cal.get(
                    "signinCal",
                    {}
                ).get(
                    "continueCount"
                )

            if days is not None:

                break

            logger(
                "连续签到天数暂未同步，重试..."
            )

            time.sleep(2 + attempt * 2)


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

    main()
