import streamlit as st
import yfinance as yf
import requests
import json

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

def call_gemini_api(price_data, news_context):
    """SDK istifadə etmədən birbaşa v1 qapısına sorğu göndərir"""
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    prompt_text = f"""
    Sən peşəkar Forex analitikisən. 
    Cari qiymət: {price_data}
    Xəbərlər: {news_context}
    
    Tapşırıq: Azərbaycan dilində qısa analiz, AL/SAT tövsiyəsi və Entry, SL, TP səviyyələrini yaz.
    """
    
    data = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        res_json = response.json()
        # AI-nın cavabını JSON içindən çıxarırıq
        return res_json['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Bağlantı xətası: {str(e)}"

# --- UI ---
st.set_page_config(page_title="Forex AI Pro", page_icon="📈")
st.title("📈 Forex AI: Direct API Access")
st.info("Bu versiya SDK xətalarını yan keçmək üçün birbaşa Google serverlərinə qoşulur.")

symbol = st.selectbox("Aktiv seçin:", ["EURUSD=X", "GBPUSD=X", "GC=F"])

if st.button('Analiz Et'):
    with st.spinner('Məlumatlar gətirilir...'):
        # 1. Qiymət və Xəbər (İşləyən hissə)
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        price = hist['Close'].iloc[-1] if not hist.empty else "N/A"
        
        news = ticker.news
        context = " ".join([n.get('title', '') for n in news[:3]])
        
        st.metric("Canlı Qiymət", f"{price:.4f}")
        
        # 2. AI Analizi (REST API vasitəsilə)
        st.subheader("AI-nın Dərin Analizi")
        analysis = call_gemini_api(price, context)
        st.write(analysis)
        st.balloons()
        
