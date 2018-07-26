#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
from pymongo import MongoClient
#import MySQLdb
import pymysql
import types


def search_mysql(sql):
    statics = []
# 打开数据库连接
    db = pymysql.connect("ip address", "username", "password", "database", charset='utf8')
# 使用cursor()方法获取操作游标 
    db_cursor = db.cursor()

# 使用execute方法执行SQL语句
    try:
#        db_cursor.execute(test_sql)
        db_cursor.execute(sql)

# 使用 fetchone() 方法获取一条数据
        results = db_cursor.fetchall()
#        return results
        if type(results) != type(True):
            for row in results:
                print('record returned by mysql:', row)
#                statics.append(row.encode('UTF-8'))
                if ',' in row[0]:
                    result = row[0].split(',')
                    for res in result:
                        statics.append(res.encode('UTF-8'))
                else:
                    statics.append(row[0].encode('UTF-8'))
        else:
            statics.append(results)
        db_cursor.close()
    except Exception,e:
        print e
        return False
    finally:
        db.close()
    return statics

def conttype_mysql(res):
        conttypes = []
        
        for row in res:
            if ',' in row[0]:
                result = row[0].split(',')
                for res in result:
                    conttypes.append(res.encode('UTF-8'))
            else:
                conttypes.append(row[0].encode('UTF-8'))


def conttype_mongo():
    client=MongoClient('hostname', port)
    db1=client.migu_video
    conttypes = []

    cursor1 = db1.program.distinct("contDisplayType")
    for conttype in cursor1:
        if conttype:
            conttypes.append(conttype.encode('UTF-8'))
        else:
            conttypes.append(conttype)
    return conttypes

def checkConttype(conttypes):
    conttype_todo = []

    print('*' * 60)
    print('mysql res:', conttypes['mysql'])
    print('mongo res:', conttypes['mongo'])
    print('*' * 60)

    if not conttypes['mysql'] or not conttypes['mongo']:
        print('result returned by mysql or mongo is null')

    else:
        for conttype in conttypes['mongo']:
#            print('Debug conttype deling with right now', conttype)
            print(conttype)
            if conttype and conttypes['mysql']:
                if conttype not in conttypes['mysql']:
                    ctype = conttype.decode('UTF-8')
                    try:
                        if int(conttype):
                            print('Conttype to be add into mysql patition:', conttype)
                            conttype_todo.append[conttype]
                    except:
                        print('wrong type', conttype, 'to be ignored')
                else:
                    pass
            else:
                pass
    print('#' * 60)
    print('ContDisplayType to be add to mysql are:', conttype_todo)
    print('#' * 60)
    return conttype_todo

def update_partition(conttypes):
    if conttypes:
        print('ContDisplayType', conttype_todo, 'add to mysql right now')
        for conttype in conttypes:
            sql = 'ALTER TABLE metadata ADD PARTITION (PARTITION p' + conttype + 'VALUES IN (conttype) );'
            search_mysql(sql)

if __name__ == '__main__':
    conttypes = {}
    test_sql = 'show databases;'
    sql = ('select partition_description from information_schema.partitions where table_schema'
          '=schema() and table_name="metadata";')
    
    res = search_mysql(sql)
    print('result returned by mysql in main', res)

    conttypes['mysql'] = conttype_mysql(res)
    conttypes['mongo'] = conttype_mongo()
    
    conttype_todo = checkConttype(conttypes)
    update_partition(conttype_todo)
