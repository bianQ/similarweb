#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:    Alan
@time:      2021/05/18
"""
import os

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
    'PORT': '7891',
    'PROTOCOL': 'socks5'
}

# 线程数量
THREAD_MAX_NUM = 5

# 浏览器插件配置
CHROME_PLUGIN_DIR = []

# 主页
START_URLS = [
    'https://zb.com/cn/',
    'https://zb.com/en/',
    'https://zb.com/kr/'
]
