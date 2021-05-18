# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import click

from WebSpider.spider import Spider


@click.command()
@click.option('--use_plugin', type=bool, default=False, help="是否加载插件")
@click.option('--use_proxy', type=bool, default=False, help="是否使用代理")
def run(use_plugin, use_proxy):
    spider = Spider(use_plugin=use_plugin, use_proxy=use_proxy)
    spider.run()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
