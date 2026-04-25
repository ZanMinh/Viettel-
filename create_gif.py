from moviepy.editor import VideoFileClip
from rembg import remove
from PIL import Image
import numpy as np

# 1. Tên file video sau khi Minh đã đổi ở Bước 1
video_input = "robot_video.mp4"

def process_frame(frame):
    img = Image.fromarray(frame)
    # Tách nền bằng AI
    out = remove(img)
    return np.array(out)

print("🚀 Đang bắt đầu tách nền... Minh đợi máy chạy xíu nhé!")

try:
    # Lấy 2 giây đầu để làm GIF
    clip = VideoFileClip(video_input).subclip(0, 2)
    # Xử lý xóa nền cho từng khung hình
    new_clip = clip.fl_image(process_frame)
    # Lưu file GIF trong suốt
    new_clip.write_gif("robot_khong_nen.gif", fps=10)
    print("✅ QUÁ TUYỆT VỜI! Mở file 'robot_khong_nen.gif' bên trái nha Minh.")
except Exception as e:
    print(f"❌ Lỗi rồi: {e}")