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
            content longtext,
            ctime timestamp DEFAULT CURRENT_TIMESTAMP
        )'''
        cur.execute(query)

        #userTable
        query = '''
        CREATE TABLE IF NOT EXISTS userTable(
            userIdNo char(10)  NOT NULL PRIMARY KEY,
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
            userIdNo char(10),
            content JSON,
            ctime timestamp DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parentCommentNo) REFERENCES commentTable(commentNo)
        )'''
        cur.execute(query)

        #followTable
        query = '''
        CREATE TABLE IF NOT EXISTS followTable(
            followerIdNo char(10),
            followeeIdNo char(10),
            ctime timestamp DEFAULT CURRENT_TIMESTAMP
        )'''
        '''
            FOREIGN KEY (followerIdNo) REFERENCES userTable(userIdNo),
            FOREIGN KEY (followeeIdNo) REFERENCES userTable(userIdNo)
        '''
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


    def insertNews(self, value):
        cur = self.conn.cursor()
        query=f'INSERT INTO newsTable VALUES (%s %s)'
        cur.executemany(query, value)
        self.conn.commit()
        #self.printCur(cur)
        

    def insertUser(self, value):
        cur = self.conn.cursor()
        query=f'INSERT INTO userTable VALUES (%s %s %s)'
        cur.executemany(query, value)
        self.conn.commit()
        #self.printCur(cur)
        

    def insertComment(self, value):
        cur = self.conn.cursor()
        query=f'INSERT INTO commentTable VALUES (%s %s %s %s %s)'
        cur.executemany(query, value)
        self.conn.commit()
        #self.printCur(cur)
        

    def insertFollow(self, value):
        cur = self.conn.cursor()
        query=f'INSERT INTO followTable VALUES (%s %s)'
        cur.executemany(query, value)
        self.conn.commit()
        #self.printCur(cur)


    def search(self, table, id):
        cur = self.conn.cursor()
        query=f'SELECT * FROM {table} WHERE {id}'
        cur.execute(query)
        self.printCur(cur)

