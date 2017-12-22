#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/11/15 14:18
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com

import re


class DbConn(object):
    """
    简单的连接数据库操作
    """
    def __init__(self, db_type):
        db_type = str(db_type).lower()
        self.db_type = db_type
        if "hive" in db_type:
            from impala.dbapi import connect as hive_connect
            from config_info.db_config import hive_config_set
            hive_config = hive_config_set[db_type]
            self.conn = hive_connect(host=hive_config['host'],
                                     port=hive_config['port'],
                                     user=hive_config['user'],
                                     auth_mechanism=hive_config['auth_mechanism'])
            print("hive server connected successfully!")
        elif "mysql" in db_type:
            import pymysql
            from config_info.db_config import mysql_config_set
            mysql_config = mysql_config_set[db_type]
            self.conn = pymysql.connect(host=mysql_config['host'], port=mysql_config['port'],
                                        user=mysql_config['user'], passwd=mysql_config['password'],
                                        db=mysql_config['database'], charset=mysql_config['charset'],
                                        cursorclass=pymysql.cursors.DictCursor)
        else:
            import sqlite3
            from config_info.db_config import sqlite_config_set
            self.conn = sqlite3.connect(sqlite_config_set['database'])
            self.cursor = self.conn.cursor()

    def query(self, sql):
        try:
            if "sqlite" in self.db_type:
                result = self.conn.execute(sql)
                return result.fetchall()
            elif "hive" in self.db_type:
                with self.conn.cursor() as cursor:
                    cursor.execute("SET mapred.job.queue.name = ai")
                    cursor.execute(sql)
                    result = cursor.fetchall()
                return result
            else:
                with self.conn.cursor() as cursor:
                    cursor.execute(sql)
                    result = cursor.fetchall()
                return result
        except Exception as e:
            print(e)
            return None

    def execute(self, sql):
        try:
            if "sqlite" in self.db_type:
                with self.conn as conn:
                    conn.execute(sql)
            else:
                with self.conn.cursor() as cursor:
                    cursor.execute(sql)
        except Exception as e:
            print(e)
            return None

    def insert_batch(self, tb_name, data=None):
        assert isinstance(data, list) or isinstance(data, tuple)
        assert len(data) > 0
        if "sqlite" in self.db_type:
            sql = "insert into " + tb_name + " values ("
            try:
                tmp = data[0]
                if isinstance(tmp, list) or isinstance(tmp, tuple):
                    sql += "?," * (len(tmp) - 1) + "?)"
                else:
                    sql += "?)"
                    data = [(x,) for x in data]
                self.cursor.executemany(sql, data)
            except Exception as e:
                print(e)
                self.conn.rollback()
                print("insert failed")
                print(e.with_traceback(tb_name))

    def insert_one(self, tb_name, data=None):
        sql = "insert into " + tb_name + " values ("
        try:
            if isinstance(data, list) or isinstance(data, tuple):
                sql += "?," * (len(data) - 1) + "?)"
            else:
                sql += "?)"
                data = (data,)
            self.cursor.execute(sql, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print("insert failed")
            print(e.with_traceback(tb_name))

    def insert_one_with_fields(self, tb_name, fields, values=None):
        sql = "insert into {} {} values {}"
        try:
            fields_str = repr(tuple(fields))
            fields_str = re.sub("\'|\"", "", fields_str)
            values_str = repr(tuple(values))
            values_str = re.sub(r"\bNone\b", 'NULL', values_str)
            data_sql = sql.format(tb_name, fields_str, values_str)
            self.cursor.execute(data_sql)
        except Exception as e:
            self.conn.rollback()
            print("insert failed")
            print(e.with_traceback(tb_name))

    def close(self):
        if self.conn:
            self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def show_tables(self):
        from app_utils.log_utils import flatten
        if "sqlite" in self.db_type:
            tables = self.query("SELECT name FROM sqlite_master WHERE type='table';")
        else:
            tables = self.query(sql="SHOW TABLES;")
        return flatten(tables)

# conn.cursor().execute("SELECT count(1) FROM yoins.e_category_filter LIMIT 10")
