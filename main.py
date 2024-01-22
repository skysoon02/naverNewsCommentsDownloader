from config import *

import requests
import json
from multiprocessing import Process
import os
from bs4 import BeautifulSoup



def init():
    if not os.path.isdir(path_newsList):
        os.makedirs(path_newsList)
    if not os.path.isdir(path_comment):
        os.makedirs(path_comment)


def titleToURL(title):
    queryURL = 'https://search.naver.com/search.naver?where=video&sm=tab_jum&query=' + title
    try:
        response = requests.get(queryURL, timeout=10)
    except:
        print('Time out from requests.get(): ', queryURL)
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    videoHTML = soup.find('a', string = '네이버 뉴스').find_parent('li')
    videoURL = videoHTML.find(class_='thumb_area').find('a').get('href')
    print(videoURL)

    oidIndex = videoURL.find('oid')+4
    aidIndex = videoURL.find('aid')+4

    return 'https://n.news.naver.com/article/' + videoURL[oidIndex: oidIndex+3] + '/' + videoURL[aidIndex:]
    
    print(a)



#news URL을 다운받아서 저장하는 함수
def newsListDownloader(channelName, _categoryURL):
    path = path_newsList + '/newsList_' + channelName + '_' + _categoryURL.split('/')[-1]
    print(path)
    f = open(path, 'w')
    
    categoryURL = _categoryURL

    while True:
        #request로 데이터 받아오기
        try:
            response = requests.get(categoryURL, timeout=10)
        except:
            print('Time out from requests.get(): ', categoryURL)
            continue

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
        comments = []
        
        oid = url.split('/')[-2]
        aid = url.split('/')[-1]

        #첫페이지 받아오기
        headers = {
            'Referer': url,
            "User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        }
        apiURL = 'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&templateId=default_economy&pool=cbox5&_cv=20240116144725&_callback=jQuery331023416264284422983_1705575101314&lang=ko&country=KR&objectId=news'+oid+'%2C'+aid+'&categoryId=&pageSize=20&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=1&initialize=true&followSize=5&userType=&useAltSort=true&replyPageSize=20&sort=reply&includeAllStatus=true&_=1705575101316'
        try:
            response = requests.get(apiURL, headers=headers, timeout=10)
        except:
            print('Time out from requests.get(): ', apiURL)
            continue
        if response.status_code != 200:
            return
        
        startIdx = response.text.find('{')
        resDict = json.loads(response.text[startIdx:-2])
        comments.append(resDict['result']['commentList'])

        for page in range(2, resDict['result']['pageModel']['totalPages']+1):
            apiURL = 'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&templateId=default_economy&pool=cbox5&_cv=20240116144725&_callback=jQuery331023416264284422983_1705575101314&lang=ko&country=KR&objectId=news'+oid+'%2C'+aid+'&categoryId=&pageSize=20&indexSize=10&groupId=&listType=OBJECT&pageType=more&page='+str(page)+'&currentPage='+str(page-1)+'&refresh=false&sort=REPLY&current=814607337766518790&prev=814571801492324559&moreParam.direction=next&moreParam.prev='+str(resDict['result']['morePage']['prev'])+'&moreParam.next='+str(resDict['result']['morePage']['next'])+'&includeAllStatus=true&_=1705575101318'
            try:
                response = requests.get(apiURL, headers=headers, timeout=10)
            except:
                print('Time out from requests.get(): ', apiURL)
                continue
            if response.status_code != 200:
                return
        
            startIdx = response.text.find('{')
            resDict = json.loads(response.text[startIdx:-2])
            comments.append(resDict['result']['commentList'])
        
        f = open(path_comment+'/'+oid+'_'+aid, 'w', encoding="UTF-8-sig")
        json.dump(comments, f, ensure_ascii=False)
#        f.write(str(comments))
        f.close()
        print(comments)
        
        

def main():
    init()
    URL = titleToURL("을씨년스런 분위기...줄폐업에 자영업자들 '곡소리'")
    

    newsCommentsDownloader([URL])

    return


    '''
    #downlaod new news URLS of channels
    processes = []
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
                toDownloadNewsURLs.append(line.rstrip('\n'))
    
    processes =[]
    for i in range(number_of_process):
        process = Process(target=newsCommentsDownloader, args=(toDownloadNewsURLs[i*len(toDownloadNewsURLs)//number_of_process : (i+1)*len(toDownloadNewsURLs)//number_of_process], ))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()


if __name__ == '__main__':
    main()