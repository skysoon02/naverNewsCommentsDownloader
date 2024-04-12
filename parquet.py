import pandas as pd

filename = "2024316_total_metadata_df.parquet"

df = pd.read_parquet(filename, engine = 'pyarrow')

labeled_urls = []
left_urls = []

for idx, row in df.iterrows():
    url = "https://www.youtube.com/watch?v="+row['video_id']
    
    if 'MBC' in row['title'] or 'MBC' in row['tags'] or 'MBC' in row['description']:
        labeled_urls.append(row['title']+"\t"+'MBC')
    elif 'SBS' in row['title'] or 'SBS' in row['tags'] or 'SBS' in row['description']:
        labeled_urls.append(row['title']+"\t"+'SBS')
    elif 'KBS' in row['title'] or 'KBS' in row['tags'] or 'KBS' in row['description']:
        labeled_urls.append(row['title']+"\t"+'KBS')
    elif 'JTBC' in row['title'] or 'JTBC' in row['tags'] or 'JTBC' in row['description']:
        labeled_urls.append(row['title']+"\t"+'JTBC')
    elif 'YTN' in row['title'] or 'YTN' in row['tags'] or 'YTN' in row['description']:
        labeled_urls.append(row['title']+"\t"+'YTN')
    elif '채널A' in row['title'] or '뉴스A' in row['title'] or '채널A' in row['tags'] or '채널A' in row['description']:
        labeled_urls.append(row['title']+"\t"+'채널A')
    elif 'CHOSUN' in row['title'] or 'CHOSUN' in row['tags']  or 'chosun' in row['tags'] or 'CHOSUN' in row['description'] or 'chosun' in row['description']:
        labeled_urls.append(row['title']+"\t"+'TV조선')
    else:
        left_urls.append(row['title'])


print(len(labeled_urls))

with open('labeled', 'w+', encoding="UTF-8-sig") as file:
    file.write('\n'.join(labeled_urls))

with open('left', 'w+', encoding="UTF-8-sig") as file:
    file.write('\n'.join(left_urls))

#f = open("asdf", "w", encoding="UTF-8-sig")




'''
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool


def youtube_to_naver(url):
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        print(soup)
        f = open("asdf", "w", encoding="UTF-8-sig")
        f.write(str(soup))
        f.close()
        #title = soup.select_one('body')
        a = html.find('yt-simple-endpoint')
        print(a)
        #print(title)

      
youtube_to_naver("https://www.youtube.com/watch?v=uiCdmv7s5sI")

for idx, row in df.iterrows():
    url = "https://www.youtube.com/watch?v="+row['video_id']
    urls.append(url)


with Pool(processes=16) as pool:
    pool.map(youtube_to_naver, urls)







'''