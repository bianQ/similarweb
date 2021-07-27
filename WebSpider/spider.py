#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:    Alan
@time:      2021/05/18
"""
import random
import time
import os
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

from settings import CHROME_PATH, START_URLS, PROXY, CHROME_PLUGIN_DIR, LOG_DIR, REFER_URLS
from WebSpider.models import CoinLog
from logger import logger


class PageTree:

    nav = {
        ''
    }


def _random(data: Sequence, item_probability: dict = None):
    """
    :param data:
    :param item_probability: 根据索引指定元素被选中的概率，概率值小于等于 1
    :return:
    """
    if item_probability is not None:
        total_probability = sum(item_probability.values())
        assert total_probability <= 1, ValueError("概率之和不能大于 1")
        new_data = []
        for index, item in enumerate(data):
            probability = item_probability.get(index)
            if not probability:
                probability = (1 - total_probability) / (len(data) - len(item_probability))
            new_data.extend([item] * int(probability * 100))
    else:
        new_data = data
    return random.choice(new_data)


def sleep(min_second=3, max_second=7):
    def decorate(fn):
        def wrapper(self, *args, **kwargs):
            second = random.randint(min_second, max(min_second, max_second))
            try:
                res = fn(self, *args, **kwargs)
                self.logger.info(f"{self}：睡眠{second}秒")
                time.sleep(second)
                return res
            except Exception as e:
                self.logger.error(f"{self}：{str(e)}")
                self.logger.error(f"{self}：{fn.__name__}, {args}, {kwargs}")
                if fn.__name__ == 'get':
                    raise e
                self.dr.refresh()
                time.sleep(second)
        return wrapper
    return decorate


class Spider:

    def __init__(self, use_plugin=False, use_proxy=False, load_img=True, timeout=60, duration=(4, 6),
                 window=True):
        self.logger = logger
        self.option = Options()
        self.option.add_experimental_option('excludeSwitches', ['enable-logging'])
        if use_proxy:
            self.set_proxy()
        if use_plugin:
            self.load_plugin()
        if not window:
            self.option.add_argument('--headless')
            self.option.add_argument('--disable-gpu')
            self.option.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML'
                                     ', like Gecko) Chrome/90.0.4430.212 Safari/537.36')

        if random.randint(0, 9) < 2:
            refer = random.choice(REFER_URLS)
            self.option.add_argument(f'-Referer={refer}')

        self.dr = webdriver.Chrome(executable_path=CHROME_PATH, options=self.option)
        try:
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
        except WebDriverException as e:
            self.logger.error(f"浏览器初始化失败：{str(e)}")
            self.dr.quit()
        self.start_time = None
        self.home = _random(START_URLS)
        self.main_path = urlparse(self.home).path
        # 指定运行时长
        self.plan_duration = _random(duration) * 60
        # 访问过的链接
        self.view_urls = set()

    def __repr__(self):
        return f"<Spider-{id(self)}>"

    # 等待某个元素加载完
    def _wait(self, by, value):
        self.logger.info(f"{self}：等待加载 {value} 元素")
        Wait(self.dr, 30).until(
            condition.presence_of_element_located((by, value)), message="元素加载失败")

    def set_proxy(self):
        from WebSpider.proxy import proxy_server

        proxy = proxy_server.get_proxy()
        if proxy:
            self.option.add_argument(f"--proxy-server=https://{proxy['ip']}:{proxy['port']}")
        else:
            self.option.add_argument(f"--proxy-server={PROXY['PROTOCOL']}://{PROXY['IP']}:{PROXY['PORT']}")

    def load_plugin(self):
        for path in CHROME_PLUGIN_DIR:
            self.option.add_argument(fr'load-extension={path}')

    @property
    def is_alive(self):
        return self.dr.service.process is not None

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
        self.logger.info(f"{self}：随机滚动{scroll_times}次")
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
    def click(self, element, wait=None):
        try:
            class_name = wait or element.get_attribute('class')
            self._wait(By.CLASS_NAME, class_name)
            element.click()
        except TimeoutException as e:
            self.logger.error(f"{self}：{str(e)}, 重载页面")
            self.dr.refresh()

    @sleep()
    def click_nav(self):
        nav_class = 'nav-item'
        navs = self.dr.find_elements_by_class_name(nav_class)[:6]
        nav_element = _random(navs, {1: 0.05, 2: 0.9, 5: 0.05})
        self.logger.info(f"{self}：选择主导航 {nav_element.text}")
        sub_nav_class = 'menu-link'
        sub_navs = nav_element.find_elements_by_class_name(sub_nav_class)
        if sub_navs:
            # 选择交易时，指定子导航的点击概率
            trade_nav = nav_element.find_elements_by_class_name("trade-menu")
            item_probability = {1: 0.85} if trade_nav else None
            nav_to_click = _random(sub_navs, item_probability)
            self.click(nav_element, wait=nav_class)
        else:
            nav_to_click = nav_element
        self.logger.info(f"{self}：点击导航'{nav_to_click.text}', {nav_to_click.get_attribute('class')}")
        self.click(nav_to_click, wait=sub_nav_class)

    @sleep()
    def click_corn_item(self, item_probability=None):
        if 'markets' not in self.dr.current_url:
            item_class = 'trade-pair'
            corn = self.dr.find_element_by_class_name(item_class)
            self.click(corn, wait=item_class)
            time.sleep(2)
            self.random_click_many('coin-item', min_iter=3, max_iter=5, limit=20, item_probability=item_probability)

    @sleep()
    def to_home(self, path):
        home_class = 'logo-wrap' if path not in ['lever-kline', 'kline'] else 'menu-logo'
        home = self.dr.find_element_by_class_name(home_class)
        self.click(home)

    @sleep()
    @retry(exceptions=WebDriverException, tries=3, delay=2, logger=logger)
    def random_click(self, class_name, limit=None, **kwargs):
        corn_types = self.dr.find_elements_by_class_name(class_name)
        if corn_types:
            item_probability = kwargs.get('item_probability')
            typ = _random(corn_types if not limit else corn_types[:limit], item_probability)
            self.click(typ, wait=class_name)
            current_url = self.dr.current_url
            if 'kline' in current_url or 'trade' in current_url:
                CoinLog.add_log(symbols=urlparse(current_url).path)

    def random_click_many(self, class_name, min_iter=1, max_iter=5, limit=None, **kwargs):
        for _ in range(0, random.randint(min_iter, max_iter)):
            self.random_click(class_name, limit, **kwargs)
            # 记录交易页访问币种数量
            if 'kline' in self.dr.current_url:
                self.view_urls.add(self.dr.current_url)

    def run(self):
        if not self.is_alive:
            return
        try:
            self.get(self.home)
            self.view_urls.add(self.home)
            self.start_time = datetime.now()
            self.scroll()
            self.loop_event()
        except TimeoutException:
            self.logger.error(f"{self}：浏览器加载超时退出")
        finally:
            self.dr.quit()
            view_url_count = len(self.view_urls)
            if view_url_count >= 2:
                success_log = os.path.join(LOG_DIR, 'success.txt')
                with open(success_log, 'a') as f:
                    f.write(f"{self}, {view_url_count}, {self.start_time}\n")

    def event(self):
        if len(self.dr.window_handles) > 1:
            self.dr.switch_to.window(self.dr.window_handles[0])
        if 'kline' in self.dr.current_url:
            self.logger.info(f"{self}：open kline {self.dr.current_url}")
        self.click_nav()
        parser = urlparse(self.dr.current_url)
        path = parser.path.replace(self.main_path, '').split('/')[0]
        if path == 'markets':
            self.scroll()
            # 切换币分区
            self.random_click_many('el-tabs__item', max_iter=2, limit=None)
            # 选择币种
            self.random_click('market-body-item')
            self.click_corn_item()
            self.to_home(path)
        elif path == 'trade':
            self.random_click_many('tabs-item', max_iter=2, limit=4)
            self.random_click_many('coin-item', max_iter=15)
        elif path in ['lever-kline', 'kline']:
            self.click_corn_item(item_probability={1: 0.15, 2: 0.15})
            self.to_home(path)

    def loop_event(self):
        while self.duration < self.plan_duration:
            self.event()
            # parse = urlparse(self.dr.current_url)
            # self.view_urls.add(f"{parse.netloc}/{parse.path}")
