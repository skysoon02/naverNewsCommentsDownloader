import re


#풀영상이나 다시보기 등 네이버 뉴스에 없을만한 영상 제목들을 거르는 함수
#YTN: 다시보기
#SBS: 없는 듯
#KBS: [풀영상] <- 근데 거의 안 올라옴
#MBC: [풀영상]
#JTBC: [다시보기]
#TV조선: [TV CHOSUN LIVE]
#채널A: [다시보기]
def titleFilter(title, channelID):
    if channelID==1:        #YTN
        if '다시보기' in title:
            return False

    elif channelID==55:     #SBS
        pass

    elif channelID==56:     #KBS
        if title.startswith('[풀영상]'):
            return False
        
    elif channelID==214:    #MBC
        if '[풀영상]' in title:
            return False
        
    elif channelID==437:    #JTBC
        if title.startswith('[다시보기]'):
            return False
    
    elif channelID==448:    #TV조선
        if title.startswith('[TV CHOSUN LIVE]'):
            return False
    
    elif channelID==449:    #채널A
        if title.startswith('[다시보기]'):
            return False

    return True


#특수문자나 날짜, 채널 이름 등을 제거하는 함수
#YTN: [*]제거, postfix의 / YTN 제거
#SBS: [*], (*) 제거, postfix의 / SBS 제거
#KBS: [*]제거, postfix의 / KBS 20XX.XX.XX 제거
#MBC: [*], (*) 제거
#JTBC: [*]제거, postfix의 /*, |* 제거
#TV조선: [*]제거, postfix의 /* 제거
#채널A: [*]제거, postfix의 /*, |* 제거
def titleBeautifier(title0):
    idx1 = title0.rfind('|')
    if idx1 != -1:
        title0 = title0[:idx1]
    else:
        idx2 = title0.rfind('/')
        if idx2 != -1:
            title0 = title0[:idx2]

    title1 = re.sub(r"\(.*\)|\[.*\]|/.*|\|.*", "", title0)  #()제거, []제거, \제거, |제거
    title2 = re.sub("“|”|\"", "", title1)       #큰따옴표를 공백으로 변경
    title3 = re.sub(" ", "+", title2)           #공백을 더하기로 변경. 네이버 URL방식을 따름.
    return title3


#LCS문자열 비교 함수
#B에 A의 LCS가 들어있는 비율을 출력
def LCS(A, B):
    dp = [[0 for _ in range(len(B)+1)] for _ in range(len(A)+1)]

    for i in range(len(A)):
        for j in range(len(B)):
            if A[i] == B[j]:
                dp[i+1][j+1] = dp[i][j] +1
            else:
                dp[i+1][j+1] = max(dp[i+1][j], dp[i][j+1])
    return dp[i+1][j+1]/len(A)
