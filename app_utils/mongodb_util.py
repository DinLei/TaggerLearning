#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2017/11/8 14:38
# @Author  : BigDin
# @Contact : dinglei_1107@outlook.com

from pymongo import MongoClient


class MongodbOperation:
    def __init__(self, host=None, port=27017):
        self._host = None
        self._port = None

        if host:
            self.host = host
        if port:
            self.port = port

        self._conn = self._mongodb_conn()

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, host):
        self._host = host

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port):
        self._port = port

    def _mongodb_conn(self):
        if self.host and self.port:
            return MongoClient(host=self.host, port=self.port)
        else:
            return None

    @property
    def conn(self):
        return self._conn

    def mongodb_conn(self, host=None, port=27017):
        if host == self.host and port == self.port:
            return self.conn
        elif host and port:
            return MongoClient(host=host, port=port)
        else:
            return self._mongodb_conn()

    def use_database(self, database):
        db = None
        try:
            db = self.conn[database]
        except Exception as e:
            print(e)
        finally:
            return db

    def use_collection(self, database, table):
        collection = None
        try:
            collection = self.conn[database][table]
        except Exception as e:
            print(e)
        finally:
            return collection
