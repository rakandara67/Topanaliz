import streamlit as st
import yfinance as yf
import requests
import json

API_KEY = "AIzaSyDkPz1j9fo-gD_j_nE72rUKUs0Mxs8fTdA"

def call_gemini(price, news):
    # Birinci 1.5-flash modelini yoxlayırıq, alınmasa gemini-pro-ya keçirik
    models = ["gemini-1.5-flash", "gemini-pro"]
    
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}
        prompt = f"{price} qiymətinə əsasən qısa Forex analizi ver."
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        res_json = response.json()
        
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
    
    return "Xəta: Heç bir model cavab vermədi. API açarınızı yoxlayın."

st.title("📈 Forex AI: Final Fix")
symbol = st.selectbox("Seçin:", ["EURUSD=X", "GBPUSD=X"])

if st.button('Analiz Et'):
    ticker = yf.Ticker(symbol)
    price = ticker.history(period="1d")['Close'].iloc[-1]
    st.metric("Qiymət", f"{price:.4f}")
    
    result = call_gemini(price, "Bazar analizi")
    st.write(result)
    
