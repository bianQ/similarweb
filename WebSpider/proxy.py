"""
Author   : Alan
Date     : 2021/7/24 9:39
Email    : vagaab@foxmail.com
"""
import requests
from retry import retry

from settings import GET_IP_URL, WHITE_URL


def get_my_ip():
    try:
        resp = requests.get('http://myip.top', timeout=2)
        return resp.json().get('ip')
    except Exception as e:
        print(e)


class Proxy:

    def __init__(self):
        self.sessoin = requests.session()

        if not WHITE_URL or not GET_IP_URL:
            raise ValueError("缺少代理配置")
        # 设置白名单
        my_ip = get_my_ip()
        if my_ip:
            self.set_white(my_ip)

    @retry(exceptions=Exception, delay=1)
    def get_proxy(self) -> dict:
        data = self.sessoin.get(GET_IP_URL).json()
        return data['data'][0]

    def set_white(self, ip):
        url = WHITE_URL + ip
        res = self.sessoin.get(url)
        print(res.text)


proxy_server = Proxy()
