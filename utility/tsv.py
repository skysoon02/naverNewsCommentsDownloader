from config.setting import *
from config.predefined import *

import os
import json


#path_newsTitle에서 네이버 뉴스 title과 채널, 유튜브 영상 ID가 저장되어 있는 파일들을 읽어와서 list로 반환하는 함수
#format
#title              channel
#KAIST duck...      TV조선
#Korean birth...    MBC
def newsListReader():
    newsList = []

    for file_name in os.listdir(path_newsTitle):
        f = open(path_newsTitle+'/'+file_name, 'r', encoding='utf-8-sig')
        lines = f.readlines()
        for line in lines:
            title = line.split('\t')[0]
            channelID = channelNameToID[line.split('\t')[1]]
            videoID = line.split('\t')[2].rstrip('\n')
            newsList.append([title, channelID, videoID])

    return newsList

def writeTsv(path, data):
    f = open(path, 'w', encoding="UTF-8-sig")
    json.dump(data, f, ensure_ascii=False)
    f.close()