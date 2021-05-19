#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:    Alan
@time:      2021/05/18
"""
import os
import logging
from logging.handlers import RotatingFileHandler

from settings import LOG_DIR


def create_log(name):
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler(os.path.join(LOG_DIR, 'log.txt'), maxBytes=1024 * 1024 * 100,
                                           backupCount=30, encoding='utf-8')

    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    fmt = '%(asctime)s %(levelname)0.4s %(filename)s:%(lineno)d %(message)s'
    formatter = logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S')

    logging.basicConfig(format=fmt, level=logging.INFO, datefmt='%H:%M:%S')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    _logger = logging.getLogger(name)
    _logger.addHandler(file_log_handler)
    return _logger


logger = create_log(__file__)
