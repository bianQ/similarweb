# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import click

from settings import THREAD_MAX_NUM, RUNNING_TIMES, USE_WINDOW, LOAD_PLUGIN, LOAD_IMAGE
from WebSpider.spider import Spider
from WebSpider.threads import MultiThread


def create_spider(use_plugin, use_proxy, window, image):
    spider = Spider(use_plugin=use_plugin, use_proxy=use_proxy, window=window, load_img=image)
    spider.run()


@click.command()
@click.option('--image', type=bool, default=LOAD_IMAGE, help="是否加载图片")
@click.option('--use_plugin', type=bool, default=LOAD_PLUGIN, help="是否加载插件")
@click.option('--use_proxy', type=bool, default=False, help="是否使用代理")
@click.option('--workers', type=int, default=THREAD_MAX_NUM, help="使用线程数量，默认为CPU内核数量的5倍")
@click.option('--times', type=int, default=RUNNING_TIMES, help="一共访问多少次，默认10次")
@click.option('--window', type=bool, default=USE_WINDOW, help="是否使用窗口模式")
def run(image, use_plugin, use_proxy, workers, times, window):
    pool = MultiThread(max_workers=workers)
    for _ in range(times):
        pool.execute(create_spider, use_plugin, use_proxy, window, image)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
