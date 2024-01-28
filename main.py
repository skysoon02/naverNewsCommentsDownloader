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



#predefined.py의 targetChannelList에 있는 채널들의 카테고리들에서 뉴스들의 URL 다운로드
def newsListDownloader_by_category_MultiProcessing():
    with Pool(processes=number_of_process) as pool:
        return pool.map(newsListDownloader_by_category, (((channel['name'], categoryURL) for categoryURL in channel['categories']) for channel in targetChannelList))


#new의 title을 입력 받아서 전처리 후 
def newsTitleToURL(news):
    title = news[0]
    channelID = news[1]
    if titleFilter(title, channelID)==True:
        beautifiedTitle = titleBeautifier(title)
        searchResultHTML = newsListDownloader_by_title(beautifiedTitle)
        if searchResultHTML == []:    #검색 결과가 하나도 없는 경우
            print('Fail to download: ', title)
            return None
        return getPreciseNews(searchResultHTML, beautifiedTitle, channelID)
    return None


def newsTitleToURL_MultiProcessing(newsList):
    with Pool(processes=number_of_process) as pool:
        return pool.map(newsTitleToURL, newsList)

    #return result



#news의 URL들이 주어지면 멀티프로세싱으로 다운로드
def newsCommentsDownloader_MultiProcessing(newsURLs):
    with Pool(processes=number_of_process) as pool:
        return pool.map(newsCommentsDownloader, newsURLs)
    


def main():
    init()
    newsList = newsListReader() #[title, channel]들로 이루어진 리스트
    newsURLs = newsTitleToURL_MultiProcessing(newsList)
    newsURLs = [newsURL for newsURL in newsURLs if newsURL != None]   #리스트의 None 제거
    newsCommentsDownloader_MultiProcessing(newsURLs)



def debug():
    print(getPreciseNews("韓 '지금보다 더 최선 다할 것'", 448))
    return
    print(newsListReader())
    print(titleFilter('asdf[풀영상] asdf', 214))
    print(titleBeautifier('asdf|asdf/asdf(asdf)[asdf](asdf)[asdf] | asdf / asdf 2023'))



if __name__ == '__main__':
    #debug()
    main()