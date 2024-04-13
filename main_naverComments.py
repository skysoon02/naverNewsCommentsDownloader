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




#comments를 다운로드하기 위한 process
def downloadNewsComments_process(news):
    newsURL = news[0]
    videoID = news[1]
    oid = newsURL.split('/')[-2]    #채널 ID
    aid = newsURL.split('/')[-1]    #뉴스 ID
    res = downloadNewsComments(newsURL)
    writeTsv(path_comment+'/'+videoID+'_'+oid+'_'+aid, res)


#contents를 다운로드하기 위한 process
def downloadNewsContent_process(news):
    newsURL = news[0]
    videoID = news[1]
    oid = newsURL.split('/')[-2]    #채널 ID
    aid = newsURL.split('/')[-1]    #뉴스 ID
    res = downloadNewsContent(newsURL)
    writeTsv(path_content+'/'+videoID+'_'+oid+'_'+aid, res)



def main():
    news = {}
    comments = {}
    users = {}

    newsURLs = []
    with open(path_newsURL+'/newsList', 'r', encoding="UTF-8-sig") as file:
        rea = csv.reader(file, delimiter='\t')
        for row in rea:
            newsURLs.append(row[0])
    news = set(newsURLs)

    while True:
        #Download news
        with Pool(processes=number_of_process) as pool:
            pool.map(downloadNewsComments_process, newsURLs)

        #Save news
        


def debug():
    db = DB()
    db.check()
    #print(downloadUserFollowers(822456347902607549, 'commentID'))
    #print(downloadUserComments(822449671979925557, 'commentID'))
    #print(downloadUserID(822449671979925557))
    #print(titleBeautifier("“수도권 공천에 국민 의견 80% 반영”…한 “의원 250명으로 축소” [9시 뉴스] (2024.01.02) / KBS  2024.01.16."))
    return


if __name__ == '__main__':
    #main()
    debug()