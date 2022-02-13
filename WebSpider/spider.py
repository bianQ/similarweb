#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:    Alan
@time:      2021/05/18
"""
import random
import time
import os
import json
from typing import Sequence
from datetime import datetime
from urllib.parse import parse_qs, urlparse
import string
import zipfile

from retry import retry
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException, ElementNotInteractableException, \
    NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as condition
from selenium.webdriver.support.ui import WebDriverWait as Wait

from settings import CHROME_PATH, START_URLS, PROXY, CHROME_PLUGIN_DIR, LOG_DIR, REFER_URLS, USER, PWD, STATIC_DIR, \
    SLEEP_TIME_MIN, SLEEP_TIME_MAX, SCROLL_TIME_MAX, USE_THIRD_PROXY, WAIT_DURATION, MIN_RUN_SECONDS, MAX_RUN_SECONDS

from WebSpider.models import CoinLog
from logger import logger


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


def sleep(min_second=SLEEP_TIME_MIN, max_second=SLEEP_TIME_MAX):
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

    def __init__(self, use_plugin=False, use_proxy=False, load_img=True, timeout=60,
                 duration=(MIN_RUN_SECONDS, MAX_RUN_SECONDS), window=True):
        self.logger = logger
        self.option = Options()
        self.option.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.proxyauth_plugin_path = self.create_proxyauth_extension(
            proxy_host="as.ipidea.io",
            proxy_port=2333,
            proxy_username=USER,
            proxy_password=PWD,
        )
        if use_plugin:
            self.load_plugin()
        if use_proxy:
            # self.set_proxy()
            self.set_proxy_by_plugin()
        if not window:
            self.option.add_argument('--headless')
            self.option.add_argument('--disable-gpu')
            self.option.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML'
                                     ', like Gecko) Chrome/90.0.4430.212 Safari/537.36')
        if not load_img:
            self.option.add_argument('blink-settings=imagesEnabled=false')
        # 设置 Referer，配置不生效
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
        # time.sleep(3)
        # 指定运行时长
        self.plan_duration = _random(duration)
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
        if USE_THIRD_PROXY:
            from WebSpider.proxy import proxy_server

            proxy = proxy_server.get_proxy()
            if not proxy:
                self.logger.error("第三方代理获取失败")
                raise ValueError("第三方代理获取失败")
            self.logger.info(f"代理IP：{str(proxy)}")
            self.option.add_argument(f"--proxy-server=http://{proxy['ip']}:{proxy['port']}")
        else:
            self.option.add_argument(f"--proxy-server={PROXY['PROTOCOL']}://{PROXY['IP']}:{PROXY['PORT']}")

    def set_proxy_by_plugin(self):
        # proxyauth_plugin_path = self.create_proxyauth_extension(
        #     proxy_host="as.ipidea.io",
        #     proxy_port=2333,
        #     proxy_username=USER,
        #     proxy_password=PWD
        # )
        self.option.add_extension(os.path.join(STATIC_DIR, 'vimm_chrome_proxyauth_plugin.zip'))

    def load_plugin(self):
        for path in CHROME_PLUGIN_DIR:
            self.option.add_argument(fr'load-extension={path}')

    def create_proxyauth_extension(self, proxy_host, proxy_port, proxy_username, proxy_password,
                               scheme='http', plugin_path=None):
        if plugin_path is None:
            # 插件地址
            plugin_path = 'vimm_chrome_proxyauth_plugin.zip'
        manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """

        background_js = string.Template(
            """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                      singleProxy: {
                        scheme: "${scheme}",
                        host: "${host}",
                        port: parseInt(${port})
                      },
                      bypassList: ["foobar.com", "file.dd.net", "accounts.google.com"]
                    }
                  };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "${username}",
                        password: "${password}"
                    }
                };
            }

            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """
        ).substitute(
            host=proxy_host,
            port=proxy_port,
            username=proxy_username,
            password=proxy_password,
            scheme=scheme,
        )
        with zipfile.ZipFile(plugin_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        return plugin_path

    @property
    def is_alive(self):
        return self.dr.service.process is not None

    @sleep()
    def get(self, url):
        self.dr.get(url)

    @sleep(max_second=SCROLL_TIME_MAX)
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
        if len(self.dr.window_handles) > 1:
            self.dr.close()
            self.dr.switch_to.window(self.dr.window_handles[0])
        nav_path = '//ul[@class="header-ul"]/li'
        navs = self.dr.find_elements_by_xpath(nav_path)
        nav_element = _random(navs, item_probability={1: 0.2, 2: 0.4, 3: 0.2})
        self.logger.info(f"{self}：选择主导航 {nav_element.text}")
        self.click(nav_element, wait="header-ul")
        nav_text = nav_element.text
        # 子导航
        sub_nav_id = None
        sub_nav_spans = self.dr.find_elements_by_xpath(f"{nav_path}//span")
        for span in sub_nav_spans:
            if span.text == nav_text:
                sub_nav_id = span.get_attribute("aria-controls")
        if sub_nav_id:
            sub_nav_path = f'//ul[@id="{sub_nav_id}"]/li'
            sub_navs = self.dr.find_elements_by_xpath(sub_nav_path)
            # 选择交易时，指定子导航的点击概率
            item_probability = {0: 0.85} if nav_text == "交易" else None
            nav_to_click = _random(sub_navs, item_probability)
            nav_text = nav_to_click.text
            self.click(nav_to_click)
        self.logger.info(f"{self}：点击导航'{nav_text}'")

    @sleep()
    def to_home(self):
        try:
            self.dr.find_element_by_class_name("header-logo-div").click()
        except (ElementNotInteractableException, NoSuchElementException):
            self.get(self.home)

    def confirm_protocol(self):
        try:
            self.dr.find_element_by_class_name("ex-btn5").click()
            self.dr.find_element_by_class_name("less-btn1").click()
        except (ElementNotInteractableException, NoSuchElementException):
            pass

    @sleep(min_second=2, max_second=5)
    @retry(exceptions=WebDriverException, tries=3, delay=2, logger=logger)
    def random_click(self, class_name, limit=None, **kwargs):
        self.confirm_protocol()
        corn_types = self.dr.find_elements_by_class_name(class_name)
        if corn_types:
            item_probability = kwargs.get('item_probability')
            typ = _random(corn_types if not limit else corn_types[:limit], item_probability)
            self.click(typ, wait=class_name)
            current_url = self.dr.current_url
            coin_log = os.path.join(LOG_DIR, 'coin_log.txt')
            symbols = urlparse(current_url).path.split('/')[-1]
            with open(coin_log, 'a') as f:
                data = json.dumps({'symbols': symbols})
                f.write(data + "\n")
            CoinLog.add_log(symbols=symbols)

    def random_click_many(self, class_name, min_iter=1, max_iter=5, limit=None, duration=WAIT_DURATION, **kwargs):
        random_times = random.randint(min_iter, max_iter)
        stop = False
        random_counts = 0
        start_time = time.time()
        while not stop:
            self.random_click(class_name, limit, **kwargs)
            # 记录交易页访问币种数量
            self.view_urls.add(self.dr.current_url)
            random_counts += 1
            random_duration = time.time() - start_time
            if duration:
                if random_duration > duration:
                    stop = True
            elif random_counts >= random_times:
                stop = True

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
        self.click_nav()
        if len(self.dr.window_handles) > 1:
            self.dr.switch_to.window(self.dr.window_handles[-1])
        self.confirm_protocol()
        parser = urlparse(self.dr.current_url)
        if parser.path in ['/markets', '/otc/trade']:
            self.scroll()
        elif parser.path.startswith("/currencyExchangeTwo"):
            self.random_click_many('list-tbody', min_iter=3, max_iter=10, limit=15)
            self.to_home()
            time.sleep(2)
            raise TimeoutException()
        elif parser.path.startswith("/currencyExchange"):
            time.sleep(2)
            self.to_home()
        elif parser.path.startswith("/contract/exchange"):
            self.random_click_many('contract-list-tbody', min_iter=3, max_iter=10, limit=15)
            self.to_home()
            time.sleep(2)
            raise TimeoutException()
        else:
            self.scroll()
            self.to_home()

    def loop_event(self):
        while self.duration < self.plan_duration:
            self.event()
            parse = urlparse(self.dr.current_url)
            self.view_urls.add(f"{parse.netloc}/{parse.path}")
