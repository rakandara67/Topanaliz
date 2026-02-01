import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Xətası: {e}")

st.set_page_config(page_title="Forex Intel Pro", page_icon="⚖️", layout="wide")

def deep_ai_logic(news_item):
    """Yahoo-dan gələn xəbər mətnini dərindən analiz edir"""
    context = f"Başlıq: {news_item['title']}\nXülasə: {news_item.get('summary', 'Məlumat yoxdur')}"
    
    prompt = f"""
    Sən peşəkar Forex analitikisən. Aşağıdakı xammal maliyyə məlumatını oxu:
    "{context}"
    
    Tapşırıq:
    1. Qərar: 🟢 LONG, 🔴 SHORT və ya 🟡 NEYTRAL?
    2. İzah: Azərbaycan dilində 1 cümləlik texniki səbəb (məs: 'RSI aşırı alım bölgəsindədir').
    3. Səviyyə: Mətndə hər hansı qiymət hədəfi varsa qeyd et.
    
    Format: [QƏRAR] | [İZAH] | [SƏVİYYƏ]
    """
    try:
        response = ai_model.generate_content(prompt)
        return response.text.split("|")
    except:
        return None

# --- UI ---
st.title("⚖️ Forex Intel Pro: Rəsmi Məlumat Analizi")
st.info("Bu sistem Yahoo Finance-ın rəsmi xəbər lentini dərindən oxuyur. Bloklanma riski yoxdur.")

# Aktiv seçimi
symbol = st.selectbox("Analiz ediləcək cütlük:", 
                     ["EURUSD=X", "GBPUSD=X", "JPY=X", "GC=F (Qızıl)", "CL=F (Neft)"])

if st.button('Dərin Analizi Başlat'):
    with st.spinner('Rəsmi agentliklərin mətni oxunur...'):
        ticker = yf.Ticker(symbol)
        news = ticker.news # Birbaşa rəsmi xəbər lenti
        
        if news:
            reports = []
            for item in news[:8]:
                analysis = deep_ai_logic(item)
                if analysis and len(analysis) >= 2:
                    reports.append({
                        "Qərar": analysis[0].strip(),
                        "Başlıq": item['title'],
                        "AI Şərhi": analysis[1].strip(),
                        "Hədəf": analysis[2].strip() if len(analysis) > 2 else "-",
                        "Link": item['link']
                    })
            
            if reports:
                for rep in reports:
                    with st.expander(f"{rep['Qərar']} | {rep['Başlıq']}"):
                        st.write(f"**AI Analizi:** {rep['AI Şərhi']}")
                        st.warning(f"**Qiymət Səviyyəsi:** {rep['Hədəf']}")
                        st.link_button("Orijinal Mənbə", rep['Link'])
                st.balloons()
            else:
                st.warning("Xəbər mətni AI tərəfindən emal edilə bilmədi.")
        else:
            st.error("Yahoo Finance-dan xəbər lenti alınmadı. Simvolu yoxlayın.")

st.sidebar.caption("Bu versiya heç bir xarici 'scraping' etmir, rəsmi API istifadə edir.")
    
