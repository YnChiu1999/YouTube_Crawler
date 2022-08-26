import codecs
from pprint import pprint
import requests
import csv
from datetime import datetime
import os
from _get_top50_YouTube import getTop50ID  # user-defined

### Step 0：Get "YOUTUBE_API_KEY" and "Channel ID"
YOUTUBE_API_KEY = "AIzaSyBnL0UuXW95x87qL43PEaBh779G7UWODEk"
# Get the Channel ID for YouTube Crawler
## 方法一：透過 https://commentpicker.com/youtube-channel-id.php 網站取得該YouTube頻道ID
list_youtube_channel_id = ["UCMUnInmOkrWN4gof9KlhNmQ", "UCdRKafyb--geO9ySg6CbhYA", 'UCfX769yHKr7S8gz7UigOsbg', 'UC6IMF6xi_MZ3jA1wRlPQDLA']
## 方法二：透過 _get_top50_YouTube.py 檔案取得該台灣地區前50名YouTube頻道ID
# list_youtube_channel_id = getTop50ID(YOUTUBE_API_KEY)

# Make the folder for saving downloaded image
os.mkdir(f"./download_image/")

### Step 1：YouTube Crawler
def main():
    all_video_info = []
    for youtube_channel_id in list_youtube_channel_id:
        ## 1.想要抓取頻道內上傳的影片前，需要先抓到"上傳影片"清單的 ID，再用此 ID 去取的影片清單。 i.e., 頻道的ID → 影片清單的ID → 影片的ID list
        # 1) "頻道的ID"
        youtube_spider = YouTubeCrawler(YOUTUBE_API_KEY)
        channel_subCount = youtube_spider.getsub_count(youtube_channel_id)
        print(channel_subCount)
        # 2) 頻道上傳影片"影片清單的ID"
        uploads_id = youtube_spider.get_channel_uploads_id(youtube_channel_id)
        print(uploads_id)
        # 3) 頻道上傳之"影片的ID list"
        #video_ids = youtube_spider.get_playlist(uploads_id, max_results=100)
        all_video_ids = []
        next_page_token = ''
        while 1:
            video_ids, next_page_token = youtube_spider.get_playlist(uploads_id, page_token=next_page_token, max_results=100)
            all_video_ids.extend(video_ids)
            # 如果沒有下一頁，則跳離
            if not next_page_token:
                break
            # if not len(all_video_ids)>5:
            #     break
        print(len(all_video_ids))
        print(all_video_ids)

        ## 2.由"影片的ID list"，一部一部取得所需之"影片info"。
        for video_id in all_video_ids:
            print("----------------------")
            video_info = youtube_spider.get_video(video_id)
            video_info['subscriberCount'] = channel_subCount
            print(video_info)
            all_video_info.append(video_info)
            # # 留言回覆
            # next_page_token = ''
            # while 1:
            #     comments, next_page_token = youtube_spider.get_comments(video_id, page_token=next_page_token)
            #     print(comments)
            #     # 如果沒有下一頁留言，則跳離
            #     if not next_page_token:
            #         break

    ## 3.寫入csv檔、
    labels = ['id', 'channelTitle', 'subscriberCount', 'publishedAt', 'title', 'likeCount', 'commentCount', 'viewCount', 'video_url']
    try:
        with open('YT_output.csv', 'a+', encoding = 'utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=labels)
            writer.writeheader()
            for elem in all_video_info:
                writer.writerow(elem)
    except IOError:
        print("I/O error")

### Subroutine：YouTube Crawler
class YouTubeCrawler():
    ## 1.每一次送出請求皆需要帶上API Key。
    def __init__(self, api_key):
        self.base_url = "https://www.googleapis.com/youtube/v3/"
        self.api_key = api_key

    ## 2.回傳資料要轉換JSON，包含用於組合網址、請求的函式，也作請求失敗的處理。
    def get_html_to_json(self, path):
        """組合 URL 後 GET 網頁並轉換成 JSON"""
        api_url = f"{self.base_url}{path}&key={self.api_key}"
        r = requests.get(api_url)
        if r.status_code == requests.codes.ok:
            data = r.json()
        else:
            data = None
        return data

    ## 3.回傳"頻道訂閱人數"。
    def getsub_count(self, channel_id, part='snippet,statistics'):
        """取得頻道上傳影片清單的ID"""
        # UC7ia-A8gma8qcdC6GDcjwsQ
        path = f'channels?part={part}&id={channel_id}'
        data = self.get_html_to_json(path)
        try:
            subCount = data['items'][0]["statistics"]["subscriberCount"]
        except KeyError:
            subCount = None
        return subCount
        # base_url = "https://www.googleapis.com/youtube/v3/channels"
        # response = requests.get(base_url)
        #
        # if response.status_code == 200:
        #     response_dict = response.json()
        #     results3_list = [response_dict["items"][0]["statistics"]["subscriberCount"]]
        # print(results3_list)

    ## 4.回傳頻道"影片清單的ID"。
    def get_channel_uploads_id(self, channel_id, part='contentDetails'):
        """取得頻道上傳影片清單的ID"""
        # UC7ia-A8gma8qcdC6GDcjwsQ
        path = f'channels?part={part}&id={channel_id}'
        data = self.get_html_to_json(path)
        try:
            uploads_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        except KeyError:
            uploads_id = None
        return uploads_id

    ## 5.回傳頻道"影片的ID list"。
    def get_playlist(self, playlist_id, part='contentDetails', page_token='', max_results=100):
        """取得影片清單ID中的影片"""
        # UU7ia-A8gma8qcdC6GDcjwsQ
        path = f'playlistItems?part={part}&playlistId={playlist_id}&maxResults={max_results}&pageToken={page_token}'
        data = self.get_html_to_json(path)
        if not data:
            return []
        # 下一頁的數值
        next_page_token = data.get('nextPageToken', '')
        video_ids = []
        for data_item in data['items']:
            video_ids.append(data_item['contentDetails']['videoId'])
        return video_ids, next_page_token

    ## 6.回傳"影片info"。
    def get_video(self, video_id, part='snippet,statistics'):
        """取得影片資訊"""
        path = f'videos?part={part}&id={video_id}'
        data = self.get_html_to_json(path)
        if not data:
            return {}

        # 以下整理並提取需要的資料
        data_item = data['items'][0]

        try:
            # 2019-09-29T04:17:05Z
            time_ = datetime.strptime(data_item['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            # 日期格式錯誤
            time_ = None

        url_ = f"https://www.youtube.com/watch?v={data_item['id']}"

        try:
            comment_ = data_item['statistics']['commentCount']
        except:
            # 留言停用
            comment_ = 0

        try:
            like_ = data_item['statistics']['likeCount']
        except:
            # 留言讚數
            like_ = 0
        info = {
            'id': data_item['id'],                                          # 影片ID
            'channelTitle': data_item['snippet']['channelTitle'],           # 頻道名稱
            'publishedAt': time_,                                           # 影片釋出時間
            'video_url': url_,                                              # 影片網址
            'title': data_item['snippet']['title'],                         # 影片標題
            # 'description': data_item['snippet']['description'],           # 影片描述
            'likeCount': like_,                                             # 讚數
            # 'dislikeCount': data_item['statistics']['dislikeCount'],      # 倒讚數
            'commentCount': comment_,                                       # 評論數
            'viewCount': data_item['statistics']['viewCount']               # 點閱率
        }
        # f = open(f"./download_image/{data_item['id']}.jpg", 'wb')           # 封面縮圖
        # response = requests.get(f"https://i.ytimg.com/vi/{data_item['id']}/0.jpg")
        # f.write(response.content)
        # f.close()
        return info

    ## 7.回傳"影片留言info"。
    def get_comments(self, video_id, page_token='', part='snippet', max_results=100):
        """取得影片留言"""
        # jyordOSr4cI
        path = f'commentThreads?part={part}&videoId={video_id}&maxResults={max_results}&pageToken={page_token}'
        data = self.get_html_to_json(path)
        if not data:
            return [], ''
        # 下一頁的數值
        next_page_token = data.get('nextPageToken', '')

        # 以下整理並提取需要的資料
        comments = []
        for data_item in data['items']:
            data_item = data_item['snippet']
            top_comment = data_item['topLevelComment']
            try:
                # 2020-08-03T16:00:56Z
                time_ = datetime.strptime(top_comment['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                # 日期格式錯誤
                time_ = None

            if 'authorChannelId' in top_comment['snippet']:
                ru_id = top_comment['snippet']['authorChannelId']['value']
            else:
                ru_id = ''

            ru_name = top_comment['snippet'].get('authorDisplayName', '')
            if not ru_name:
                ru_name = ''

            comments.append({
                'reply_id': top_comment['id'],                                 # 留言ID
                'ru_id': ru_id,                                                # 留言者ID
                'ru_name': ru_name,                                            # 留言者名稱
                'reply_time': time_,                                           # 留言時間
                'reply_content': top_comment['snippet']['textOriginal'],       # 留言內容
                'rm_positive': int(top_comment['snippet']['likeCount']),       # 留言讚數
                'rn_comment': int(data_item['totalReplyCount'])                # 留言回覆數
            })
        return comments, next_page_token

if __name__ == "__main__":
    main()