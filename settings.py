#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:    Alan
@time:      2021/05/18
"""
import os
import json

# 项目路径
PROJECT_DIR = os.path.dirname(__file__)

# 浏览器配置，driver 路径
CHROME_PATH = r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'

# 日志保存路径
LOG_DIR = os.path.join(PROJECT_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 代理设置
PROXY = {
    'IP': '127.0.0.1',
    'PORT': '1080',
    'PROTOCOL': 'socks5'
}

# 线程数量
THREAD_MAX_NUM = 5

# 浏览器插件配置
CHROME_PLUGIN_DIR = []
LOAD_PLUGIN = True

# 主页
START_URLS = [
    'https://zb.com/cn/',
    'https://zb.com/en/',
    'https://zb.com/kr/'
]

# 运行次数
RUNNING_TIMES = 10

# 是否使用窗口模式 True/False
USE_WINDOW = True

# 数据库
if os.path.exists("mysql.json"):
    with open("mysql.json", 'r') as f:
        DATABASE = json.loads(f.read())
else:
    DATABASE = {
        'host': "",
        'port': 3306,
        'user': "",
        'password': "",
        'db': "",
    }


# ============== 第三方代理设置 ==============
# 获取 ip 的链接
GET_IP_URL = "http://tiqu.ipidea.io:81/abroad?num=1&type=2&lb=1&sb=0&flow=1&regions=ae&port=1&n=0"
# 设置白名单的链接
WHITE_URL = "http://api.ipidea.net/index/index/save_white?neek=53693&appkey=9a847c6eaa1d6a2998196f330c67ed47&white="

# refer 设置
REFER_URLS = [
    "https://coinmarketcap.com/",
    "https://coingecko.com/",
    "https://feixiaohao.cc/"
    "https://hypertechgrp.com/",
    "https://hokk.finance/"
]
