import _thread
import time

import requests

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/6.5.19 NetType/4G Language/zh_TW",
}

# mainUrl = 'http://ipinfo.ipidea.io'


mainUrl = 'https://api.myip.la/en?json'

username = 'zbipuser-zone-custom-region-ae'
password = 'zbip123'

def Merge(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res 

def testUrl(username, password):
    ip = {}
    
    entry = 'http://{}:{}@proxy.ipidea.io:2334'.format(username, password)
    proxy = {
        'http': entry,
        'https': entry,
    }
    try:
        res = requests.get(mainUrl, headers=headers, proxies=proxy, timeout=10)
        print(res.status_code, res.text)
        ipstr = str(res.json()["ip"])
    except Exception as e:
        ipstr = ''
        print("访问失败", e)
        pass
    if ipstr:
        ip['ip'] =  ipstr
        print(type(ip), ip)
        port = {'port': '2333'}
        print(type(port), port)
        data = Merge(ip, port)
        # data = dict([ip.items()] + [port.items()])
    else:
        data = {}
    return data

ip = testUrl(username, password)
print(type(ip), ip)
port = 2333 #  默认端口号就是2333

##
##for port in range(0, 2):
##    _thread.start_new_thread(testUrl, ())
##    time.sleep(0.1)
##
##time.sleep(10)
