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
THREAD_MAX_NUM = 25

# 浏览器插件配置
CHROME_PLUGIN_DIR = []
LOAD_PLUGIN = True

# 主页
START_URLS = [
    'https://www.zb.com/cn/',
    'https://www.zb.com/en/',
    'https://www.zb.com/kr/'
]

# 运行次数
RUNNING_TIMES = 1200000

# 是否使用窗口模式 True/False
USE_WINDOW = False

# 是否加载图片
LOAD_IMAGE = True

# 数据库
if os.path.exists("env.json"):
    with open("env.json", 'r') as f:
        ENV = json.loads(f.read())
        DATABASE = ENV["DATABASE"]
else:
    ENV = {}
    DATABASE = {
        'host': "",
        'port': 3306,
        'user': "",
        'password': "",
        'db': "",
    }


# ============== 第三方代理设置 ==============
# 获取 ip 的链接
GET_IP_URL = ENV.get("GET_IP_URL")
# 设置白名单的链接
WHITE_URL = ENV.get("WHITE_URL")

# refer 设置
REFER_URLS = [
    "https://coinmarketcap.com/",
    "https://coingecko.com/",
    "https://feixiaohao.cc/"
    "https://hypertechgrp.com/",
    "https://hokk.finance/"
]
