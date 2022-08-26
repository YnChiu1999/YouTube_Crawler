# YouTube_Crawler
YouTube_Crawler使用官方YouTube Data API抓取資料，使用前須先至 https://developers.google.com/youtube/v3 申請`YOUTUBE_API_KEY`，取得`YOUTUBE_API_KEY`之後即可透過以下代碼爬取台灣地區總觀看數前50名YouTube頻道之影片資訊及影片封面縮圖。


## 使用方式

### Step 1：將Youtube_Crawler.py中的`YOUTUBE_API_KEY`替換成從 https://developers.google.com/youtube/v3 申請到的`YOUTUBE_API_KEY`
```
YOUTUBE_API_KEY = "AIzaxxxxxxxxxxxxxxxxxxxxx"
```

### Step 2：指定要爬取的YouTube頻道影片
方法一：透過 https://commentpicker.com/youtube-channel-id.php 網站取得該YouTube頻道ID
```
list_youtube_channel_id = ["UCMUnInmOkrWN4gof9KlhNmQ", "UCdRKafyb--geO9ySg6CbhYA", 'UCfX769yHKr7S8gz7UigOsbg', 'UC6IMF6xi_MZ3jA1wRlPQDLA']
```

方法二：透過 _get_top50_YouTube.py 檔案取得該台灣地區前50名YouTube頻道ID
```
from _get_top50_YouTube import getTop50ID
list_youtube_channel_id = topForTW(YOUTUBE_API_KEY)
```

### Step 3：執行Youtube_Crawler.py爬取指定YouTube頻道之影片資訊及影片封面縮圖
```
$ python Youtube_Crawler.py
```

### Step 4：查看獲取的影片資訊及影片封面縮圖
影片資訊：打開 `YT_output.csv` 檔案
[YT_output.csv](https://github.com/YnChiu1999/YouTube_Crawler/files/9433603/YT_output.csv)

封面縮圖：打開 `download_image` 資料夾  
![image](https://user-images.githubusercontent.com/111637364/186917014-cb1378c2-b95a-4ec1-9b46-ddb79323f11a.png)
