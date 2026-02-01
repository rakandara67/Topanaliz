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

st.set_page_config(page_title="Forex AI Final", page_icon="🏦")

st.title("🏦 Forex AI: Professional Analyzer")

symbol_map = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "GOLD (Qızıl)": "GC=F",
    "BITCOIN": "BTC-USD"
}

selected = st.selectbox("Aktiv seçin:", list(symbol_map.keys()))
symbol = symbol_map[selected]

if st.button('Dərindən Analiz Et'):
    with st.spinner('Məlumatlar toplanır...'):
        try:
            ticker = yf.Ticker(symbol)
            
            # 1. Qiymət məlumatı
            hist = ticker.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                st.metric(label=f"{selected} Cari Qiymət", value=f"{current_price:.4f}")
            else:
                current_price = "Məlum deyil"

            # 2. Xəbərləri ehtiyatlı şəkildə çəkirik
            news = ticker.news
            context = ""
            
            if news and len(news) > 0:
                for n in news[:5]:
                    # 'title' və ya 'summary' yoxdursa xəta verməməsi üçün .get() istifadə edirik
                    t = n.get('title', 'Başlıqsız xəbər')
                    s = n.get('summary', n.get('description', 'Xülasə yoxdur'))
                    context += f"Xəbər: {t}\nDetallar: {s}\n\n"
            
            if not context:
                context = "Hazırda bu aktiv üçün xüsusi xəbər tapılmadı, lakin ümumi bazar trendini analiz et."

            # 3. AI Analizi
            prompt = f"""
            Sən peşəkar Forex analitikisən.
            Aktiv: {selected} ({symbol})
            Cari Qiymət: {current_price}
            
            Son Bazar Məlumatları:
            {context}
            
            Tapşırıq (Azərbaycan dilində cavab ver):
            1. Sentiment: 🟢 LONG, 🔴 SHORT və ya 🟡 NEYTRAL?
            2. Texniki İzah: Bu qərara niyə gəldiyini 1-2 cümlə ilə izah et.
            3. Səviyyələr: Cari qiymətə əsasən Entry, Stop Loss (SL) və Take Profit (TP) rəqəmlərini təyin et.
            """
            
            response = model.generate_content(prompt)
            
            st.markdown("---")
            st.markdown(response.text)
            st.balloons()

        except Exception as e:
            st.error(f"Analiz zamanı gözlənilməz xəta: {str(e)}")
            st.info("İpucu: Bir neçə saniyə gözləyib yenidən yoxlayın.")
            
