import streamlit as st
from openai import OpenAI
import pandas as pd
import plotly.express as px
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
import os

# =============================
# ⚙️ CONFIG
# =============================
st.set_page_config(page_title="Viettel AI", layout="wide", page_icon="🤖")

# =============================
# 🔑 API KEY (AN TOÀN)
# =============================
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    API_KEY = None

client = OpenAI(api_key=API_KEY)
# =============================
# 🎨 STYLE
# =============================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top right, #1e293b, #020617);
    color: #f8fafc;
    font-family: 'Segoe UI', sans-serif;
}

.welcome-text {
    text-align: center;
    font-size: 3.5rem !important;
    font-weight: 800;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-welcome {
    text-align: center;
    color: #94a3b8;
    font-size: 1.2rem;
}

.glass-card {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    text-align: center;
    transition: 0.3s;
}
.glass-card:hover {
    border: 1px solid #38bdf8;
    transform: translateY(-5px);
}
.robot-glow {
    border-radius: 50%;
    box-shadow: 0 0 60px rgba(56,189,248,0.2);
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# =============================
# 🧠 SENTIMENT FUNCTION
# =============================
def analyze_sentiment(text):
    text = text.lower()
    if any(word in text for word in ["tốt", "hay", "ok", "good", "đỉnh"]):
        return "Tích cực"
    elif any(word in text for word in ["tệ", "chán", "dở", "bad"]):
        return "Tiêu cực"
    else:
        return "Trung lập"

# =============================
# 🧠 SYSTEM PROMPT
# =============================
SYSTEM_PROMPT = """
Bạn là Viettel AI Assistant.

Chỉ trả lời về:
- Viettel
- Phân tích dữ liệu
- Phân tích cảm xúc
- YouTube, mạng xã hội

Trả lời ngắn gọn, có insight.
"""

# =============================
# STATE
# =============================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

if "menu" not in st.session_state:
    st.session_state.menu = "🏠 Trang chủ"

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.image("robot_khong_nen.gif", use_container_width=True)
    st.markdown("<h2 style='text-align:center;color:#38bdf8;'>VIETTEL AI</h2>", unsafe_allow_html=True)
    st.markdown("---")

    menu = st.radio(
        "Điều hướng",
        ["🏠 Trang chủ", "💬 Chat AI", "🎥 Phân tích"],
        index=["🏠 Trang chủ", "💬 Chat AI", "🎥 Phân tích"].index(st.session_state.menu)
    )

    st.session_state.menu = menu

# =============================
# 🏠 HOME (UI ĐẸP - GIỮ ROBOT + TITLE)
# =============================
if menu == "🏠 Trang chủ":

    # Title
    st.markdown('<h1 class="welcome-text">Xin chào, tôi là Viettel</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-welcome">Hệ thống phân tích cảm xúc & dữ liệu thông minh</p>', unsafe_allow_html=True)

    # Robot center
    _, col_robot, _ = st.columns([1,1.2,1])
    with col_robot:
        st.markdown('<div class="robot-glow">', unsafe_allow_html=True)
        st.image("robot_khong_nen.gif", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =============================
    # 📊 STATS (ĐẸP HƠN)
    # =============================
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="glass-card">
            <h2>😊 88%</h2>
            <p>Tích cực</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="glass-card">
            <h2>💬 2,150</h2>
            <p>Thảo luận</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="glass-card">
            <h2>⚡ 145ms</h2>
            <p>Tốc độ AI</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =============================
    # 📊 SENTIMENT BAR (ĐẸP HƠN)
    # =============================
    st.markdown("### 📊 Tổng quan cảm xúc")

    st.progress(0.88, text="😊 Tích cực - 88%")
    st.progress(0.2, text="😐 Trung lập - 20%")
    st.progress(0.15, text="😡 Tiêu cực - 15%")

    st.markdown("<br>", unsafe_allow_html=True)

    # =============================
    # 🔥 FEATURE CARDS
    # =============================
    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown("""
        <div class="glass-card">
        🤖 <h4>AI Chat</h4>
        <p>Hỏi đáp dữ liệu Viettel</p>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div class="glass-card">
        📊 <h4>Sentiment</h4>
        <p>Phân tích cảm xúc khách hàng</p>
        </div>
        """, unsafe_allow_html=True)

    with f3:
        st.markdown("""
        <div class="glass-card">
        🎥 <h4>YouTube</h4>
        <p>Phân tích comment video</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =============================
    # CTA BUTTON
    # =============================
    col_l, col_c, col_r = st.columns([1,1,1])
    with col_c:
        if st.button("🚀 BẮT ĐẦU NGAY", use_container_width=True):
            st.session_state.menu = "💬 Chat AI"
            st.rerun()
# =============================
# 💬 CHAT AI
# =============================
elif menu == "💬 Chat AI":
    st.markdown('<h1 class="welcome-text" style="font-size:2.5rem;">AI Assistant</h1>', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Hỏi về Viettel..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            try:
                with st.spinner("🤖 AI đang trả lời..."):
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[st.session_state.messages[0]] + st.session_state.messages[-5:]
                    )
                    reply = res.choices[0].message.content
            except Exception as e:
                reply = f"⚠️ Lỗi AI: {e}"

            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

# =============================
# 🎥 YOUTUBE ANALYSIS
# =============================
elif menu == "🎥 Phân tích":

    st.markdown('<h1 class="welcome-text" style="font-size:2.5rem;">YouTube Analysis</h1>', unsafe_allow_html=True)

    url = st.text_input("🔗 Nhập link YouTube")

    if url:
        with st.spinner("🤖 Đang lấy dữ liệu từ YouTube..."):
            try:
                downloader = YoutubeCommentDownloader()
                comments = downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR)
            except:
                st.error("❌ Không lấy được comment từ video này")
                st.stop()

        data = []
        for i, c in enumerate(comments):
            if i >= 40:
                break
            text = c.get('text', '')
            data.append({
                "User": c.get('author', ''),
                "Comment": text,
                "Sentiment": analyze_sentiment(text)
            })

        df = pd.DataFrame(data)

        if df.empty:
            st.warning("⚠️ Không có dữ liệu để phân tích")
            st.stop()

        col1, col2 = st.columns([2,1])

        with col1:
            fig = px.pie(df, names="Sentiment", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.metric("📊 Comments", len(df))
            st.success("AI đã phân tích xong!")

        st.dataframe(df, use_container_width=True)

        # 🧠 AI Insight
        if st.button("🧠 AI Phân tích Insight"):
            with st.spinner("AI đang phân tích..."):
                try:
                    sample_text = df["Comment"].head(10).to_string()

                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Phân tích sentiment và đưa insight ngắn"},
                            {"role": "user", "content": sample_text}
                        ]
                    )

                    insight = res.choices[0].message.content
                    st.success(insight)

                except Exception as e:
                    st.error(f"⚠️ Lỗi AI: {e}")