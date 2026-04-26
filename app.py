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
# LOAD STYLE
# =============================
st.markdown("""
<style>

/* BACKGROUND FULL */
.stApp {
    background: url("app/static/background_ai.png") no-repeat center center fixed;
    background-size: cover;
}

/* overlay */
[data-testid="stAppViewContainer"] {
    background: rgba(0,0,0,0.65);
    backdrop-filter: blur(3px);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.4);
    backdrop-filter: blur(20px);
}

.welcome-text {
    text-align: center;
    font-size: 3rem !important;
    font-weight: 800;
    background: linear-gradient(135deg, #ee0000, #ffffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* LOGIN */
.login-box{
    width:420px;
    margin:auto;
    margin-top:60px;
    padding:40px;
    background: rgba(255,255,255,0.05);
    border-radius:20px;
    backdrop-filter: blur(20px);
    box-shadow:0 0 40px rgba(255,0,0,0.2);
}

.viettel-logo{
    text-align:center;
    margin-bottom:15px;
}

.divider{
    text-align:center;
    margin:20px 0;
    opacity:0.6;
}

/* HERO */
.hero-box{
    background: linear-gradient(135deg, rgba(255,0,0,0.15), rgba(255,255,255,0.02));
    border-radius:20px;
    padding:30px;
    backdrop-filter: blur(20px);
    border:1px solid rgba(255,255,255,0.05);
}

/* STATS */
.stat-card{
    background: rgba(255,255,255,0.05);
    padding:25px;
    border-radius:16px;
    text-align:center;
    transition:0.2s;
}

.stat-card:hover{
    transform: translateY(-5px);
    box-shadow:0 10px 30px rgba(255,0,0,0.2);
}

.big-number{
    font-size:32px;
    font-weight:700;
    color:#ff4d4d;
}

.sub-text{
    opacity:0.7;
    margin-top:5px;
}

/* chat box */
.stChatInputContainer > div {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 30px;
    backdrop-filter: blur(10px);
}

</style>
""", unsafe_allow_html=True)

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
# SENTIMENT
# =============================
def analyze_sentiment(text):
    text = text.lower()
    if any(w in text for w in ["tốt","hay","ok","good","đỉnh"]):
        return "Tích cực"
    elif any(w in text for w in ["tệ","chán","dở","bad"]):
        return "Tiêu cực"
    return "Trung lập"

# =============================
# LOGIN STATE
# =============================
if "token" not in st.session_state:
    st.session_state.token = None

if "users" not in st.session_state:
    st.session_state.users = {}

# =============================
# LOGIN PAGE
# =============================
if not st.session_state.token:

    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.markdown("""
    <div class="viettel-logo">
    <svg viewBox="0 0 400 120" xmlns="http://www.w3.org/2000/svg">
    <defs>
    <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#ff0000"/>
    <stop offset="100%" stop-color="#ffffff"/>
    </linearGradient>
    </defs>

    <text x="50%" y="55%" text-anchor="middle"
    font-size="48"
    font-weight="700"
    fill="url(#g1)">
    VIETTEL
    </text>

    <text x="50%" y="90%"
    text-anchor="middle"
    font-size="14"
    fill="#aaa">
    AI PLATFORM
    </text>
    </svg>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])

    with tab1:

        email = st.text_input("Email")
        password = st.text_input("Mật khẩu", type="password")

        if st.button("Đăng nhập"):
            if email in st.session_state.users and st.session_state.users[email] == password:
                st.session_state.token = email
                st.rerun()
            else:
                st.error("Sai tài khoản")

        st.markdown('<div class="divider">Hoặc</div>', unsafe_allow_html=True)

        result = oauth2.authorize_button(
            "🔑 Đăng nhập bằng Google",
            redirect_uri="http://localhost:8501",
            scope="openid email profile"
        )

        if result:
            st.session_state.token = result["token"]
            st.rerun()

    with tab2:

        new_email = st.text_input("Email đăng ký")
        new_pass = st.text_input("Mật khẩu đăng ký", type="password")

        if st.button("Tạo tài khoản"):
            st.session_state.users[new_email] = new_pass
            st.success("Tạo tài khoản thành công")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =============================
# SIDEBAR
# =============================
with st.sidebar:

    st.image("robot_khong_nen.gif", use_container_width=True)

    if st.button("🚪 Đăng xuất"):
        st.session_state.token = None
        st.rerun()

    menu = st.radio("Menu", ["🏠 Trang chủ", "💬 Chat AI", "🎥 YouTube"])

# =============================
# HOME
# =============================
if menu == "🏠 Trang chủ":

    st.markdown('<h1 class="welcome-text">Viettel AI Dashboard</h1>', unsafe_allow_html=True)

    st.markdown('<div class="hero-box">', unsafe_allow_html=True)

    col1, col2 = st.columns([1.2,1])

    with col1:
        st.markdown("""
        ### 🤖 AI Phân tích dữ liệu Viettel
        
        - Phân tích comment YouTube  
        - Chat AI nội bộ  
        - Dashboard realtime  
        - Sentiment AI  
        """)

    with col2:
        st.image("robot_khong_nen.gif", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 📊 Tổng quan hệ thống")

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown("""
    <div class="stat-card">
    <div class="big-number">88%</div>
    <div class="sub-text">Sentiment tích cực</div>
    </div>
    """, unsafe_allow_html=True)

    c2.markdown("""
    <div class="stat-card">
    <div class="big-number">2,150</div>
    <div class="sub-text">Thảo luận</div>
    </div>
    """, unsafe_allow_html=True)

    c3.markdown("""
    <div class="stat-card">
    <div class="big-number">145ms</div>
    <div class="sub-text">Tốc độ AI</div>
    </div>
    """, unsafe_allow_html=True)

    c4.markdown("""
    <div class="stat-card">
    <div class="big-number">4</div>
    <div class="sub-text">Modules AI</div>
    </div>
    """, unsafe_allow_html=True)

# =============================
# CHAT AI
# =============================
elif menu == "💬 Chat AI":

    st.markdown('<h1 class="welcome-text">AI Assistant</h1>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hỏi về Viettel..."):

        st.session_state.messages.append({"role":"user","content":prompt})

        with st.chat_message("assistant"):
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages[-6:]
            )

            reply = res.choices[0].message.content
            st.markdown(reply)

        st.session_state.messages.append({"role":"assistant","content":reply})

# =============================
# YOUTUBE
# =============================
elif menu == "🎥 YouTube":

    st.markdown('<h1 class="welcome-text">YouTube Analysis</h1>', unsafe_allow_html=True)

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