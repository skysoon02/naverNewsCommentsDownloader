from config import *
from predefined import *
from downloaders import *

import requests
from bs4 import BeautifulSoup
import re
import os


#path_newsTitle에서 네이버 뉴스 title과 채널들이 저장되어 있는 파일을 읽어와서 list로 반환하는 함수
#format
#title              channel
#KAIST duck...      TV조선
#Korean birth...    MBC
def newsListReader():
    newsList = []

    for file_name in os.listdir(path_newsTitle):
        f = open(path_newsTitle+'/'+file_name, 'r', encoding='utf-8-sig')
        lines = f.readlines()
        for line in lines:
            title = line.split('\t')[0]
            channelID = channelNameToID[line.split('\t')[1].rstrip('\n')]
            newsList.append([title, channelID])

    return newsList



#YTN: 다시보기
#SBS: 없는 듯
#KBS: [풀영상] <- 근데 거의 안 올라옴
#MBC: [풀영상]
#JTBC: [다시보기]
#TV조선: [TV CHOSUN LIVE]
#채널A: [다시보기]
def titleFilter(title, channelID):
    if channelID==1:        #YTN
        if '다시보기' in title:
            return False

    elif channelID==55:     #SBS
        pass

    elif channelID==56:     #KBS
        if title.startswith('[풀영상]'):
            return False
        
    elif channelID==214:    #MBC
        if '[풀영상]' in title:
            return False
        
    elif channelID==437:    #JTBC
        if title.startswith('[다시보기]'):
            return False
    
    elif channelID==448:    #TV조선
        if title.startswith('[TV CHOSUN LIVE]'):
            return False
    
    elif channelID==449:    #채널A
        if title.startswith('[다시보기]'):
            return False

    return True



#YTN: [*]제거, postfix의 / YTN 제거
#SBS: [*], (*) 제거, postfix의 / SBS 제거
#KBS: [*]제거, postfix의 / KBS 20XX.XX.XX 제거
#MBC: [*], (*) 제거
#JTBC: [*]제거, postfix의 /*, |* 제거
#TV조선: [*]제거, postfix의 /* 제거
#채널A: [*]제거, postfix의 /*, |* 제거
def titleBeautifier(title0):
    title1 = re.sub(r"\(.*\)|\[.*\]|/.*|\|.*", "", title0)  #()제거, []제거, \제거, |제거
    title2 = re.sub("\"", "'", title1)          #큰따옴표를 작은따옴표로 변경. 네이버 검색할 때 별 문제 안 생기는 추정 됨
    title3 = re.sub(" ", "+", title2)           #공백을 더하기로 변경. 네이버 URL방식을 따름.
    return title3
    


#네이버 뉴스의 title을 입력 받아서 해당 뉴스의 URL을 반환
#input title example: 대통령실 사퇴 요구에 한동훈 비대위원장이 직접 밝힌 입장
#return title example: 
def getPreciseNews(searchResultHTMLs, title, channelID):
    videoURLs = []
    channelName = channelIDToName[channelID]
    for searchResultHTML in searchResultHTMLs:
        if channelName in searchResultHTML.contents[1].contents and '네이버뉴스' in searchResultHTML.contents[3].contents:
            videoURLs.append(searchResultHTML.contents[3].get('href'))

    if len(videoURLs) != 1: #일치하는 검색 결과가 정확히 한 개가 아닌 경우
        print('There is not exactly one result:', len(videoURLs))
        return
        
    videoURL = videoURLs[0].split('?')[0]   #'?sid=' 제거
    oidIndex = videoURL.find('oid')+4
    aidIndex = videoURL.find('aid')+4

    return 'https://n.news.naver.com/article/' + videoURL[oidIndex: oidIndex+3] + '/' + videoURL[aidIndex:]


#네이버 뉴스의 title을 입력 받아서 네이버에 검색되는 네이버 뉴스의 URL들을 반환
def getSeveralNewses(searchResultHTMLs, title, number_of_news):
    videoURLs = []
    for searchResultHTML in searchResultHTMLs:
        if '네이버뉴스' in searchResultHTML.contents[3].contents:
            videoURLs.append(searchResultHTML.contents[3].get('href'))

    if len(videoURLs) != 1: #일치하는 검색 결과가 정확히 한 개가 아닌 경우
        print('There is not exactly one result:', len(videoURLs))
        return
    
    returnURLs = []
    for videoURL in videoURLs:
        videoURL_ = videoURL.split('?')[0]   #'?sid=' 제거
        oidIndex = videoURL_.find('oid')+4
        aidIndex = videoURL_.find('aid')+4
        returnURLs.append('https://n.news.naver.com/article/' + videoURL_[oidIndex: oidIndex+3] + '/' + videoURL_[aidIndex:])

    return returnURLs

