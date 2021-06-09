#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:    Alan
@time:      2021/05/18
"""
import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


class MultiThread(ThreadPoolExecutor):

    def __init__(self, max_workers=None, thread_name_prefix=''):
        super().__init__(max_workers, thread_name_prefix)

    def thread_log(self, worker):
        """捕获线程异常，并保存日志"""
        try:
            result = worker.result()
            return result
        except:
            traceback.print_exc()

    def execute(self, fn, *args, **kwargs):
        """生成新线程，并捕捉异常"""
        thread = self.submit(fn, *args, **kwargs)
        thread.add_done_callback(self.thread_log)
        return thread

    @staticmethod
    def execute_after_done(fn, workers, *args, **kwargs):
        wait(workers, timeout=86400, return_when=ALL_COMPLETED)
        return fn(*args, **kwargs)


async def async_func(fn, *args, **kwargs):
    second = kwargs.pop('second', 0)
    res = fn(*args, **kwargs)
    if second:
        await asyncio.sleep(second)
    return res


async def async_func_with_self(fn, self, *args, **kwargs):
    second = kwargs.pop('second', 0)
    res = fn(self, *args, **kwargs)
    if second:
        self.logger.info(f"{self}：睡眠{second}秒")
        await asyncio.sleep(second)
    return res
