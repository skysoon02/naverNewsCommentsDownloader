from config.setting import *
from config.predefined import *
from utility.utils import *

import requests
from bs4 import BeautifulSoup
import json


#news의 URL을 입력 받아서 comments를 다운로드
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
    
    return comments


#news의 URL을 입력 받아서 content를 다운로드
def downloadNewsContent(newsURL):
    try:
        response = requests.get(newsURL, timeout=10)
    except:
        print('Time out from requests.get(): ', newsURL)
        return
    
    return response.text

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



'''
def downloadUserID(commentID):
    headers = {
        'Referer': "https://n.news.naver.com",
        "User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
    apiURL = "https://apis.naver.com/commentBox/cbox/web_naver_user_info_jsonp.json?ticket=news&templateId=view_society_m1&pool=cbox5&_cv=20240311122521&_callback=jQuery331046734403471661223_1710381136305&lang=ko&country=KR&objectId=news001%2C00000123&categoryId=&pageSize=20&indexSize=10&groupId=&listType=user&pageType=more&page=2&commentNo="+str(commentID)+"&targetUserInKey=&includeAllStatus=true&_=1710381136309"

    try:
        response = requests.get(apiURL, headers=headers, timeout=10)
    except:
        print('Time out from requests.get(): ', apiURL)
        return

    print(response.text)
    startIdx = response.text.find('{')
    resDict = json.loads(response.text[startIdx:-2])
    return resDict['result']['commentList'][0]
'''

