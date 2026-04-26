import streamlit as st
from openai import OpenAI
import pandas as pd
import plotly.express as px
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from streamlit_oauth import OAuth2Component

# =============================
# ⚙️ CONFIG
# =============================
st.set_page_config(page_title="Viettel AI Platform", layout="wide", page_icon="🤖")

# =============================
# 🔑 API KEY
# =============================
API_KEY = st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY) if API_KEY else None

# =============================
# 🔐 GOOGLE LOGIN
# =============================
CLIENT_ID = st.secrets.get("G_CLIENT_ID")
CLIENT_SECRET = st.secrets.get("G_CLIENT_SECRET")

oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    "https://accounts.google.com/o/oauth2/auth",
    "https://oauth2.googleapis.com/token",
    "https://www.googleapis.com/oauth2/v1/userinfo",
)


# =============================
# 🎨 STYLE
# =============================
st.markdown("""
<style>
.stApp {
    background: #020617;
    color: #f8fafc;
    font-family: 'Segoe UI', sans-serif;
}
.welcome-text {
    text-align: center;
    font-size: 3rem !important;
    font-weight: 800;
    background: linear-gradient(135deg, #ee0000, #ffffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.glass-card {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 20px;
    text-align: center;
}
.robot-glow {
    border-radius: 50%;
    box-shadow: 0 0 60px rgba(255,0,0,0.3);
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# =============================
# 🧠 SENTIMENT
# =============================
def analyze_sentiment(text):
    text = text.lower()
    if any(w in text for w in ["tốt", "hay", "ok", "good", "đỉnh"]):
        return "Tích cực"
    elif any(w in text for w in ["tệ", "chán", "dở", "bad"]):
        return "Tiêu cực"
    return "Trung lập"

# =============================
# 🛡️ LOGIN STATE
# =============================
if "token" not in st.session_state:
    st.session_state.token = None

# =============================
# 🔐 LOGIN PAGE
# =============================
if not st.session_state.token:
    st.markdown('<h1 class="welcome-text">Viettel AI Platform</h1>', unsafe_allow_html=True)

    result = oauth2.authorize_button(
        "🔑 Đăng nhập với Google",
        redirect_uri="http://localhost:8501",
        scope="email profile"
    )

    if result:
        st.session_state.token = result["token"]
        st.rerun()

    st.stop()
# =============================
# 🧭 MENU
# =============================
with st.sidebar:
    st.image("robot_khong_nen.gif", use_container_width=True)

    # 🔥 LOGOUT BUTTON
    if st.button("🚪 Đăng xuất"):
        st.session_state.token = None
        st.rerun()

    st.markdown("---")

    menu = st.radio("Menu", ["🏠 Trang chủ", "💬 Chat AI", "🎥 YouTube"])
# =============================
# 🏠 HOME
# =============================
if menu == "🏠 Trang chủ":

    st.markdown('<h1 class="welcome-text">Xin chào 👋</h1>', unsafe_allow_html=True)

    _, col_robot, _ = st.columns([1,1.2,1])
    with col_robot:
        st.markdown('<div class="robot-glow">', unsafe_allow_html=True)
        st.image("robot_khong_nen.gif", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    c1.markdown('<div class="glass-card"><h2>88%</h2><p>Tích cực</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="glass-card"><h2>2,150</h2><p>Thảo luận</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="glass-card"><h2>145ms</h2><p>Tốc độ AI</p></div>', unsafe_allow_html=True)

# =============================
# 💬 CHAT AI
# =============================
elif menu == "💬 Chat AI":

    st.markdown('<h1 class="welcome-text">AI Assistant</h1>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hỏi về Viettel..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            try:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages[-6:]
                )
                reply = res.choices[0].message.content
            except Exception as e:
                reply = f"Lỗi: {e}"

            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

# =============================
# 🎥 YOUTUBE ANALYSIS
# =============================
elif menu == "🎥 YouTube":

    st.markdown('<h1 class="welcome-text">YouTube Analysis</h1>', unsafe_allow_html=True)

    url = st.text_input("🔗 Nhập link YouTube")

    if url:
        clean_url = url.split('&list=')[0]

        with st.spinner("Đang lấy comment..."):
            try:
                downloader = YoutubeCommentDownloader()
                comments = downloader.get_comments_from_url(clean_url, sort_by=SORT_BY_POPULAR)
            except Exception as e:
                st.error(f"Lỗi: {e}")
                st.stop()

        data = []
        for i, c in enumerate(comments):
            if i >= 40:
                break
            text = c.get("text", "")
            data.append({
                "User": c.get("author", ""),
                "Comment": text,
                "Sentiment": analyze_sentiment(text)
            })

        df = pd.DataFrame(data)

        if df.empty:
            st.warning("Không có dữ liệu")
            st.stop()

        col1, col2 = st.columns([2,1])

        with col1:
            fig = px.pie(df, names="Sentiment", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.metric("Comments", len(df))

        st.dataframe(df, use_container_width=True)