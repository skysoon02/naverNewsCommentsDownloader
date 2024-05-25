from config.setting import *
from download.api import *
from download.search import *
from utility.mysql import *
from utility.utils import *
from utility.tsv import *

import json
from multiprocessing import Pool
import csv
from datetime import datetime


db = None


#news를 다운로드하기 위한 process
def downloadNewsContent_process(newsURL):
    res = downloadNewsContent(newsURL)
    oid = newsURL.split('/')[-2]    #채널 ID
    aid = newsURL.split('/')[-1]    #뉴스 ID
    objectId = oid + '_' + aid
    return (objectId, res)


#comments를 다운로드하기 위한 process
def downloadNewsComments_process(newsURL):
    ret = []
    res = downloadNewsComments(newsURL)
    for i in res:
        ret.append((i['commentNo'], i['parentCommentNo'], i['objectId'], i['userIdNo'], json.dumps(i)))
    return ret
    

#user 를 다운로드하기 위한 process
def downloadUserContents_process(ID):
    if str(ID)[0] == '8': #commentID
        res = downloadUserContent(ID, 'commentID')
        if res != None:
            return (res['user']['idNo'], None, json.dumps(res))
    else:               #userID
        res = downloadUserContent(ID, 'userID')
        if res != None:
            return (res['user']['idNo'], ID, json.dumps(res))
    

#user follow를 다운로드하기 위한 process
def downloadUserFollowers_process(user):    #(userId, userInKey or commentNo) 형태
    if str(user[1])[0] == '8': #commentID
        res = downloadUserFollowers(user[1], 'commentID')
    else:
        res = downloadUserFollowers(user[1], 'userID')
    return (user, res)  #((followeeId, followeeInKey or followeeCommentNo), [[userIdNo, userInKey], [userIdNo, userInKey], ...])


#user comment를 다운로드하기 위한 process
def downloadUserComments_process(ID):
    if str(ID)[0] == '8': #commentID
        res = downloadUserComments(ID, 'commentID')
    else:
        res = downloadUserComments(ID, 'userID')
    return res


def main():
    db = DB()

    cycle = 1
    newsURLs = []

    print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
    print('Naver Comment Downlaoder start')

    #0. Get news urls
    with open(path_newsURL+'/newsList_test', 'r', encoding="UTF-8-sig") as file:
        rea = csv.reader(file, delimiter='\t')
        for row in rea:
            if row[0][8] == 's':    #delete news start with 'sports.news'
                continue
            newsURLs.append(row[0])

    print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
    print('Naver Comment Downlaoder start')

    while len(newsURLs) > 0:
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Cycle\t{0} starts.'.format(cycle))

        #1. news
        #1-1. DB에서 중복 제거
        _newsURLs = []
        for newsURL in newsURLs:
            newsId = newsURL.split('/')[-2] + '_' + newsURL.split('/')[-1]
            if db.searchNews(newsId) == False:
                _newsURLs.append(newsURL)
        newsURLs = _newsURLs

        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Cycle\t{0}. {1} news datas are remained after deduplicate.'.format(cycle, len(newsURLs)))

        #1-2. 뉴스 다운로드 후 저장
        res = []
        with Pool(processes=number_of_process) as pool:
            res = pool.map(downloadNewsContent_process, newsURLs)
        db.insertNews(res)

        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Cycle\t{0}. {1} news datas are stored in DB.'.format(cycle, len(res)))
        
        #2. 댓글에서 유저 추출
        #2-1. 뉴스의 댓글 다운로드
        res = []
        with Pool(processes=number_of_process) as pool:
            res = pool.map(downloadNewsComments_process, newsURLs)

        #2-2. 유저 추출
        usersToDownload = []
        users = {}  #Dictionary to deduplicate
        for commentList in res:
            for comment in commentList:
                commentNo = comment[0]
                userIdNo = comment[3]
                if db.searchUser(userIdNo) == False:
                    users[userIdNo] = commentNo
        if None in users:   #삭제된 유저
            del users[None]
        
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Cycle\t{0}. {1} users are extracted from news.'.format(cycle, len(users)))

        #2-3. 유저 팔로워에서 유저 추출
        followCycle = 1
        while len(users) > 0:
            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
            print('Cycle\t{0}. Inner Cycle\t{1} starts.'.format(cycle, followCycle))
            
            usersToDownload.extend(users.values())   #comment를 가져와야 되는 유저 목록

            #2-3-1. 유저 정보 다운로드
            with Pool(processes=number_of_process) as pool:
                res = pool.map(downloadUserContents_process, users.values())
            res = [i for i in res if i != None] #None 제거. user info가 없는 경우  None으로 반환됨
            db.insertUser(res)

            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
            print('Cycle\t{0}. Inner Cycle\t{1}. {2} user data are stored in DB from {3}. The cumulative number of users is {4}.'.format(cycle, followCycle, len(res), len(users), len(usersToDownload)))

            #2-3-2. 팔로워 정보 다운로드
            with Pool(processes=number_of_process) as pool:
                res = pool.map(downloadUserFollowers_process, users.items())
            res = [i for i in res if i[1] != None] #None 제거. user info가 없는 경우  None으로 반환됨

            followDB = []
            for followInfo in res:
                followee = followInfo[0]
                followers = followInfo[1]
                for follower in followers:
                    followDB.append((followee[0], follower[0]))
            db.insertFollow(followDB)

            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
            print('Cycle\t{0}. Inner Cycle\t{1}. {2} follow data are stored in DB.'.format(cycle, followCycle, len(followDB)))
            
            #2-3-3. 유저 추출
            users = {}  #Dictionary to deduplicate
            for followerInfo in res:
                followers = followerInfo[1]
                for follower in followers:
                    userInKey = follower[1]
                    userIdNo = follower[0]
                    if db.searchUser(userIdNo) == False:
                        users[userIdNo] = userInKey

            print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
            print('Cycle\t{0}. Inner Cycle\t{1}. {2} followers are added to new users to download.'.format(cycle, followCycle, len(users)))
            
            followCycle += 1

        #3 comment
        #3-1. 유저가 작성한 Comments 다운로드
        with Pool(processes=number_of_process) as pool:
            res = pool.map(downloadUserComments_process, usersToDownload)
        db.insertComment(res)

        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Cycle\t{0}. {1} comments data are stored in DB.'.format(cycle, len(res)))
        
        #4 news
        newsURLs = {}
        for comment in res:
            newsURL = "https://n.news.naver.com/mnews/article/" + comment['objectId'][4:7] + '_' +  comment['objectId'][8:]
            newsURLs.add(newsURL)
        newsURLs = list(newsURLs)

        cycle += 1 



def debug():
    db = DB()
    db.check()
    db.deleteAll()
    #print(db.searchNews('056_0011647391'))
    #db.insertNews([('123', 'asdf'), ('456', 'asdfasdf')])
    return


if __name__ == '__main__':
    debug()
    main()

