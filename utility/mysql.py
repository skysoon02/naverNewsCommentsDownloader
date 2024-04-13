from config.setting import *

import pymysql

class DB:
    def __init__(self, ):
        self.conn = pymysql.connect(**DB_info)
        cur = self.conn.cursor()
        
        #newsTable
        query = '''
        CREATE TABLE IF NOT EXISTS newsTable(
            objectId char(20) NOT NULL PRIMARY KEY,
            content JSON,
            ctime timestamp DEFAULT CURRENT_TIMESTAMP
        )'''
        cur.execute(query)

        #userTable
        query = '''
        CREATE TABLE IF NOT EXISTS userTable(
            userIdNo char(5)  NOT NULL PRIMARY KEY,
            userInkey bigint,
            content JSON,
            ctime timestamp DEFAULT CURRENT_TIMESTAMP
        )'''
        cur.execute(query)

        #commentTable
        query = '''
        CREATE TABLE IF NOT EXISTS commentTable(
            commentNo bigint NOT NULL PRIMARY KEY,
            parentCommentNo bigint,
            objectId char(20),
            userIdNo char(5),
            content JSON,
            ctime timestamp DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parentCommentNo) REFERENCES commentTable(commentNo)
        )'''
        cur.execute(query)

        #followTable
        query = '''
        CREATE TABLE IF NOT EXISTS followTable(
            followerIdNo char(5),
            followeeIdNo char(5),
            ctime timestamp DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (followerIdNo) REFERENCES userTable(userIdNo),
            FOREIGN KEY (followeeIdNo) REFERENCES userTable(userIdNo)
        )'''
        cur.execute(query)


    def printCur(self, cur):
        res = cur.fetchall()
        print([d[0] for d in cur.description])
        for r in res:
            print(r)
        print('')


    def check(self):
        cur = self.conn.cursor()

        query = 'show databases'
        cur.execute(query)
        self.printCur(cur)

        query = 'show table status'
        cur.execute(query)
        self.printCur(cur)
            
        query = 'desc commentTable'
        cur.execute(query)
        self.printCur(cur)


    def insert(self, table, value):
        cur = self.conn.cursor()
        query=f'INSERT INTO {table} VALUES ({value})'
        print(query)
        return
        cur.execute(query)
        self.printCur(cur)


    def search(self, table, id):
        cur = self.conn.cursor()
        query=f'SELECT * FROM {table} WHERE {id}'
        cur.execute(query)
        self.printCur(cur)

