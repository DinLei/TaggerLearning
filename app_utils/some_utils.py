#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/11/16 10:57
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com

import logging
import numpy as np
import logging.handlers


def max_min(arr, log=True):
    """
    最大最小值归一
    :return: 
    """
    from sklearn import preprocessing
    assert isinstance(arr, list) or isinstance(arr, np.ndarray)
    normalizer = preprocessing.minmax_scale
    new_arr = np.array(arr)
    if log:
        new_arr = np.log(1+new_arr)
    return normalizer(new_arr)


def is_integer(string):
    import re
    return re.match('\d+$', string)


def time_elapse(func):
    import time
    from functools import wraps

    @wraps(func)
    def wrapper(*arg, **kwargs):
        cur = time.time()
        if not arg and not kwargs:
            func()
        elif arg and kwargs:
            func(*arg, **kwargs)
        elif arg:
            func(*arg)
        elif kwargs:
            func(**kwargs)
        print("耗时: %s 秒！" % (time.time()-cur))
    return wrapper


def get_logger(logger_name, level=logging.DEBUG, filename=None):
    logger = logging.getLogger(logger_name)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter('%(asctime)s [%(pathname)s:%(lineno)d:%(funcName)s] %(message)s'))
    stream_handler.setLevel(level)
    logger.setLevel(level=level)
    logger.addHandler(stream_handler)

    if filename:
        file_handler = logging.handlers.TimedRotatingFileHandler(filename, when='D', encoding='utf-8')
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s [%(pathname)s:%(lineno)d:%(funcName)s] %(message)s'))
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    return logger


def get_date_seq(start, end=None):
    import re
    import time
    import datetime
    if not end:
        end = time.strftime("%Y-%m-%d", time.localtime())
    if isinstance(start, str):
        if re.match("\d{4}-\d{2}-\d{2}", start):
            start = [int(x) for x in start.split("-")]
    if isinstance(end, str):
        if re.match("\d{4}-\d{2}-\d{2}", end):
            end = [int(x) for x in end.split("-")]
    start_date = datetime.date(*start)
    end_date = datetime.date(*end)

    result = []
    curr_date = start_date
    while curr_date != end_date:
        result.append("%04d-%02d-%02d" % (curr_date.year, curr_date.month, curr_date.day))
        curr_date += datetime.timedelta(1)
    result.append("%04d-%02d-%02d" % (curr_date.year, curr_date.month, curr_date.day))
    return result


def get_date_range(date, span_days):
    import datetime
    date_format = '%Y-%m-%d'
    start_date = datetime.datetime.strptime(date, date_format) - datetime.timedelta(span_days)
    start_date = start_date.strftime(date_format)
    end_date = date
    return start_date, end_date


def flatten(arr):
    outcome = []
    for ele in arr:
        if isinstance(ele, str) or isinstance(ele, int):
            outcome.append(ele)
        elif isinstance(ele, dict):
            outcome.extend(flatten(
                list(ele.values())
            ))
        elif isinstance(ele, tuple) or isinstance(ele, list):
            outcome.extend(flatten(ele))
    return outcome


if __name__ == "__main__":
    print(get_date_seq((2014, 7, 28), (2014, 8, 3)))
