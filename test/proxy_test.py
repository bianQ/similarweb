"""
Author   : Alan
Date     : 2021/7/25 12:01
Email    : vagaab@foxmail.com
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath('.')))

import requests

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
    resp2 = session.get(url, headers=headers, proxies={'http': f"http://{proxy['ip']}:{proxy['port']}"})
    print(resp2.text)



def zmain():
    from requests.auth import HTTPBasicAuth
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
    user = "zbipuser"
    pwd = "zbip123"
    url = r"proxy.ipidea.io:2333"
    req = requests.get(url, auth=HTTPBasicAuth(user, pwd))#.text
    print(req)
   # proxy = req
   # print(f"代理配置 {proxy}")
   # resp2 = session.get(url, headers=headers, proxies={'http': f"http://{proxy['ip']}:{proxy['port']}"})
   # print(resp2.text)


if __name__ == '__main__':
    #zmain()
    from requests.auth import HTTPBasicAuth
    print('========== 代理ip ==========')
    user = "zbipuser-zone-custom-region-ae"
    pwd = "zbip123"
    url = r"proxy.ipidea.io:2333"
    req = requests.get(url, auth=HTTPBasicAuth(user, pwd))#.text
    print(req)
    
