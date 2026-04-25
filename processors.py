from transformers import pipeline
import streamlit as st

@st.cache_resource  # Sửa thành dòng này
def load_sentiment_model():
    model_name = "wonrax/phobert-base-vietnamese-sentiment"
    classifier = pipeline("sentiment-analysis", model=model_name)
    return classifier

def analyze_viettel_text(text):
    classifier = load_sentiment_model()
    result = classifier(text)[0]
    
    label_map = {
        'POS': 'Tích cực',
        'NEU': 'Trung lập',
        'NEG': 'Tiêu cực'
    }
    return label_map.get(result['label'], 'Trung lập')
@st.cache_resource  # Giúp tải model nhanh hơn ở những lần sau
def load_sentiment_model():
    # Tải mô hình PhoBERT chuyên cho tiếng Việt
    model_name = "wonrax/phobert-base-vietnamese-sentiment"
    classifier = pipeline("sentiment-analysis", model=model_name)
    return classifier

def analyze_viettel_text(text):
    classifier = load_sentiment_model()
    result = classifier(text)[0]
    
    # Dịch kết quả từ AI sang tiếng Việt
    label_map = {'POS': 'Tích cực', 'NEU': 'Trung lập', 'NEG': 'Tiêu cực'}
    return label_map.get(result['label'], 'Trung lập')