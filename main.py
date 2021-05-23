# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import click

from WebSpider.spider import Spider
from WebSpider.threads import MultiThread


def create_spider(use_plugin, use_proxy):
    spider = Spider(use_plugin=use_plugin, use_proxy=use_proxy)
    spider.run()


@click.command()
@click.option('--use_plugin', type=bool, default=False, help="是否加载插件")
@click.option('--use_proxy', type=bool, default=False, help="是否使用代理")
@click.option('--workers', type=int, default=None, help="使用线程数量，默认为CPU内核数量的5倍")
@click.option('--times', type=int, default=0, help="一共访问多少次，默认10次")
def run(use_plugin, use_proxy, workers, times):
    pool = MultiThread(max_workers=workers)
    for _ in range(times or 10):
        pool.execute(create_spider, use_plugin, use_proxy)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
