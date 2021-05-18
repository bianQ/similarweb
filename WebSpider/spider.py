#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:    Alan
@time:      2021/05/18
"""
import random
import time
import functools

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from settings import CHROME_PATH, START_URLS
from logger import logger


class PageTree:

    nav = {
        ''
    }


def _random(data):
    return random.choice(data)


def sleep(min_second=1, max_second=5):
    def decorate(fn):
        def wrapper(self, *args, **kwargs):
            second = random.randint(min_second, max_second)
            res = fn(self, *args, **kwargs)
            self.logger.info(f"睡眠{second}秒")
            time.sleep(second)
            return res
        return wrapper
    return decorate


class Spider:

    def __init__(self, use_plugin=False, use_proxy=False, load_img=True, timeout=30):
        self.option = Options()
        self.option.add_experimental_option('excludeSwitches', ['enable-logging'])
        if use_proxy:
            self.set_proxy()

        self.dr = webdriver.Chrome(executable_path=CHROME_PATH, options=self.option)
        self.dr.set_page_load_timeout(timeout)
        self.dr.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    })
                """
            }
        )
        self.logger = logger

    def set_proxy(self):
        self.option.add_argument(f"--proxy-server=socks5://127.0.0.1:10808")

    def load_plugin(self):
        self.option.add_argument('')

    @sleep()
    def get(self, url):
        self.dr.get(url)

    @sleep(max_second=2)
    def _scroll(self, height):
        js = f"var q=document.documentElement.scrollTop={height}"
        self.dr.execute_script(js)

    @sleep()
    def scroll(self):
        scroll_times = random.randint(0, 5)
        self.logger.info(f"随机滚动{scroll_times}次")
        scroll_height = 0
        for _ in range(scroll_times):
            scroll_height += _random(range(400, 700))
            self._scroll(scroll_height)
        while scroll_height > 0:
            scroll_height -= _random(range(400, 700))
            scroll_height = max(scroll_height, 0)
            self._scroll(scroll_height)

    def change_nav(self):
        pass

    def run(self):
        self.get(_random(START_URLS))
        self.scroll()
        time.sleep(15)
