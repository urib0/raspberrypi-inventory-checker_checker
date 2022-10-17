#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import time

url = "https://ponkichi.blog/raspberrypi-inventory-checker/"

items = [
    "Raspberry Pi 4 Model B / 2GB",
    "Raspberry Pi 4 Model B / 4GB",
    "Raspberry Pi 4 Model B / 8GB",
    "Raspberry Pi Zero2 W"
]

def send_line_message(token,message):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": "Bearer " + token,
    }
    files = {
        "message": (None, message),
    }
    res = requests.post(url, headers=headers, files=files)
    return res

def send_slack_message(token,channel,message):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": "Bearer " + token,
    }
    data = {
        "channel": channel,
        "text": message
    }
    res = requests.post(url, headers=headers, data=data)
    return res

while(True):
    # 設定値読み込み
    with open("./config.json", "r") as f:
        conf = json.loads(f.read())

    msg = ""
    # 在庫チェック&メッセージ作成
    sp = BeautifulSoup(requests.get(url).text, "html.parser")
    title = sp.find("title").text.split(":")[0]
    table = sp.find_all("tr")[1:]
    for row in table:
        item_name = row.find(class_="column-1").get_text()
        shop_name = row.find(class_="column-2").get_text()
        stock_status = row.find(class_="column-4").get_text()
        item_url = row.find(class_="column-5").find("a").get("href")
        if item_name in items:
            if stock_status == "〇在庫あり" and shop_name != "Amazon":
                msg = msg + f"\n[{shop_name}] {item_name}\n{stock_status}\n{item_url}"
    print(msg)
    # メッセージ送信
    if len(msg) != 0:
        ret = send_line_message(conf["line_token"],msg)
        print(f"line notifier response:{ret}")
#        ret = send_slack_message(conf["slack_token"],conf["slack_channel"],msg)
#        print(f"slack notifier response:{ret}")

    time.sleep(conf["interval"])

