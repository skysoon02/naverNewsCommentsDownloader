from config.setting import *
from download.api import *
from download.search import *
from utility.mysql import *
from utility.utils import *
from utility.tsv import *

import json
from multiprocessing import Pool
import tqdm
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
        objectId = i['objectId'][4:7] + '_' +  i['objectId'][8:]
        ret.append((i['commentNo'], i['parentCommentNo'], objectId, i['userIdNo'], json.dumps(i)))
    return ret


#comments 메타데이터를 다운로드하기 위한 process
def downloadNewsCommentsMeta_process(newsURL):
    res = downloadNewsCommentsMeta(newsURL)
    oid = newsURL.split('/')[-2]    #채널 ID
    aid = newsURL.split('/')[-1]    #뉴스 ID
    objectId = oid + '_' + aid
    return (objectId, json.dumps(res))



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
    ret = []
    if str(ID)[0] == '8': #commentID
        res = downloadUserComments(ID, 'commentID')
    else:
        res = downloadUserComments(ID, 'userID')

    if res == None:
        return []
    
    for i in res:
        objectId = i['objectId'][4:7] + '_' +  i['objectId'][8:]
        ret.append((i['commentNo'], i['parentCommentNo'], objectId, i['userIdNo'], json.dumps(i)))
    return ret


def main():
    db = DB()

    users = {}  #Dictionary to deduplicate
    cycle = 1

    print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
    print('Naver Comment Downlaoder start')

    #0. 첫 유저 목록을 위해 외부 파일에서 뉴스 목록 가져오기
    newsURLs = []
    with open(path_newsURL+'/newsList_test', 'r', encoding="UTF-8-sig") as file:
        rea = csv.reader(file, delimiter='\t')
        for row in rea:
            if row[0][8] == 's':    #delete news start with 'sports.news'
                continue
            newsURLs.append(row[0])

    #1. 뉴스 다운로드 후 저장
    res = []
    with Pool(processes=number_of_process) as pool:
        #res = list(tqdm.tqdm(pool.imap(downloadNewsContent_process, newsURLs), total=len(newsURLs)))
        res = list(tqdm.tqdm(pool.imap(downloadNewsCommentsMeta_process, newsURLs), total=len(newsURLs)))
    db.insertNews(res)

    print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
    print('Init. {0} news datas are stored in DB.'.format(len(res)))
    
    #2. 댓글 다운로드 후 저장
    res = []
    with Pool(processes=number_of_process) as pool:
        res = list(tqdm.tqdm(pool.imap(downloadNewsComments_process, newsURLs), total=len(newsURLs)))
    for commentList in res:
        #commentList = [i for i in commentList if db.searchComment(i[0])==False]
        db.insertComment(commentList)
    comments = sum(res, [])

    print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
    print('Init. {0} comments data are stored in DB.'.format(len(comments)))

    #3. 댓글에서 유저 추출
    for comment in comments:
        commentNo = comment[0]
        userIdNo = comment[3]
        if db.searchUser(userIdNo) == False:
            users[userIdNo] = commentNo
    if None in users:   #삭제된 유저
        del users[None]

    print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
    print('Init. {0} users are extracted from news comments.'.format(len(users)))
    
    while len(users) > 0:
        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Cycle\t{0}. starts.'.format(cycle))

        #1. 유저
        #1-1. 유저 정보 다운로드
        with Pool(processes=number_of_process) as pool:
            res = list(tqdm.tqdm(pool.imap(downloadUserContents_process, users.values()), total=len(users.values())))
        res = [i for i in res if i != None] #None 제거. user info가 없는 경우  None으로 반환됨
        db.insertUser(res)

        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Cycle\t{0}. {1} user data are stored in DB from {2} tasks.'.format(cycle,  len(res), len(users)))
        
        #1-2. 유저가 작성한 Comments 다운로드
        with Pool(processes=number_of_process) as pool:
            res = list(tqdm.tqdm(pool.imap(downloadUserComments_process, users.values()), total=len(users.values())))   #res 기반으로 가져와야 되나?
        comments = sum(res, [])

        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Cycle\t{0}. {1} comments by user are extracted.'.format(cycle, len(comments)))

        #2. 뉴스
        #2-1. 댓글에서 뉴스 추출
        newsURLs = set()
        for comment in comments:
            if db.searchNews(comment[2]) == False:  #objectId
                newsURL = "https://n.news.naver.com/mnews/article/" + comment[2].replace('_', '/')
                newsURLs.add(newsURL)
        newsURLs = list(newsURLs)

        #2-2. 뉴스 다운로드 후 저장
        res = []
        with Pool(processes=number_of_process) as pool:
            #res = list(tqdm.tqdm(pool.imap(downloadNewsContent_process, newsURLs), total=len(newsURLs)))
            res = list(tqdm.tqdm(pool.imap(downloadNewsCommentsMeta_process, newsURLs), total=len(newsURLs)))
        db.insertNews(res)

        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Cycle\t{0}. {1} news data(metadata of comments) are stored in DB.'.format(cycle, len(res)))

        #2-3. 뉴스의 댓글 다운로드 후 저장
        res = []
        with Pool(processes=number_of_process) as pool:
            res = list(tqdm.tqdm(pool.imap(downloadNewsComments_process, newsURLs), total=len(newsURLs)))
        for commentList in res:
            #commentList = [i for i in commentList if db.searchComment(i[0])==False]
            try:
                db.insertComment(commentList)
            except:
                with open('error_data', 'w+') as file:
                    file.write('\n'.join([i[3] for i in commentList]))
            
        comments = sum(res, [])

        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Cycle\t{0}. {1} comments data are stored in DB.'.format(cycle, len(comments)))

        #3. 유저의 팔로우
        #3-1. 팔로워 정보 다운로드 후 저장
        with Pool(processes=number_of_process) as pool:
            res = list(tqdm.tqdm(pool.imap(downloadUserFollowers_process, users.items()), total=len(users.items())))
        res = [i for i in res if i[1] != None] #None 제거. user info가 없는 경우  None으로 반환됨

        followDB = []
        for followInfo in res:
            followee = followInfo[0]
            followers = followInfo[1]
            for follower in followers:
                followDB.append((followee[0], follower[0]))
        db.insertFollow(followDB)

        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Cycle\t{0}. {1} follow data are stored in DB.'.format(cycle, len(followDB)))
        
        #3-2. 유저 추출
        users = {}  #Dictionary to deduplicate
        for followerInfo in res:
            followers = followerInfo[1]
            for follower in followers:
                userInKey = follower[1]
                userIdNo = follower[0]
                if db.searchUser(userIdNo) == False:
                    users[userIdNo] = userInKey

        print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), end=' ')
        print('Cycle\t{0}. {1} users are added to tasks.'.format(cycle, len(users)))
        
        cycle += 1 



def debug():
    db = DB()
    db.check()
    #db.deleteAll()

    #print(downloadNewsCommentsMeta('https://n.news.naver.com/article/comment/001/0008419824'))
    #print(downloadNewsContent('https://n.news.naver.com/mnews/article/056/0011425827'))
    #print(downloadUserComments(826737275369947268, 'commentID'))
    #print(db.searchNews('056_0011647391'))
    #db.insertNews([('123', 'asdf'), ('456', 'asdfasdf')])
    return


if __name__ == '__main__':
    #debug()
    main()

