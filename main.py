from config import *

import requests
import json
from bs4 import BeautifulSoup
from multiprocessing import Process
import os



def init():
    if not os.path.isdir(path_newsList):
        os.makedirs(path_newsList)



#news URL을 다운받아서 저장하는 함수
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
            f.write(news['linkUrl']+'\n')

        #종료 or 다음 다운로드위해 설정
        if newsURLs == [] or newsURLs[-1]['serviceTimeForMoreApi'] < startTime:   #300개를 다운로드 받아서 더 이상 받을 수 없는 경우 or startDate 이후의 url을 전부 다운로드 받은 경우
            break
        else:
            categoryURL = _categoryURL + '?before=' + newsURLs[-1]['serviceTimeForMoreApi'] #이어서 계속 다운로드하도록 categoryURL 수정]
    
    f.close()



#news의 comments를 다운받아서 저장하는 함수
#https://blog.naver.com/seodaeho91/221273565367
def newsCommentsDownloader(newsURLs):
    for url in newsURLs:
        oid = url.split('/')[-2]
        aid = url.split('/')[-1]
        page = 1
        #apiURL = "https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_society&pool=cbox5&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country=&objectId=news"+oid+"%2C"+aid+"&categoryId=&pageSize=20&indexSize=10&groupId=&listType=OBJECT&pageType=more&page="+str(page)+"&refresh=false&sort=FAVORITE"
        apiURL = 'https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_economy&pool=cbox5&_callback=jQuery33107462323356263885_1705410942353&lang=ko&country=KR&objectId=news'+oid+'%2C'+aid+'&pageSize=400&indexSize=10&pageType=more&page='+str(page)+'&sort=new'
        headers = {
            'Referer': url,
            "User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        }

        response = requests.get(apiURL, headers=headers)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup)
        #print(response.request.headers)


def main():
    init()

    newsCommentsDownloader(['https://n.news.naver.com/article/comment/001/0014445643'])

    return

    '''
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
    '''

    #downlaod comments of channels
    toDownloadNewsURLs = []
    for channel in targetChannelList:                       #각 채널에서
        print(channel)
        for categoryURL in channel['categories']:           #채널의 각 카테고리에서
            path = path_newsList + '/newsList_' + channel['name'] + '_' + categoryURL.split('/')[-1]
            print(path)
            f = open(path, 'r')
            lines = f.readlines()
            for line in lines:
                toDownloadNewsURLs.append(line.replace('/article', '/article/comment').rstrip('\n'))
    
    processes =[]
    for i in range(number_of_process):
        process = Process(target=newsCommentsDownloader, args=(toDownloadNewsURLs[i*len(toDownloadNewsURLs)//number_of_process : (i+1)*len(toDownloadNewsURLs)//number_of_process], ))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()


if __name__ == '__main__':
    main()