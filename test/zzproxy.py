"""
Author   : Alan
Date     : 2021/7/25 12:01
Email    : vagaab@foxmail.com
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath('.')))

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep
import random
import datetime

from WebSpider.proxy import proxy_server


def main():
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML"
                      ", like Gecko) Mobile/14G60 MicroMessenger/6.5.19 NetType/4G Language/zh_TW",
    }
    session = requests.session()
    #url = 'http://myip.top'
    url = "https://ipinfo.io/"
    print('========== 本机ip ==========')
    resp1 = session.get(url)
    print(resp1.text)
    print('========== 代理ip ==========')
    proxy = proxy_server.get_proxy()
    print(f"代理配置 {proxy}")
    ip = str(proxy['ip'])+":"+str(proxy['port'])
    try:
        options = Options()
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        # 设置代理
        options.add_argument('--proxy-server=http://' + ip)
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-blink-features=AutomationControlled")
        chromedriver = 'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
        dr = webdriver.Chrome(options=options, executable_path=chromedriver)
        # dr.set_page_load_timeout(20)
        # dr.set_script_timeout(20)
        # dr.maximize_window()
        # element = random.choice(elements)
        try:
            dr.get(url)
            sleep(random.uniform(15.07, 25.39))
        except Exception as message:
            print('打开网站报错，报错信息如下：\n', message)
            dr.quit()
            options = Options()
            # options.add_argument('--headless')
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument('--no-sandbox')
            # 设置代理
            options.add_argument('--proxy-server=http://' + ip)
            options.add_argument('--disable-dev-shm-usage')
            chromedriver = 'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
            dr = webdriver.Chrome(options=options, executable_path=chromedriver)
            # dr.set_page_load_timeout(20)
            # dr.set_script_timeout(20)
            dr.get(url)
            sleep(random.uniform(5.07, 5.39))
            print('重新执行一次...')
    except Exception as message:
        print('打开浏览器出错，出错信息如下：\n', message)
        dr = webdriver.Chrome('C:\Program Files\Google\Chrome\Application\chromedriver.exe')



if __name__ == '__main__':
    main()
