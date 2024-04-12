from config.setting import *
from config.predefined import *
from utility.utils import *

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


#네이버 뉴스의 title을 입력 받아서 해당 뉴스의 URL들을 반환
#조건1. 네이버 뉴스(news.naver.com)으로 접근할 수 있어야 함
#조건2. 뉴스 채널이 동일해야 함
#조건3. LCS의 비율이 0.5 이상
def searchParticularNews(title, channelID, videoID):
    queryURL = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query=' + title
    print(queryURL)
    try:
        response = requests.get(queryURL, timeout=10)
    except:
        print('Time out from requests.get(): ', queryURL)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    searchResultHTMLs = soup.find_all('div', class_ = 'news_area')
    if searchResultHTMLs == []:    #검색 결과가 하나도 없는 경우
        print('There is no result of query id: ', videoID)
        return None
    
    newsURLs = []
    channelName = channelIDToName[channelID]
    for searchResultHTML in searchResultHTMLs:
        info_group = searchResultHTML.contents[1].contents[2]   #news_area > news_info > info_group
        news_tit = searchResultHTML.find('a', class_ = 'news_tit')    #news_area > news_contents > news_tit
        if channelName in info_group.contents[1].contents and '네이버뉴스' in info_group.contents[3].contents:  #news_area > news_info > info_group
            if LCS(title, news_tit.get('title'))>0.5:
                newsURLs.append([info_group.contents[3].get('href'), videoID])

    if len(newsURLs) != 1: #일치하는 검색 결과가 정확히 한 개가 아닌 경우
        print('There is not exactly one result from ', videoID )
        print('There are ', len(newsURLs))

    return [[newsURL[0].split('?')[0], newsURL[1]] for newsURL in newsURLs]  #'?sid=' 제거


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
