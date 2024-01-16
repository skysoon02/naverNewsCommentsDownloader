from config import *

import requests
import json
from multiprocessing import Process, Queue
import os
import time

#new URL을 다운받아서 저장하는 함수
def newsListDownloader(channelName, _categoryURL):
    path = path_newsList + '/newsList_' + channelName + '_' + _categoryURL.split('/')[-1]
    print(path)
    f = open(path, 'w')
    
    categoryURL = _categoryURL

    while True:
        #request로 데이터 받아오기
        response = requests.get(categoryURL)
        if response.status_code != 200:
            return
        
        #news URL들을 저장
        newsURLs = json.loads(response.text)['list']
        for news in newsURLs:
            f.write(news['linkUrl'])

        #종료 or 다음 다운로드위해 설정
        f.write(str(newsURLs))
        print(len(newsURLs))
        if newsURLs[-1]['serviceTimeForMoreApi'] < startTime:   #startDate 이후의 url을 전부 다운로드 받은 경우
            break
        else:
            categoryURL = _categoryURL + '?before=' + newsURLs[-1]['serviceTimeForMoreApi'] #이어서 계속 다운로드하도록 categoryURL 수정
            time.sleep(1)
    
    f.close()





def newsCommentsDownloader():
    pass

def init():
    if not os.path.isdir(path_newsList):
        os.makedirs(path_newsList)

if __name__ == '__main__':
    init()

    #downlaod new news URLS of channels
    processes =[]
    for channel in targetChannelList:                       #각 채널에서
        print(channel)
        for categoryURL in channel['categories']:           #채널의 각 카테고리에서
            process = Process(target=newsListDownloader, args=(channel['name'], categoryURL))
            process.start()
            processes.append(process)

        for process in processes:
            process.join()