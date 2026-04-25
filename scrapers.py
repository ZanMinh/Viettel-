from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT
import pandas as pd
from datetime import datetime

def get_youtube_comments(url, max_comments=1000):
    downloader = YoutubeCommentDownloader()
    try:
        comments = downloader.get_comments_from_url(url, sort_by=SORT_BY_RECENT)
        data = []
        count = 0
        for comment in comments:
            if count >= max_comments:
                break
            data.append({
                'Ngày': datetime.now().strftime("%Y-%m-%d"),
                'Nguồn': 'YouTube',
                'Nội dung': comment['text']
            })
            count += 1
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Lỗi cào dữ liệu: {e}")
        return pd.DataFrame()