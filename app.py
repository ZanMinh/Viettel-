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
# STYLE
# =============================
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
background: url("app/static/background_ai.png") no-repeat center center fixed;
background-size: cover;
}

[data-testid="stAppViewContainer"]{
background: rgba(0,0,0,0.65);
backdrop-filter: blur(3px);
}

[data-testid="stSidebar"]{
background: rgba(0,0,0,0.45);
backdrop-filter: blur(20px);
}

/* TITLE */
.welcome-text {
text-align:center;
font-size:3rem !important;
font-weight:800;
background: linear-gradient(135deg,#ff0026,#ffffff);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
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
margin-bottom:20px;
}

/* STATS */
.stat-card{
background: rgba(255,255,255,0.05);
padding:25px;
border-radius:16px;
text-align:center;
transition:0.25s;
}

.stat-card:hover{
transform: translateY(-8px);
box-shadow:0 20px 40px rgba(255,0,0,0.25);
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

/* AI LOADER */
.ai-loader{
display:flex;
justify-content:center;
align-items:center;
flex-direction:column;
padding:40px 0;
}

.ai-brain{
width:70px;
height:70px;
border-radius:50%;
background: radial-gradient(circle,#ff0026,#330000);
box-shadow:0 0 30px #ff0026;
animation:pulseAI 1.5s infinite ease-in-out;
}

.ai-text{
margin-top:12px;
font-size:14px;
opacity:0.8;
}

@keyframes pulseAI{
0%{transform:scale(1);box-shadow:0 0 10px #ff0026;}
50%{transform:scale(1.15);box-shadow:0 0 40px #ff0026;}
100%{transform:scale(1);box-shadow:0 0 10px #ff0026;}
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
<div style="text-align:center;margin-bottom:20px">
<svg width="180" viewBox="0 0 512 128">
<defs>
<linearGradient id="viettelGrad" x1="0" y1="0" x2="1" y2="1">
<stop offset="0%" stop-color="#ff0026"/>
<stop offset="100%" stop-color="#ff4d4d"/>
</linearGradient>
</defs>

<text x="50%" y="60%" text-anchor="middle"
font-size="48"
font-weight="700"
fill="url(#viettelGrad)">
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

    tab1, tab2 = st.tabs(["Đăng nhập","Đăng ký"])

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

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =============================
# SIDEBAR
# =============================
with st.sidebar:

    st.image("robot_khong_nen.gif", use_container_width=True)

    menu = st.radio("Menu", ["🏠 Trang chủ","💬 Chat AI","🎥 YouTube"])

    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.token = None
        st.rerun()

# =============================
# HOME
# =============================
if menu == "🏠 Trang chủ":

    st.markdown('<h1 class="welcome-text">Viettel AI Dashboard</h1>', unsafe_allow_html=True)

    st.markdown("""
<div class="hero-box">
<h2>🚀 Nền tảng AI nội bộ Viettel</h2>
<p>Chat AI • Phân tích YouTube • Dashboard Realtime • Sentiment AI</p>
</div>
""", unsafe_allow_html=True)

    col1,col2 = st.columns([1.2,1])

    with col1:
        st.markdown("""
### 🤖 Hệ thống AI Viettel

- Phân tích comment YouTube  
- Chat AI nội bộ  
- Dashboard realtime  
- Sentiment AI  
""")

    with col2:
        st.image("robot_khong_nen.gif")

    st.markdown("### 📊 Tổng quan")

    c1,c2,c3,c4 = st.columns(4)

    c1.markdown('<div class="stat-card"><div class="big-number">88%</div><div class="sub-text">Sentiment</div></div>',unsafe_allow_html=True)
    c2.markdown('<div class="stat-card"><div class="big-number">2,150</div><div class="sub-text">Comments</div></div>',unsafe_allow_html=True)
    c3.markdown('<div class="stat-card"><div class="big-number">145ms</div><div class="sub-text">Latency</div></div>',unsafe_allow_html=True)
    c4.markdown('<div class="stat-card"><div class="big-number">4</div><div class="sub-text">Modules</div></div>',unsafe_allow_html=True)

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

            loader = st.empty()

            loader.markdown("""
            <div class="ai-loader">
            <div class="ai-brain"></div>
            <div class="ai-text">AI Viettel đang suy nghĩ...</div>
            </div>
            """, unsafe_allow_html=True)

            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages[-6:]
            )

            reply = res.choices[0].message.content

            loader.empty()
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
        comments = downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR)

        data=[]
        for i,c in enumerate(comments):
            if i>=40:
                break

            text=c.get("text","")

            data.append({
                "Comment":text,
                "Sentiment":analyze_sentiment(text)
            })

        df=pd.DataFrame(data)

        fig=px.pie(df,names="Sentiment",hole=0.4)
        st.plotly_chart(fig,use_container_width=True)

        st.dataframe(df,use_container_width=True)