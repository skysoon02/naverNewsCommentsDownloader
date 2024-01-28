from config import *
from predefined import *

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


#풀영상이나 다시보기 등 네이버 뉴스에 없을만한 영상 제목들을 거르는 함수
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


#특수문자나 날짜, 채널 이름 등을 제거하는 함수
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
    
