from config.setting import *
from download.api import *
from download.search import *
from utility.utils import *
from utility.tsv import *

import requests
import json
from multiprocessing import Pool
import os
import time
import csv


def init():
    if not os.path.isdir(path_newsURL):
        os.makedirs(path_newsURL)
    if not os.path.isdir(path_comment):
        os.makedirs(path_comment)
    if not os.path.isdir(path_content):
        os.makedirs(path_content)



#title로 URL을 검색하기 위한 process
def searchNewsURLs_process(news):
    title = news[0]
    channelID = news[1]
    videoID = news[2]
    if titleFilter(title, channelID)==True:
        beautifiedTitle = titleBeautifier(title)
        return searchParticularNews(beautifiedTitle, channelID, videoID)
    return None


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



#newsTitle 디렉토리의 (유튜브 뉴스 제목, 뉴스 채널 이름, 유튜브 영상 ID)에서 네이버 뉴스의 content와 comment를 다운로드 함
def main():
    init()

    #youtube title -> naver news urls
    newsList = newsListReader() #[title, channelName, videoID]들로 이루어진 리스트

    newsURLs = []
    for news in newsList:
        res = searchNewsURLs_process(news)
        newsURLs.append(res)
        if res != None:
            with open(path_newsURL+'/newsList', 'a+', encoding="UTF-8-sig") as file:
                for i in res:
                    file.write('\t'.join(i))
                    file.write('\n')
        time.sleep(6)
    
    newsURLs = []
    with open(path_newsURL+'/newsList', 'r', encoding="UTF-8-sig") as file:
        r = csv.reader(file, delimiter='\t')
        for row in r:
            newsURLs.append((row[0], row[1]))

    with Pool(processes=number_of_process) as pool:
        pool.map(downloadNewsComments_process, newsURLs)
    
    with Pool(processes=number_of_process) as pool:
        pool.map(downloadNewsContent_process, newsURLs)


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