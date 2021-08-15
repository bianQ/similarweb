"""
Author   : Alan
Date     : 2021/7/24 9:39
Email    : vagaab@foxmail.com
"""
import requests
from retry import retry

from settings import GET_IP_URL, WHITE_URL, USER, PWD


def get_my_ip():
    try:
        # resp = requests.get('http://myip.top', timeout=2)
        resp = requests.get('http://ipinfo.io', timeout=2)
        return resp.json().get('ip')
    except Exception as e:
        print(e)


def Merge(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res 


class Proxy:

    def __init__(self):
        self.sessoin = requests.session()
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/6.5.19 NetType/4G Language/zh_TW",
        }
        self.mainUrl = 'https://api.myip.la/en?json'

        # if not WHITE_URL or not GET_IP_URL:
        #     raise ValueError("缺少代理配置")
        # # 设置白名单
        # my_ip = get_my_ip()
        # if my_ip:
        #     self.set_white(my_ip)

    @retry(exceptions=Exception, delay=1)
    def get_proxy(self) -> dict:
        ip = {}
        # data = self.sessoin.get(GET_IP_URL).json()
        # return data['data'][0]
        entry = 'http://{}:{}@proxy.ipidea.io:2334'.format(USER, PWD)
        proxy = {
            'http': entry,
            'https': entry,
        }
        try:
            res = requests.get(self.mainUrl, headers=self.headers, proxies=proxy, timeout=10)
            print(res.status_code, res.text)
            ipstr = str(res.json()["ip"])
        except Exception as e:
            ipstr = ''
            print("访问失败", e)
            pass
        if ipstr:
            ip['ip'] = ipstr
            # print(type(ip), ip)
            port = {'port': '2334'}
            # print(type(port), port)
            data = Merge(ip, port)
            # data = dict([ip.items()] + [port.items()])
        else:
            data = {}
        return data

    def set_white(self, ip):
        url = WHITE_URL + ip
        res = self.sessoin.get(url)
        print(res.text)


proxy_server = Proxy()
