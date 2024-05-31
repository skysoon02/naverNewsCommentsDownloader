from config.setting import *

import mysql.connector

class DB:
    def __init__(self):
        self.conn = mysql.connector.connect(**DB_info)
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
            userIdNo char(40)  NOT NULL PRIMARY KEY,
            userInKey char(20),
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
            userIdNo char(40),
            content JSON,
            ctime timestamp DEFAULT CURRENT_TIMESTAMP
        )'''
        cur.execute(query)

        #followTable
        query = '''
        CREATE TABLE IF NOT EXISTS followTable(
            followeeIdNo char(40),
            followerIdNo char(40),
            ctime timestamp DEFAULT CURRENT_TIMESTAMP
        )'''
        cur.execute(query)

        #Encoding
        query = 'SET NAMES utf8mb4'
        cur.execute(query)
        query = 'ALTER DATABASE commentDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci'
        cur.execute(query)

        #query = 'SET global max_allowed_packet=1000000000'
        #cur.execute(query)


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
            
        query = 'desc newsTable'
        cur.execute(query)
        self.printCur(cur)

    
    def deleteAll(self):
        cur = self.conn.cursor()
        query = 'drop table commentTable'
        cur.execute(query)
        query = 'drop table followTable'
        cur.execute(query)
        query = 'drop table newsTable'
        cur.execute(query)
        query = 'drop table userTable'
        cur.execute(query)
    

    def insertNews(self, value):
        cur = self.conn.cursor()
        query='INSERT INTO newsTable (objectId, content) VALUES (%s, %s)'
        cur.executemany(query, value)
        self.conn.commit()
        #self.printCur(cur)
        

    def insertUser(self, value):
        cur = self.conn.cursor()
        query='INSERT INTO userTable (userIdNo, userInKey, content) VALUES (%s, %s, %s)'
        cur.executemany(query, value)
        self.conn.commit()
        #self.printCur(cur)
        

    def insertComment(self, value):
        cur = self.conn.cursor()
        query='INSERT INTO commentTable (commentNo, parentCommentNo, objectId, userIdNo, content) VALUES (%s, %s, %s, %s, %s)'
        cur.executemany(query, value)
        self.conn.commit()
        #self.printCur(cur)
        

    def insertFollow(self, value):
        cur = self.conn.cursor()
        query='INSERT INTO followTable (followeeIdNo, followerIdNo) VALUES (%s, %s)'
        cur.executemany(query, value)
        self.conn.commit()
        #self.printCur(cur)


    def searchNews(self, id):
        cur = self.conn.cursor()
        query=f'SELECT EXISTS(SELECT 1 FROM newsTable WHERE objectId = "{id}") as cnt'
        cur.execute(query)
        return True if cur.fetchall()[0][0]==1 else False
    

    def searchComment(self, id):
        cur = self.conn.cursor()
        query=f'SELECT EXISTS(SELECT 1 FROM commentTable WHERE commentNo = "{id}") as cnt'
        cur.execute(query)
        return True if cur.fetchall()[0][0]==1 else False
    
    
    def searchUser(self, id):
        cur = self.conn.cursor()
        query=f'SELECT EXISTS(SELECT 1 FROM userTable WHERE userIdNo = "{id}") as cnt'
        cur.execute(query)
        return True if cur.fetchall()[0][0]==1 else False

