from config import *
from predefined import *

import requests
from bs4 import BeautifulSoup
import json


'''
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
'''


#네이버 뉴스에 제목으로 검색한 결과(HTML 리스트)를 반환하는 함수
def serachNaverNews(title):
    queryURL = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query=' + title
    try:
        response = requests.get(queryURL, timeout=10)
    except:
        print('Time out from requests.get(): ', queryURL)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    searchResultHTML = soup.find_all('div', class_ = 'info_group') 
    
    return searchResultHTML


#네이버 뉴스의 title을 입력 받아서 해당 뉴스의 URL을 반환
#input title example: 대통령실 사퇴 요구에 한동훈 비대위원장이 직접 밝힌 입장
#return title example: 
def searchParticularNews(title, channelID):
    queryURL = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query=' + '"' + title + '"' 
    try:
        response = requests.get(queryURL, timeout=10)
    except:
        print('Time out from requests.get(): ', queryURL)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    searchResultHTMLs = soup.find_all('div', class_ = 'info_group') 
    if searchResultHTMLs == []:    #검색 결과가 하나도 없는 경우
        print('Fail to download: ', title)
        return None
    
    newsURLs = []
    channelName = channelIDToName[channelID]
    for searchResultHTML in searchResultHTMLs:
        if channelName in searchResultHTML.contents[1].contents and '네이버뉴스' in searchResultHTML.contents[3].contents:
            newsURLs.append(searchResultHTML.contents[3].get('href'))

    if len(newsURLs) != 1: #일치하는 검색 결과가 정확히 한 개가 아닌 경우
        print('There is not exactly one result:', len(newsURLs))
        return
        
    newsURL = newsURLs[0].split('?')[0]   #'?sid=' 제거
    oidIndex = newsURL.find('oid')+4
    aidIndex = newsURL.find('aid')+4

    return 'https://n.news.naver.com/article/' + newsURL[oidIndex: oidIndex+3] + '/' + newsURL[aidIndex:]


#네이버 뉴스의 title을 입력 받아서 네이버에 검색되는 네이버 뉴스의 URL들을 반환
def searchSeveralNewses(title, number_of_news):
    newsURLs = []   #반환할 URL을 저장하는 변수
    page=0          #요청할 네이버 검색 결과의 페이지
    while True:
        queryURL = 'https://s.search.naver.com/p/newssearch/search.naver?cluster_rank=19&de=&ds=&eid=&field=0&force_original=&is_dts=0&is_sug_officeid=0&mynews=0&news_office_checked=&nlu_query=&nqx_theme=&nso=%26nso%3Dso%3Ar%2Cp%3Aall%2Ca%3Aall&nx_and_query=&nx_search_hlquery=&nx_search_query=&nx_sub_query=&office_category=0&office_section_code=0&office_type=0&pd=0&photo=0&query=' + title + '&query_original=&service_area=0&sort=0&spq=0&start=' + str(page) + '1&where=news_tab_api&nso=so:r,p:all,a:all'
        print(queryURL)
        try:
            response = requests.get(queryURL, timeout=10)
        except:
            print('Time out from requests.get(): ', queryURL)
            return None
        
        if json.loads(response.text)['contents'] == []: #네이버가 더 이상 검색 결과를 제공하지 않을 경우 종료
            return newsURLs

        searchResultHTMLs = [BeautifulSoup(i, 'html.parser').find('div', class_ = 'info_group')  for i in json.loads(response.text)['contents']]    #응답의 HTML 중에 특정 부분을 가져와서 soup로 변환
        for searchResultHTML in searchResultHTMLs:
            if '네이버뉴스' in searchResultHTML.contents[3]:    #네이버 뉴스만을 수집
                newsURLs.append(searchResultHTML.contents[3].get('href').split('?')[0].replace('/mnews', ''))
            
            if len(newsURLs)>=number_of_news:   #필요한 개수만큼 뉴스 url을 수집했으면 종료
                return newsURLs
        
        page+=1


#news의 URL을 입력 받아서 comments를 다운받아 json 파일로 저장하는 함수
def downloadNewsComments(newsURL):
    comments = []
    
    oid = newsURL.split('/')[-2]    #채널 ID
    aid = newsURL.split('/')[-1]    #뉴스 ID

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
    
    #내용을 감싸는 jQuery~함수 부분 제거
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


def downloadNewsContent(newsURL):
    try:
        response = requests.get(newsURL, timeout=10)
    except:
        print('Time out from requests.get(): ', newsURL)
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup.select_one('#title_area > span'))    #제목
    print(soup.select_one('#dic_area')) #본문(사진 포함)
    
    if soup.select_one('#contents > div._VOD_PLAYER_WRAP') != None: #영상이 있는 경우 영상 주소 반환
        videoKey = soup.select_one('#contents > div._VOD_PLAYER_WRAP').get('data-inkey')
        apiURL = 'https://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/ED5B61A25414EDC8495C57707F7CE007402B?key=' + videoKey + '&sid=2006&pid=51d65d91-8641-4c35-9d8f-1ad4bedd9b93&nonce=1706446614203&devt=HTML5_PC&prv=N&aup=N&stpb=N&cpl=ko_KR&env=real&lc=ko_KR&adi=%5B%7B%22adSystem%22%3A%22null%22%7D%5D&adu=%2F'
        try:
            response = requests.get(apiURL, timeout=10)
        except:
            print('Time out from requests.get(): ', apiURL)
            return
        print(json.loads(response.text)['meta']['url'])