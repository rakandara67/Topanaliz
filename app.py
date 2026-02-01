import streamlit as st
import feedparser
import requests

# --- KONFİQURASİYA ---
# API açarınızın düzgünlüyündən əmin olun
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

def get_ai_analysis(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    prompt = f"Sən peşəkar tradersən. Bu analizi Azərbaycan dilində xülasə et. Trend (Long/Short), Entry, SL və TP nöqtələrini aydın göstər: {text}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=15)
        res_json = response.json()
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"API Mesajı: {res_json.get('error', {}).get('message', 'Nəticə tapılmadı')}"
    except Exception as e:
        return f"Bağlantı xətası: {str(e)}"

st.set_page_config(page_title="Forex AI Final", layout="wide")

st.title("🏆 Forex AI: Populyar Analiz Hub")

symbol = st.selectbox("Aktiv seçin:", ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "ETHUSD"])

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🔥 Son 10 Populyar Analiz")
    rss_url = f"https://www.tradingview.com/feed/?symbol={symbol}"
    feed = feedparser.parse(rss_url)
    
    if feed.entries:
        for i, entry in enumerate(feed.entries[:10], 1):
            with st.expander(f"{i}. {entry.title}"):
                st.write(f"📅 Mənbə: TradingView")
                st.markdown(f"[🔗 Analizi aç və mətni kopyala]({entry.link})")
    else:
        st.info("Hazırda analiz tapılmadı.")

with col2:
    st.subheader("🤖 AI Analizator")
    # Yazı yazılan yer artıq tam aktiv və sərbəstdir
    user_input = st.text_area(
        "Analiz mətnini bura yapışdırın:", 
        height=350, 
        placeholder="TradingView-dan kopyaladığınız mətni bura daxil edin...",
        key="final_input"
    )
    
    if st.button("Analiz et", use_container_width=True):
        if user_input:
            with st.spinner('AI təhlil edir...'):
                result = get_ai_analysis(user_input)
                st.markdown("---")
                st.success("🎯 AI Rəyi:")
                st.write(result)
        else:
            st.warning("Zəhmət olmasa mətn daxil edin.")
            
