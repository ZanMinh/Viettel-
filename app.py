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
# USER STORAGE (FIX CHÍNH)
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

# =============================
# LOGIN PAGE
# =============================
if not st.session_state.token:

    st.markdown("## 🔐 Viettel AI Login")

    tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])

    # ===== LOGIN =====
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Mật khẩu", type="password")

        if st.button("Đăng nhập"):
            if email in users and users[email] == hash_pass(password):
                st.session_state.token = email
                st.success("Đăng nhập thành công")
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu")

        st.markdown("---")

        result = oauth2.authorize_button(
            "🔐 Đăng nhập Google",
            redirect_uri="http://localhost:8501",
            scope="openid email profile"
        )

        if result:
            st.session_state.token = result["token"]
            st.rerun()

    # ===== REGISTER =====
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

    st.stop()

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.write(f"👤 {st.session_state.token}")
    menu = st.radio("Menu", ["🏠 Trang chủ", "💬 Chat AI", "🎥 YouTube"])
    st.button("🚪 Đăng xuất", on_click=lambda: st.session_state.update(token=None))

# =============================
# HOME
# =============================
if menu == "🏠 Trang chủ":

    st.title("🤖 Viettel AI Platform")

    col1, col2, col3 = st.columns(3)
    col1.metric("Tích cực", "88%")
    col2.metric("Comments", "2,150")
    col3.metric("Latency", "145ms")

    st.info("🚀 Chat AI | YouTube Analysis | Dashboard")

# =============================
# CHAT AI
# =============================
elif menu == "💬 Chat AI":

    st.title("💬 AI Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hỏi gì đó..."):

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
                    reply = "⚠️ Chưa cấu hình API key"

                st.markdown(reply)

        st.session_state.messages.append({"role":"assistant","content":reply})

# =============================
# YOUTUBE
# =============================
elif menu == "🎥 YouTube":

    st.title("🎥 YouTube Analysis")

    url = st.text_input("Nhập link YouTube")

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