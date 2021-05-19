#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:    Alan
@time:      2021/05/18
"""
import random
import time
from typing import Sequence
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from retry import retry
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as condition
from selenium.webdriver.support.ui import WebDriverWait as Wait

from settings import CHROME_PATH, START_URLS
from logger import logger


class PageTree:

    nav = {
        ''
    }


def _random(data: Sequence):
    return random.choice(data)


def sleep(min_second=3, max_second=7):
    def decorate(fn):
        def wrapper(self, *args, **kwargs):
            second = random.randint(min_second, max(min_second, max_second))
            try:
                res = fn(self, *args, **kwargs)
                self.logger.info(f"睡眠{second}秒")
                time.sleep(second)
                return res
            except Exception as e:
                self.logger.error(e)
                self.logger.error(f"{fn.__name__}, {args}, {kwargs}")
                raise e
        return wrapper
    return decorate


class Spider:

    def __init__(self, use_plugin=False, use_proxy=False, load_img=True, timeout=60, duration=(4, 6)):
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
        self.start_time = None
        self.home = _random(START_URLS)
        self.main_path = urlparse(self.home).path
        # 指定运行时长
        self.plan_duration = _random(duration) * 60

    # 等待某个元素加载完
    def _wait(self, by, value):
        Wait(self.dr, 30).until(
            condition.presence_of_element_located((by, value)), message="元素加载失败")

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

    @property
    def duration(self):
        return time.time() - self.start_time.timestamp()

    @retry(exceptions=WebDriverException, tries=3, logger=logger, delay=1)
    def click(self, element):
        try:
            self._wait(By.CLASS_NAME, element.get_attribute('class'))
            element.click()
            if 'zb.com' not in self.dr.current_url:
                self.dr.close()
                self.dr.switch_to.window(self.dr.window_handles[0])
        except TimeoutException as e:
            self.logger.error(f"{str(e)}, 重载页面")
            self.dr.refresh()

    @sleep()
    @retry(exceptions=WebDriverException, tries=3, delay=2, logger=logger)
    def click_nav(self):
        navs = self.dr.find_elements_by_class_name('nav-item')[:6]
        nav_element = _random(navs)
        self.logger.info(f"选择主导航 {nav_element.text}")
        sub_navs = nav_element.find_elements_by_class_name('menu-link')
        if sub_navs:
            nav_to_click = _random(sub_navs)
            self.click(nav_element)
        else:
            nav_to_click = nav_element
        self.logger.info(f"点击导航'{nav_to_click.text}', {nav_to_click.get_attribute('class')}")
        self.click(nav_to_click)

    @sleep()
    @retry(exceptions=WebDriverException, tries=3, delay=2, logger=logger)
    def random_click(self, class_name, limit=None):
        corn_types = self.dr.find_elements_by_class_name(class_name)
        if corn_types:
            typ = _random(corn_types if not limit else corn_types[:limit])
            self.click(typ)

    def random_click_many(self, class_name, times=5, limit=None):
        for _ in range(0, random.randint(1, times)):
            self.random_click(class_name, limit)

    def run(self):
        self.get(self.home)
        self.start_time = datetime.now()
        self.scroll()
        self.loop_event()

    def loop_event(self):
        while self.duration < self.plan_duration:
            self.click_nav()
            self.scroll()
            parser = urlparse(self.dr.current_url)
            path = parser.path.replace(self.main_path, '').split('/')[0]
            if path == 'markets':
                # 切换币分区
                self.random_click_many('el-tabs__item', times=2, limit=None)
                # 选择币种
                self.random_click('market-body-item')
                corn = self.dr.find_element_by_class_name('trade-pair')
                self.click(corn)
                self.random_click_many('coin-item')
            elif path == 'trade':
                self.random_click_many('tabs-item', times=2, limit=4)
                self.random_click_many('coin-item')
            elif path in ['lever-kline', 'kline']:
                self.random_click_many('coin-item')