def downloadUserComments(ID, paramType):
    comments = []
    
    if paramType=='commentID':
        commentID = ID
        apiURL = "https://apis.naver.com/commentBox/cbox/web_naver_user_info_jsonp.json?ticket=news&templateId=view_society_m1&pool=cbox5&_cv=20240311122521&_callback=jQuery331046734403471661223_1710381136305&lang=ko&country=KR&objectId=news001%2C00000123&categoryId=&pageSize=20&indexSize=10&groupId=&listType=user&pageType=more&page=2&commentNo="+str(commentID)+"&targetUserInKey=&includeAllStatus=true&_=1710381136309"
    elif paramType=='userID':
        userID = ID
        apiURL = "https://apis.naver.com/commentBox/cbox/web_naver_user_info_jsonp.json?ticket=news&templateId=view_society_m1&pool=cbox5&_cv=20240311122521&_callback=jQuery33105296405296895645_1710383158565&lang=ko&country=KR&objectId=&categoryId=&pageSize=20&indexSize=10&groupId=&listType=user&pageType=more&commentNo=&targetUserInKey="+str(userID)+"&includeAllStatus=true&_=1710383158572"
    

    headers = {
        'Referer': "https://n.news.naver.com",
        "User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }

    #첫페이지 받아오기
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

        apiURL = 'https://apis.naver.com/commentBox/cbox/web_naver_list_per_user_jsonp.json?ticket=news&pool=cbox5&_cv=20240311122521&lang=ko&country=KR&categoryId=&pageSize=20&indexSize=10&listType=user&pageType=more&sort=NEW&moreParam.direction=next&moreParam.prev='+resDict['result']['morePage']['prev']+'&moreParam.next='+resDict['result']['morePage']['next']+'&targetUserInKey=686913160061388254&includeAllStatus=true&_=1710470908862'
        try:
            response = requests.get(apiURL, headers=headers, timeout=10)
        except:
            print('Time out from requests.get(): ', apiURL)
            continue
        if response.status_code != 200:
            return

        print(response.text)
        print(response)
    
        startIdx = response.text.find('{')
        resDict = json.loads(response.text[startIdx:-2])
        comments.append(resDict['result']['commentList'])
    
    return comments


def downloadUserFollowers(ID, paramType):
    followers=[]
    
    if paramType=='commentID':
        commentID = ID
        apiURL = 'https://apis.naver.com/commentBox/cbox/web_naver_follower_list_jsonp.json?ticket=news&templateId=default_election&pool=cbox5&_cv=20240404150157&_callback=jQuery33104762941492794568_1712660950860&lang=ko&country=KR&objectId=news001%2C0014620778&categoryId=&pageSize=&indexSize=10&groupId=&listType=OBJECT&pageType=more&commentNo='+str(commentID)+'&targetUserInKey=&_=1712660950885'
    elif paramType=='userID':
        userID = ID
        apiURL = 'https://apis.naver.com/commentBox/cbox/web_naver_follower_list_jsonp.json?ticket=news&templateId=default_election&pool=cbox5&_cv=20240404150157&_callback=jQuery33104762941492794568_1712660950860&lang=ko&country=KR&objectId=&categoryId=&pageSize=&indexSize=10&groupId=&listType=OBJECT&pageType=more&commentNo=&targetUserInKey='+str(userID)+'&_=1712660950894'
    

    #첫페이지 받아오기
    headers = {
        'Referer': 'https://n.news.naver.com/article/comment/001/0014620778',
        "User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
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
    for user in resDict['result']['userInfo']:
        followers.append([user['idNo'], int(user['userInKey'])])

    while resDict['result']['next'] is not None:
        if paramType=='commentID':
            commentID = ID
            apiURL = 'https://apis.naver.com/commentBox/cbox/web_naver_follower_list_jsonp.json?ticket=news&templateId=default_election&pool=cbox5&_cv=20240404150157&_callback=jQuery33104762941492794568_1712660950860&lang=ko&country=KR&objectId=news001%2C0014620778&categoryId=&pageSize=&indexSize=10&groupId=&listType=OBJECT&pageType=more&cursor='+str(resDict['result']['next'])+'&commentNo='+str(commentID)+'&targetUserInKey=&_=1712660950886'
        elif paramType=='userID':
            userID = ID
            apiURL = 'https://apis.naver.com/commentBox/cbox/web_naver_follower_list_jsonp.json?ticket=news&templateId=default_election&pool=cbox5&_cv=20240404150157&_callback=jQuery33104762941492794568_1712660950860&lang=ko&country=KR&objectId=&categoryId=&pageSize=&indexSize=10&groupId=&listType=OBJECT&pageType=more&cursor='+str(resDict['result']['next'])+'&commentNo=&targetUserInKey='+str(userID)+'&_=1712660950894'
        
        try:
            response = requests.get(apiURL, headers=headers, timeout=10)
        except:
            print('Time out from requests.get(): ', apiURL)
            return
        if response.status_code != 200:
            return
        startIdx = response.text.find('{')
        resDict = json.loads(response.text[startIdx:-2])
        for user in resDict['result']['userInfo']:
            followers.append([user['idNo'], int(user['userInKey'])])

    return followers


def downloadUserFollowings(ID, paramType):
    followings=[]
    
    if paramType=='commentID':
        commentID = ID
        apiURL = 'https://apis.naver.com/commentBox/cbox/web_naver_following_list_jsonp.json?ticket=news&templateId=default_election&pool=cbox5&_cv=20240404150157&_callback=jQuery33104762941492794568_1712660950860&lang=ko&country=KR&objectId=news001%2C0014620778&categoryId=&pageSize=&indexSize=10&groupId=&listType=OBJECT&pageType=more&commentNo='+str(commentID)+'&targetUserInKey=&_=1712660950885'
    elif paramType=='userID':
        userID = ID
        apiURL = 'https://apis.naver.com/commentBox/cbox/web_naver_following_list_jsonp.json?ticket=news&templateId=default_election&pool=cbox5&_cv=20240404150157&_callback=jQuery33104762941492794568_1712660950860&lang=ko&country=KR&objectId=&categoryId=&pageSize=&indexSize=10&groupId=&listType=OBJECT&pageType=more&commentNo=&targetUserInKey='+str(userID)+'&_=1712660950894'
    

    #첫페이지 받아오기
    headers = {
        'Referer': 'https://n.news.naver.com/article/comment/001/0014620778',
        "User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
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
    for user in resDict['result']['userInfo']:
        followings.append([user['idNo'], int(user['userInKey'])])

    while resDict['result']['next'] is not None:
        if paramType=='commentID':
            commentID = ID
            apiURL = 'https://apis.naver.com/commentBox/cbox/web_naver_following_list_jsonp.json?ticket=news&templateId=default_election&pool=cbox5&_cv=20240404150157&_callback=jQuery33104762941492794568_1712660950860&lang=ko&country=KR&objectId=news001%2C0014620778&categoryId=&pageSize=&indexSize=10&groupId=&listType=OBJECT&pageType=more&cursor='+str(resDict['result']['next'])+'&commentNo='+str(commentID)+'&targetUserInKey=&_=1712660950886'
        elif paramType=='userID':
            userID = ID
            apiURL = 'https://apis.naver.com/commentBox/cbox/web_naver_following_list_jsonp.json?ticket=news&templateId=default_election&pool=cbox5&_cv=20240404150157&_callback=jQuery33104762941492794568_1712660950860&lang=ko&country=KR&objectId=&categoryId=&pageSize=&indexSize=10&groupId=&listType=OBJECT&pageType=more&cursor='+str(resDict['result']['next'])+'&commentNo=&targetUserInKey='+str(userID)+'&_=1712660950894'
        
        try:
            response = requests.get(apiURL, headers=headers, timeout=10)
        except:
            print('Time out from requests.get(): ', apiURL)
            return
        if response.status_code != 200:
            return
        startIdx = response.text.find('{')
        resDict = json.loads(response.text[startIdx:-2])
        for user in resDict['result']['userInfo']:
            followings.append([user['idNo'], int(user['userInKey'])])

    return followings