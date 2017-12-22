#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/11/15 14:22
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com

import re
import os
import pickle
from app_utils.log_utils import get_logger
from config_info.log_config import io_logfile_name

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger = get_logger("running",
                    filename=os.path.join(BASE_DIR, io_logfile_name))


def transfer_data_to_database(data_generator, db_conn, table, batch_size=200):
    if "sqlite" in db_conn.db_type:
        _transfer_data_to_sqlite(data_generator=data_generator, db_conn=db_conn, table=table, batch_size=batch_size)
    elif "mysql" in db_conn.db_type:
        _transfer_data_to_mysql(data_generator=data_generator, db_conn=db_conn, table=table, batch_size=batch_size)
    else:
        print("No this operator")


def transfer_data_to_mongodb(data_generator, collection, total_flag=False, batch_size=500):
    if total_flag:
        collection.insert_many(data_generator)
    elif batch_size:
        items = []
        for item in data_generator:
            if len(items) >= batch_size:
                collection.insert_many(items)
                items = []
            assert isinstance(item, dict)
            items.append(item)
        collection.insert_many(items)
    else:
        for item in data_generator:
            collection.insert_many(item)
    print("转移数据成功!")


def _transfer_data_to_mysql(data_generator, db_conn, table, batch_size=200):
    """
    将数据转存到MySQL数据库
    :param data_generator: list
    :param db_conn: 数据库连接
    :param table: 需要插入的表
    :param batch_size: 批操作数量约束
    :return: 无返回
    """
    items = []
    for item in data_generator:
        if len(items) >= batch_size:
            values = ','.join([repr(i) for i in items])
            sql = "INSERT INTO {table} VALUES {values}".format(table=table, values=values)
            sql = re.sub(r'\bNone\b', 'NULL', sql)
            db_conn.execute(sql)
            items = []
        items.append(item)
    values = ','.join([repr(i) for i in items])
    sql = "INSERT INTO {table} VALUES {values}".format(table=table, values=values)
    sql = re.sub(r'\bNone\b', 'NULL', sql)
    db_conn.execute(sql)
    print("转移数据成功!")


def _transfer_data_to_sqlite(data_generator, db_conn, table, batch_size=200):
    """
    将数据转存到SQLITE数据库
    :param data_generator: list
    :param db_conn: 数据库连接
    :param table: 需要插入的表
    :return: 无返回
    """
    items = []
    for item in data_generator:
        if len(items) >= batch_size:
            db_conn.insert_batch(table, data=items)
            items = []
        if isinstance(item, tuple) or isinstance(item, list):
            items.append(item)
        else:
            items.append(item.attributes)
    if len(items) > 0:
        db_conn.insert_batch(table, data=items)
    print("转移数据成功!")


def csv_data_generator(csv_path,
                       data_types=None,
                       skip_header=True,
                       add_field=None,
                       auto_inc=True):
    """
    从指定的csv文件读取数据
    :param csv_path: csv文件存储路径
    :param data_types: 指定的数据类型
    :param skip_header: 是否保留第一行
    :param add_field: 特殊处理，增加一列常数值
    :param auto_inc: 插入数据库自增则在头部增加None值
    :return: list
    """
    import csv
    assert os.path.isfile(csv_path)
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        if skip_header:
            next(reader, None)
        for row in reader:
            if add_field:
                row.append(add_field)
            if data_types:
                if len(row) != len(data_types):
                    continue
                row = convert(row, data_types)
            if auto_inc:
                row.insert(0, None)
            yield tuple(row)


def convert(data, data_types):
    """
    将数据转存为指定的格式
    :param data: list
    :param data_types: 如int, float...
    :return: 格式约定后的数据集
    """
    return [data_types[i](data[i])
            if data[i] != 'NULL' else None
            for i in range(len(data))]


def create_if_not_exists_table(table, db_conn):
    """
    创建数据库表
    :param table: 表名（从配置文件中读取SQL）
    :param db_conn: 
    :return: 无返回
    """
    try:
        sql_config = None
        if "sqlite" in db_conn.db_type:
            from config_info.data_config import SQLITE_CONFIGS
            sql_config = SQLITE_CONFIGS
        elif "mysql" in db_conn.db_type:
            from config_info.data_config import MYSQL_SQL_CONFIGS
            sql_config = MYSQL_SQL_CONFIGS
        if not sql_config:
            print("No this operator")
            return
        exists_tables = db_conn.show_tables()
        if table in exists_tables:
            print("表【%s】已经存在！" % table)
            return
        db_conn.execute(sql_config['CREATE'][table])
        print("创建【%s】成功！" % table)
    except Exception as e:
        print("创建【%s】出现异常%s" % (table, e))
    finally:
        db_conn.commit()


# 将文件存储为pickle
def save_as_pickle(file, save_name, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    save_path = output_dir+"/"+save_name
    try:
        with open(save_path, 'wb') as output:
            pickle.dump(file, output)
    except IOError as ioe:
        print("nothing get")
        print(ioe)


# 读取pickle
def load_pickle(file, file_dir=None):
    try:
        if file_dir:
            file = file_dir + '/' + file
        with open(file, 'rb') as pkl_file:
            return pickle.load(pkl_file)
    except IOError as ioe:
        print(ioe)
        print("nothing get")


def delete_specific_files(file_dir,
                          specific_chars="raw_query_data"):
    import os
    assert os.path.isdir(file_dir)
    for file_name in os.listdir(file_dir):
        if specific_chars in file_name:
            the_file = file_dir+"/"+file_name
            print("delete file -- {}".format(the_file))
            os.remove(the_file)
