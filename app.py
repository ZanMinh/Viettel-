import streamlit as st
from openai import OpenAI
import pandas as pd
import plotly.express as px
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from streamlit_oauth import OAuth2Component

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="Viettel AI Platform", layout="wide", page_icon="🤖")

# =============================
# API KEY
# =============================
API_KEY = st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY) if API_KEY else None

# =============================
# GOOGLE LOGIN
# =============================
CLIENT_ID = st.secrets.get("G_CLIENT_ID")
CLIENT_SECRET = st.secrets.get("G_CLIENT_SECRET")

oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    "https://accounts.google.com/o/oauth2/v2/auth",
    "https://oauth2.googleapis.com/token",
    "https://openidconnect.googleapis.com/v1/userinfo",
)

# =============================
# STYLE
# =============================
st.markdown("""
<style>
.stApp {
    background: #020617;
    color: #f8fafc;
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
</style>
""", unsafe_allow_html=True)

# =============================
# SENTIMENT
# =============================
def analyze_sentiment(text):
    text = text.lower()
    if any(w in text for w in ["tốt", "hay", "ok", "good", "đỉnh"]):
        return "Tích cực"
    elif any(w in text for w in ["tệ", "chán", "dở", "bad"]):
        return "Tiêu cực"
    return "Trung lập"

# =============================
# LOGIN STATE
# =============================
if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None

# database user giả
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "admin": "123456"
    }

# =============================
# LOGIN PAGE
# =============================
if not st.session_state.token and not st.session_state.user:

    st.markdown('<h1 class="welcome-text">Viettel AI Platform</h1>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔐 Google", "👤 Đăng nhập", "📝 Đăng ký"])

    # GOOGLE LOGIN
    with tab1:
        result = oauth2.authorize_button(
            "🔑 Đăng nhập với Google",
            redirect_uri="http://localhost:8501",
            scope="openid email profile"
        )

        if result:
            st.session_state.token = result["token"]
            st.rerun()

    # LOGIN ACCOUNT
    with tab2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Đăng nhập"):
            if username in st.session_state.users_db and \
               st.session_state.users_db[username] == password:
                st.session_state.user = username
                st.success("Đăng nhập thành công")
                st.rerun()
            else:
                st.error("Sai tài khoản")

    # REGISTER
    with tab3:
        new_user = st.text_input("Username mới")
        new_pass = st.text_input("Password mới", type="password")

        if st.button("Tạo tài khoản"):
            if new_user in st.session_state.users_db:
                st.warning("User đã tồn tại")
            else:
                st.session_state.users_db[new_user] = new_pass
                st.success("Tạo tài khoản thành công")

    st.stop()

# =============================
# SIDEBAR
# =============================
with st.sidebar:

    if st.button("🚪 Đăng xuất"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

    st.markdown("---")

    menu = st.radio("Menu", ["🏠 Trang chủ", "💬 Chat AI", "🎥 YouTube"])

# =============================
# HOME
# =============================
if menu == "🏠 Trang chủ":

    st.markdown('<h1 class="welcome-text">Xin chào 👋</h1>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    c1.markdown('<div class="glass-card"><h2>88%</h2><p>Tích cực</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="glass-card"><h2>2,150</h2><p>Thảo luận</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="glass-card"><h2>145ms</h2><p>Tốc độ AI</p></div>', unsafe_allow_html=True)

# =============================
# CHAT AI
# =============================
elif menu == "💬 Chat AI":

    st.title("AI Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Hỏi về Viettel..."):

        st.session_state.messages.append({"role":"user","content":prompt})

        with st.chat_message("assistant"):
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages[-6:]
            )
            reply = res.choices[0].message.content
            st.write(reply)

        st.session_state.messages.append({"role":"assistant","content":reply})

# =============================
# YOUTUBE
# =============================
elif menu == "🎥 YouTube":

    st.title("YouTube Analysis")

    url = st.text_input("🔗 Nhập link YouTube")

    if url:

        downloader = YoutubeCommentDownloader()
        comments = downloader.get_comments_from_url(
            url,
            sort_by=SORT_BY_POPULAR
        )

        data = []
        for i, c in enumerate(comments):
            if i >= 40:
                break

            text = c.get("text", "")

            data.append({
                "Comment": text,
                "Sentiment": analyze_sentiment(text)
            })

        df = pd.DataFrame(data)

        fig = px.pie(df, names="Sentiment", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True)