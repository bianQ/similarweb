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
    url = 'http://myip.ipip.net'
    print('========== 本机ip ==========')
    resp1 = session.get(url)
    print(resp1.text)
    print('========== 代理ip ==========')
    proxy = proxy_server.get_proxy()
    print(f"代理配置 {proxy}")
    resp2 = session.get(url, headers=headers, proxies={'https': f"https://{proxy['ip']}:{proxy['port']}"})
    print(resp2.text)


if __name__ == '__main__':
    main()
