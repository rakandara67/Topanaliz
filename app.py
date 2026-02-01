import streamlit as st
import yfinance as yf
import requests
import json

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

def call_gemini_api(price_data, news_context):
    # Stabil v1 endpointi
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    # AI-nı daha rahat işləməyə təşviq edən prompt
    prompt_text = f"""
    Aşağıdakı Forex məlumatlarını analiz et:
    Aktiv qiyməti: {price_data}
    Xəbər xülasəsi: {news_context}
    
    Zəhmət olmasa Azərbaycan dilində qısa bir texniki rəy ver və 
    ehtimal olunan Entry, Stop Loss və Take Profit səviyyələrini rəqəmlərlə qeyd et.
    """
    
    data = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "safetySettings": [ # Filtrləri minimuma endiririk ki, 'candidates' xətası verməsin
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        res_json = response.json()
        
        # Xətanın diaqnozu üçün yoxlama
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in res_json:
            return f"API Xətası: {res_json['error']['message']}"
        else:
            return f"Gözlənilməz cavab formatı. Detal: {res_json}"
            
    except Exception as e:
        return f"Bağlantı xətası: {str(e)}"

# --- UI ---
st.set_page_config(page_title="Forex AI Final", page_icon="📈")
st.title("📈 Forex AI: Professional Deep Analysis")

pair_map = {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "Qızıl": "GC=F", "Bitcoin": "BTC-USD"}
selected_pair = st.selectbox("Analiz üçün aktiv seçin:", list(pair_map.keys()))

if st.button('Dərin Analizi Başlat'):
    with st.spinner('Bazar datası və AI emal edilir...'):
        # 1. Qiymət çəkmə
        ticker = yf.Ticker(pair_map[selected_pair])
        hist = ticker.history(period="1d")
        
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            st.metric(f"{selected_pair} Qiyməti", f"{price:.4f}")
            
            # 2. Xəbər çəkmə
            news = ticker.news
            context = " ".join([n.get('title', '') for n in news[:3]]) if news else "Xəbər tapılmadı."
            
            # 3. AI Analizi
            st.markdown("---")
            st.subheader("🤖 AI-nın Analitik Rəyi")
            result = call_gemini_api(price, context)
            st.write(result)
        else:
            st.error("Bazar məlumatı tapılmadı.")
