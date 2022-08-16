#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json


class Server_chan:
    def __init__(self, send_key: str) -> None:
        self.send_key = send_key

    def send_message(self, title: str, content: str) -> bool:
        data = {"title": title, "desp": content}
        response = requests.post(
            f"https://sctapi.ftqq.com/{self.send_key}.send", data=data
        )
        res_data = response.json().get("data")
        pushid = res_data.get("pushid")
        readkey = res_data.get("readkey")
        result = requests.get(
            f"https://sctapi.ftqq.com/push?id={pushid}&readkey={readkey}"
        )
        return True if result.json().get("code") == 0 else False


class Wechat_message:
    def __init__(self, corpid: str, corpsecret: str, agentid: str) -> None:
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.token = (
            requests.get(
                f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
            )
            .json()
            .get("access_token")
        )

    def send_message(self, content: str) -> bool:
        data = {
            "touser": "@all",
            "msgtype": "text",
            "agentid": self.agentid,
            "text": {"content": content},
            "safe": 0,
        }
        response = requests.post(
            f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.token}",
            data=json.dumps(data),
        )
        return True if response.json().get("errcode") == 0 else False
