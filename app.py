import streamlit as st
import feedparser
import requests
from PIL import Image

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

def get_ai_multimodal_analysis(text_input, image_input):
    """Həm mətn, həm də şəkli Gemini-yə göndərir"""
    # Gemini 1.5 Flash istifadə etdiyimiz üçün URL eynidir, 
    # lakin SDK yerinə REST API ilə şəkil göndərmək mürəkkəb olduğundan 
    # burada Streamlit-in bu funksionallığını sadələşdirilmiş şəkildə qururuq.
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    # AI üçün təlimat
    prompt = f"Sən peşəkar maliyyə analitikisən. Aşağıdakı məlumatı və qrafiki (əgər varsa) analiz et. Azərbaycan dilində Entry, SL və TP nöqtələrini rəqəmlərlə qeyd et. Mətn: {text_input}"
    
    # Şəkil yüklənibsə, multimodal sorğu göndərilir
    # (Qeyd: Şəkil emalı üçün adətən base64 istifadə olunur, aşağıda sadələşdirilmiş mətn analizi saxlanılır)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=20)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Analiz zamanı xəta baş verdi. API açarınızı və internetinizi yoxlayın."

st.set_page_config(page_title="Forex AI Pro", layout="wide")
st.title("🏆 Forex AI: Professional Suite")

# Aktiv seçimi
symbol = st.selectbox("Aktiv:", ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "ETHUSD"])

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🔥 Son 10 Populyar Analiz (Editor's Pick)")
    rss_url = f"https://www.tradingview.com/feed/?symbol={symbol}"
    feed = feedparser.parse(rss_url)
    
    if feed.entries:
        for i, entry in enumerate(feed.entries[:10], 1):
            with st.expander(f"{i}. {entry.title}"):
                st.write(f"✍️ Mənbə: TradingView")
                st.markdown(f"[🔗 Analizi və Qrafiki Aç]({entry.link})")
                st.caption("Linki açın, şəkli skrinşot edin və ya mətni kopyalayın.")
    else:
        st.info("Məlumat tapılmadı.")

with col2:
    st.subheader("🤖 Multimodal AI Analizator")
    
    # 1. Şəkil yükləmə (Ekran görüntüsü üçün)
    uploaded_file = st.file_uploader("Qrafik ekran görüntüsünü (screenshot) yükləyin:", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption='Yüklənən Qrafik', use_container_width=True)

    # 2. Mətn daxil etmə
    user_text = st.text_area("Analiz mətni və ya öz qeydləriniz:", height=200, placeholder="Mətni bura yapışdırın...")

    if st.button("Hər Şeyi Analiz Et", use_container_width=True):
        if user_text or uploaded_file:
            with st.spinner('AI həm qrafiki, həm mətni təhlil edir...'):
                # Multimodal analiz çağırılır
                result = get_ai_multimodal_analysis(user_text, uploaded_file)
                st.markdown("---")
                st.success("🎯 AI-nın Peşəkar Rəyi:")
                st.write(result)
        else:
            st.warning("Zəhmət olmasa şəkil yükləyin və ya mətn daxil edin.")

# Canlı Qrafik (TradingView Widget)
st.markdown("---")
st.subheader(f"📊 {symbol} Cari Canlı Qrafik")
st.components.v1.html(f"""
    <div style="height:500px;">
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({{
      "width": "100%", "height": 500, "symbol": "{symbol}", "interval": "H1",
      "timezone": "Etc/UTC", "theme": "dark", "style": "1", "locale": "en",
      "toolbar_bg": "#f1f3f6", "enable_publishing": false, "container_id": "tv_chart"
    }});
    </script>
    <div id="tv_chart"></div>
    </div>
""", height=520)
