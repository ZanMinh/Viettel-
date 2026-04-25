import pandas as pd
import random
from datetime import datetime, timedelta

def create_sample_data(days=30):
    # Khai báo dữ liệu mẫu ngay trong hàm
    platforms = ['Facebook', 'TikTok', 'Báo chí', 'YouTube']
    sentiments = ['Tích cực', 'Trung lập', 'Tiêu cực']
    
    contents = {
        'Tích cực': ["Mạng Viettel rất nhanh", "Giá cước hợp lý", "Hỗ trợ nhiệt tình"],
        'Tiêu cực': ["Mạng lag quá", "Trừ tiền vô lý", "Chờ tổng đài lâu"],
        'Trung lập': ["Đang dùng gói cước mới", "Vừa gia hạn xong"]
    }
    
    data = []
    for i in range(100):
        date = datetime.now() - timedelta(days=random.randint(0, days))
        sent = random.choice(sentiments)
        data.append({
            'Ngày': date,
            'Nguồn': random.choice(platforms),
            'Nội dung': random.choice(contents[sent]),
            'Cảm xúc': sent
        })
    return pd.DataFrame(data)