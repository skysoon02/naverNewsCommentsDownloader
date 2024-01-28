from config import *
from downloaders import *
from utils import *

import requests
import json
from multiprocessing import Pool
import os


def init():
    if not os.path.isdir(path_newsURL):
        os.makedirs(path_newsURL)
    if not os.path.isdir(path_comment):
        os.makedirs(path_comment)


'''
#predefined.py의 targetChannelList에 있는 채널들의 카테고리들에서 뉴스들의 URL 다운로드
def newsListDownloader_by_category_MultiProcessing():
    with Pool(processes=number_of_process) as pool:
        return pool.map(newsListDownloader_by_category, (((channel['name'], categoryURL) for categoryURL in channel['categories']) for channel in targetChannelList))
'''


#new의 title을 입력 받아서 전처리 후 
def newsTitleToURL(news):
    title = news[0]
    channelID = news[1]
    if titleFilter(title, channelID)==True:
        beautifiedTitle = titleBeautifier(title)
        searchResultHTML = serachNaverNews(beautifiedTitle)
        return getPreciseNews(searchResultHTML, beautifiedTitle, channelID)
    return None


def newsTitleToURL_MultiProcessing(newsList):
    with Pool(processes=number_of_process) as pool:
        return pool.map(newsTitleToURL, newsList)

    #return result



#news의 URL들이 주어지면 멀티프로세싱으로 다운로드
def downloadNewsComments_MultiProcessing(newsURLs):
    with Pool(processes=number_of_process) as pool:
        return pool.map(downloadNewsComments, newsURLs)
    
















def main():
    init()
    newsList = newsListReader() #[title, channel]들로 이루어진 리스트
    newsURLs = newsTitleToURL_MultiProcessing(newsList)
    newsURLs = [newsURL for newsURL in newsURLs if newsURL != None]   #리스트의 None 제거
    downloadNewsComments_MultiProcessing(newsURLs)



def debug():
    print(searchParticularNews(titleBeautifier('대통령실 사퇴 요구에 한동훈 비대위원장이 직접 밝힌 입장'), 1))
    print(searchSeveralNewses(titleBeautifier('대통령실 사퇴 요구에 한동훈 비대위원장이 직접 밝힌 입장'), 50))
    downloadNewsContent('https://n.news.naver.com/article/052/0001740291')
    return
    downloadNewsContent('https://n.news.naver.com/article/656/0000077835')
    return
    downloadNewsComments('https://n.news.naver.com/article/052/0001740291')
    print(searchSeveralNewses(titleBeautifier('대통령실 사퇴 요구에 한동훈 비대위원장이 직접 밝힌 입장'), 50))
    print(searchParticularNews("韓 '지금보다 더 최선 다할 것'", 448))
    print(newsListReader())
    print(titleFilter('asdf[풀영상] asdf', 214))
    print(titleBeautifier('asdf|asdf/asdf(asdf)[asdf](asdf)[asdf] | asdf / asdf 2023'))



if __name__ == '__main__':
    debug()
    #main()