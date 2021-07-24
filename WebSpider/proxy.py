"""
Author   : Alan
Date     : 2021/7/24 9:39
Email    : vagaab@foxmail.com
"""
import requests
from retry import retry


class Proxy:

    def __init__(self):
        self.sessoin = requests.session()

    @retry(exceptions=Exception, delay=1)
    def get_proxy(self) -> dict:
        url = 'http://tiqu.linksocket.com:81/abroad?num=1&type=2&lb=1&sb=0&flow=1&regions=ae&port=1&n=0'
        data = self.sessoin.get(url).json()
        return data['data'][0]


proxy_server = Proxy()
