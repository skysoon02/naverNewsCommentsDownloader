from config import *
from utils import *
from predefined import *

import requests
import json


#채널 URL을 입력 받아서 최신 뉴스 300개의 URL을 가져와 파일로 저장하는 함수
#input channel example: https://media.naver.com/newsflash/001/ElectionNation
def newsListDownloader_by_category(channelName, _categoryURL):
    path = path_newsURL + '/newsList_' + channelName + '_' + _categoryURL.split('/')[-1]
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
    return



def newsListDownloader_by_title(title):
    queryURL = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query=' + title
    try:
        response = requests.get(queryURL, timeout=10)
    except:
        print('Time out from requests.get(): ', queryURL)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    searchResultHTML = soup.find_all('div', class_ = 'info_group') 
    
    return searchResultHTML








#news의 URL을 입력 받아서 comments를 다운받아 json 파일로 저장하는 함수
#https://blog.naver.com/seodaeho91/221273565367
def newsCommentsDownloader(newsURL):
    comments = []
    
    oid = newsURL.split('/')[-2]
    aid = newsURL.split('/')[-1]

    #첫페이지 받아오기
    headers = {
        'Referer': newsURL,
        "User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
    apiURL = 'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&templateId=default_economy&pool=cbox5&_cv=20240116144725&_callback=jQuery331023416264284422983_1705575101314&lang=ko&country=KR&objectId=news'+oid+'%2C'+aid+'&categoryId=&pageSize=20&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=1&initialize=true&followSize=5&userType=&useAltSort=true&replyPageSize=20&sort=reply&includeAllStatus=true&_=1705575101316'
    try:
        response = requests.get(apiURL, headers=headers, timeout=10)
    except:
        print('Time out from requests.get(): ', apiURL)
        return
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
    f.close()




