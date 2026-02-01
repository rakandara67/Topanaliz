import streamlit as st
import feedparser
import requests

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

def get_ai_analysis(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    prompt = f"Aşağıdakı Forex analizini Azərbaycan dilində xülasə et. Trend, Giriş və SL/TP qeyd et: {text}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "AI təhlili zamanı xəta. Mətni kopyaladığınızdan əmin olun."

st.set_page_config(page_title="TradingView Feed Pro", layout="wide")
st.title("📈 TradingView Canlı Analiz Lenti")

# Aktiv seçimi
symbol = st.selectbox("Aktiv seçin:", ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD"])

# RSS vasitəsilə linkləri gətiririk
if st.button(f"{symbol} Son Analizləri Gətir"):
    with st.spinner('TradingView-dan son məlumatlar alınır...'):
        # TradingView-un rəsmi analiz lenti
        rss_url = f"https://www.tradingview.com/feed/?symbol={symbol}"
        feed = feedparser.parse(rss_url)
        
        if feed.entries:
            st.subheader(f"🔗 {symbol} üçün Son Analizlər:")
            for i, entry in enumerate(feed.entries[:10], 1):
                # Linkləri və başlıqları göstəririk
                st.markdown(f"{i}. **{entry.title}**")
                st.markdown(f"   👉 [Analizə baxmaq üçün klikləyin]({entry.link})")
                st.write("---")
        else:
            st.warning("Hazırda bu aktiv üçün canlı link tapılmadı. Bir az sonra yenidən yoxlayın.")

st.markdown("### 📝 Analiz Edici")
st.info("Yuxarıdakı linklərdən birini açıb mətni bura yapışdırın:")
user_input = st.text_area("Analiz mətni:", height=150)

if st.button("AI Xülasəni Çıxar"):
    if user_input:
        with st.spinner('Analiz edilir...'):
            st.success("🤖 AI-nın Rəyi:")
            st.write(get_ai_analysis(user_input))
            
