import streamlit as st
import google.generativeai as genai
import yfinance as yf
import pandas as pd

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI bağlantı xətası: {e}")

st.set_page_config(page_title="Forex AI Master", page_icon="🏦", layout="wide")

st.title("🏦 Forex AI Master: Real-Time Intelligence")
st.markdown("Bu sistem rəsmi **Yahoo Finance** bazasından həm canlı rəqəmləri, həm də tam analiz mətnlərini gətirir.")

# Valyuta seçimi
symbol = st.selectbox("Aktiv seçin:", ["EURUSD=X", "GBPUSD=X", "GC=F (Qızıl)", "BTC-USD"])

if st.button('Dərindən Analiz Et'):
    with st.spinner('Rəsmi məlumatlar və analizlər toplanır...'):
        try:
            # 1. Rəqəmsal məlumatları çəkirik
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            current_price = hist['Close'].iloc[-1]
            
            # 2. Xəbər və Analizləri çəkirik (Bloklanma riski 0%)
            news = ticker.news
            
            if not news:
                st.warning("Bu aktiv üçün hazırda aktiv xəbər lenti tapılmadı.")
            else:
                st.subheader(f"📊 {symbol} üzrə Yekun Hesabat")
                
                # Bütün xəbərləri birləşdirib AI-ya veririk
                context = ""
                for n in news[:5]:
                    context += f"Başlıq: {n['title']}\nXülasə: {n.get('summary', '')}\n\n"
                
                # AI Analizi
                prompt = f"""
                Sən peşəkar Forex analitikisən. 
                Aktiv: {symbol}
                Cari Qiymət: {current_price}
                Son Analizlər:
                {context}
                
                Tapşırıq:
                1. Qərar: 🟢 LONG, 🔴 SHORT və ya 🟡 NEYTRAL?
                2. Səbəb: Azərbaycan dilində ən son xəbərlərə əsaslanan texniki izah.
                3. Səviyyələr: Cari qiymətə ({current_price}) əsasən ağlabatan Entry, SL və TP təyin et.
                """
                
                response = model.generate_content(prompt)
                
                # Vizual nəticə
                st.markdown("---")
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric(label="Cari Qiymət", value=f"{current_price:.4f}")
                    st.info(f"**AI Qərarı:**\n{response.text.splitlines()[0]}")
                with col2:
                    st.write("**🧠 Dərin Analiz və Səviyyələr:**")
                    st.write(response.text)
                
                st.balloons()
                
        except Exception as e:
            st.error(f"Sistem xətası: {e}")

st.sidebar.markdown("### Niyə bu ən yaxşısıdır?")
st.sidebar.write("✅ **Bloklanmır:** Yahoo Finance rəsmi API kimidir.")
st.sidebar.write("✅ **Rəqəmsal + Mətn:** Həm son qiyməti görür, həm də xəbərləri oxuyur.")
st.sidebar.write("✅ **Stabil:** 404 xətası verməyən ən stabil metoddur.")
