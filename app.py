import streamlit as st
from googlesearch import search
import requests
import json

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

def get_ai_summary(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    prompt = f"Aşağıdakı Forex analizini Azərbaycan dilində 3 bəndlə xülasə et (Trend, Səviyyələr, Qərar): {text}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "AI təhlili zamanı xəta baş verdi."

st.set_page_config(page_title="TradingView Analiz Hub", layout="wide")
st.title("📈 TradingView Analiz Mərkəzi")

pair = st.selectbox("Aktiv seçin:", ["EURUSD", "GBPUSD", "GOLD", "BTCUSD"])

# 1. LİNKLƏRİN TAPILMASI
if st.button(f"{pair} üçün son analizləri tap"):
    with st.spinner('TradingView bazası yoxlanılır...'):
        query = f"site:tradingview.com {pair} technical analysis today"
        links = list(search(query, num_results=10))
        
        st.subheader(f"🔗 {pair} üçün Son 10 Analiz Linki:")
        for i, link in enumerate(links, 1):
            st.markdown(f"{i}. [Analizi Aç: {link.split('/')[-2]}]({link})")

st.markdown("---")

# 2. ANALİZ EDİCİ (Kopyala-Yapışdır hissəsi)
st.subheader("📝 Seçdiyiniz Analizin Sürətli Xülasəsi")
st.info("Yuxarıdakı linklərdən birini açın, mətni kopyalayıb aşağıya yapışdırın.")

user_text = st.text_area("Analiz mətnini bura daxil edin:", height=150)

if st.button("AI Xülasəni Çıxar"):
    if user_text:
        with st.spinner('AI oxuyur...'):
            summary = get_ai_summary(user_text)
            st.success("✅ AI-nın Yekun Rəyi:")
            st.write(summary)
    else:
        st.warning("Zəhmət olmasa əvvəlcə mətni yapışdırın.")
        
