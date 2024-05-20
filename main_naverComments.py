from config.setting import *
from download.api import *
from download.search import *
from utility.mysql import *
from utility.utils import *
from utility.tsv import *

import requests
import json
from multiprocessing import Pool
import os
import time
import csv


db = None


#news를 다운로드하기 위한 process
def downloadNewsContent_process(newsURL):
    res = downloadNewsContent(newsURL)
    oid = newsURL.split('/')[-2]    #채널 ID
    aid = newsURL.split('/')[-1]    #뉴스 ID
    objectId = oid + ',' + aid
    return (objectId, res)


#comments를 다운로드하기 위한 process
def downloadNewsComments_process(newsURL):
    return downloadNewsComments(newsURL)
    

#user 를 다운로드하기 위한 process
def downloadUsers_process(ID):
    res = downloadUserContent(ID, 'commentID')



def main():
    news = {}
    comments = {}

    #0. Get news urls
    newsURLs = []
    with open(path_newsURL+'/newsList', 'r', encoding="UTF-8-sig") as file:
        rea = csv.reader(file, delimiter='\t')
        for row in rea:
            newsURLs.append(row[0])
    news = set(newsURLs)

    while True:
        #1. Save news at DB (enable to skip)
        res = []
        with Pool(processes=number_of_process) as pool:
            res = pool.map(downloadNewsContent_process, newsURLs)
        db.insertNews(res)
        
        return
        #2. Download News Comments
        res = []
        with Pool(processes=number_of_process) as pool:
            res = pool.map(downloadNewsComments_process, newsURLs)
        
        #3. 유저 추출
        users = {}  #Dictionary to deduplicate
        for commentList in res:
            for comment in commentList:
                commentNo = comment['commentNo']
                userIdNo = comment['userIdNo']
                users[userIdNo] = commentNo

        #3-1. DB에서 유저 중복 제거

        #3-2. 유저 정보 다운로드
        with Pool(processes=number_of_process) as pool:
            res = pool.map(downloadUsers_process, users.keys())

        #3-2. 유저 팔로워 팔로잉 BFS


        #4. 유저가 작성한 Comments 다운로드
        user

        #5. Comments DB 저장

        #5-1. 



def debug():
    db = DB()
    db.check()
    return


if __name__ == '__main__':
    main()
    #debug()