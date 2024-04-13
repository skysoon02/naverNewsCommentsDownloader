from config.setting import *

import pymysql

def db_connect():
    conn = pymysql.connect(**DB_info)
    return conn


def db_init():
    conn = db_connect()
    cur = conn.cursor()
    
    #newsTable
    sql = '''
    CREATE TABLE IF NOT EXISTS newsTable(
        objectId char(20) NOT NULL PRIMARY KEY,
        content JSON,
        ctime timestamp DEFAULT CURRENT_TIMESTAMP
    )'''
    cur.execute(sql)

    #userTable
    sql = '''
    CREATE TABLE IF NOT EXISTS userTable(
        userIdNo char(5)  NOT NULL PRIMARY KEY,
        userInkey bigint,
        content JSON,
        ctime timestamp DEFAULT CURRENT_TIMESTAMP
    )'''
    cur.execute(sql)

    #commentTable
    sql = '''
    CREATE TABLE IF NOT EXISTS commentTable(
        commentNo bigint NOT NULL PRIMARY KEY,
        parentCommentNo bigint,
        objectId char(20),
        userIdNo char(5),
        content JSON,
        ctime timestamp DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parentCommentNo) REFERENCES commentTable(commentNo)
    )'''
    cur.execute(sql)

    #followTable
    sql = '''
    CREATE TABLE IF NOT EXISTS followTable(
        followerIdNo char(5),
        followeeIdNo char(5),
        ctime timestamp DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (followerIdNo) REFERENCES userTable(userIdNo),
        FOREIGN KEY (followeeIdNo) REFERENCES userTable(userIdNo)
    )'''
    cur.execute(sql)


    conn.close()


def db_check():
    conn = db_connect()
    cur = conn.cursor()

    sql = 'show databases'
    cur.execute(sql)
    for r in cur:
        print(r)

    sql = 'show table status'
    cur.execute(sql)
    for r in cur:
        print(r)
        
    sql = 'desc commentTable'
    cur.execute(sql)
    for r in cur:
        print(r)

