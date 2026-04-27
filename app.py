import streamlit as st
from openai import OpenAI
import pandas as pd
import plotly.express as px
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from streamlit_oauth import OAuth2Component
import json, os, hashlib

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
# USER SYSTEM (FIXED)
# =============================
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

users = load_users()

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
# STYLE (GIỮ NGUYÊN CỦA BẠN)
# =============================
st.markdown("""
<style>
.stApp {
    background: url("app/static/background_ai.png") no-repeat center center fixed;
    background-size: cover;
    color: #f8fafc;
}

[data-testid="stAppViewContainer"]{
    background: rgba(0,0,0,0.65);
    backdrop-filter: blur(3px);
}

[data-testid="stHeader"]{
    background: transparent;
}

[data-testid="stSidebar"]{
    background: rgba(0,0,0,0.5);
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

.hero-box{
    background: linear-gradient(135deg, rgba(255,0,0,0.15), rgba(255,255,255,0.02));
    border-radius:20px;
    padding:30px;
    backdrop-filter: blur(20px);
    border:1px solid rgba(255,255,255,0.05);
}

.stat-card{
    background: rgba(255,255,255,0.05);
    padding:25px;
    border-radius:16px;
    text-align:center;
}

.stat-card:hover{
    transform: translateY(-5px);
}

.big-number{
    font-size:32px;
    font-weight:700;
    color:#ff4d4d;
}

.sub-text{
    opacity:0.7;
}

.login-box{
    width:420px;
    margin:auto;
    margin-top:60px;
    padding:40px;
    background: rgba(255,255,255,0.05);
    border-radius:20px;
}
</style>
""", unsafe_allow_html=True)

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
# SESSION
# =============================
if "token" not in st.session_state:
    st.session_state.token = None

# =============================
# LOGIN PAGE (FIXED LOGIC ONLY)
# =============================
if not st.session_state.token:

    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center'>Viettel AI Login</h2>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])

    # ================= LOGIN =================
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Mật khẩu", type="password")

        if st.button("Đăng nhập"):
            if email in users and users[email] == hash_pass(password):
                st.session_state.token = email
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu")

        st.markdown("---")

        result = oauth2.authorize_button(
            "🔐 Google Login",
            redirect_uri="http://localhost:8501",
            scope="openid email profile"
        )

        if result:
            st.session_state.token = result["token"]
            st.rerun()

    # ================= REGISTER =================
    with tab2:
        new_email = st.text_input("Email đăng ký")
        new_pass = st.text_input("Mật khẩu đăng ký", type="password")

        if st.button("Tạo tài khoản"):
            if not new_email or not new_pass:
                st.warning("Nhập đầy đủ thông tin")
            elif new_email in users:
                st.error("Email đã tồn tại")
            else:
                users[new_email] = hash_pass(new_pass)
                save_users(users)
                st.success("Tạo tài khoản thành công")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =============================
# SIDEBAR (GIỮ NGUYÊN UI BẠN)
# =============================
with st.sidebar:

    st.image("robot_khong_nen.gif")

    menu = st.radio("Menu", ["🏠 Trang chủ", "💬 Chat AI", "🎥 YouTube"])

    st.markdown("---")

    st.button("🚪 Đăng xuất", on_click=lambda: st.session_state.update(token=None))

# =============================
# HOME (GIỮ NGUYÊN UI BẠN)
# =============================
if menu == "🏠 Trang chủ":

    st.markdown('<h1 class="welcome-text">Viettel AI Platform</h1>', unsafe_allow_html=True)

    st.markdown('<div class="hero-box">', unsafe_allow_html=True)

    col1,col2 = st.columns([1.2,1])

    with col1:
        st.markdown("""
### 🤖 AI Platform Viettel

- Phân tích sentiment AI  
- Chat AI nội bộ  
- Dashboard dữ liệu realtime  
- Phân tích YouTube comment  
- Viettel NLP Engine  
""")

    with col2:
        st.image("robot_khong_nen.gif")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 📊 Tổng quan")

    c1,c2,c3,c4 = st.columns(4)

    c1.markdown('<div class="stat-card"><div class="big-number">88%</div><div class="sub-text">Tích cực</div></div>', unsafe_allow_html=True)
    c2.markdown('<div class="stat-card"><div class="big-number">2,150</div><div class="sub-text">Comments</div></div>', unsafe_allow_html=True)
    c3.markdown('<div class="stat-card"><div class="big-number">145ms</div><div class="sub-text">Latency</div></div>', unsafe_allow_html=True)
    c4.markdown('<div class="stat-card"><div class="big-number">4</div><div class="sub-text">AI Modules</div></div>', unsafe_allow_html=True)

    st.markdown("### 🚀 Modules AI")

    m1,m2,m3 = st.columns(3)

    with m1:
        st.info("💬 Chat AI Viettel")

    with m2:
        st.success("🎥 YouTube Analysis")

    with m3:
        st.warning("📊 Dashboard BI")

# =============================
# CHAT AI (GIỮ NGUYÊN)
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

            with st.spinner("AI đang trả lời..."):

                if client:
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=st.session_state.messages[-6:]
                    )
                    reply = res.choices[0].message.content
                else:
                    reply = "Chưa có API key"

                st.markdown(reply)

        st.session_state.messages.append({"role":"assistant","content":reply})

# =============================
# YOUTUBE (GIỮ NGUYÊN)
# =============================
elif menu == "🎥 YouTube":

    st.markdown('<h1 class="welcome-text">YouTube Analysis</h1>', unsafe_allow_html=True)

    url = st.text_input("🔗 Nhập link YouTube")

    if url:

        downloader = YoutubeCommentDownloader()
        comments = downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR)

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