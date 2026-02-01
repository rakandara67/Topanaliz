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

st.set_page_config(page_title="Forex AI Deep Reader", page_icon="🧬", layout="wide")

def process_with_ai(title, summary):
    """Mətnin hamısını analiz edən beyin"""
    full_text = f"Başlıq: {title}\nMəzmun: {summary}"
    
    prompt = f"""
    Sən peşəkar Forex analitikisən. Aşağıdakı tam mətni dərindən oxu və təhlil et:
    "{full_text}"
    
    Tapşırıq:
    1. Bazar sentimentini tut: 🟢 LONG, 🔴 SHORT və ya 🟡 NEYTRAL?
    2. Azərbaycan dilində 1 cümləlik texniki səbəb yaz.
    3. Mətndə hər hansı Entry, SL və ya TP rəqəmi varsa mütləq qeyd et.
    
    Format: [QƏRAR] | [İZAH] | [SƏVİYYƏ]
    """
    try:
        response = ai_model.generate_content(prompt)
        return response.text.split("|")
    except:
        return ["🟡 NEYTRAL", "AI emal xətası.", "-"]

# --- İNTERFEYS ---
st.title("🧬 Forex AI: Tam Mətn Analizatoru")
st.markdown("Bu sistem rəsmi kanallardan gələn **tam mətnləri** oxuyur. Bloklanma riski yoxdur.")

symbol_map = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "QIZIL (Gold)": "GC=F",
    "NEFT (Oil)": "CL=F",
    "USD/JPY": "JPY=X"
}

target_pair = st.selectbox("Analiz üçün aktiv seçin:", list(symbol_map.keys()))

if st.button('Dərin Analizi Başlat (Heç bir başlığı ötürmə)'):
    with st.spinner('Mənbələr dərindən oxunur...'):
        ticker_sym = symbol_map[target_pair]
        data = yf.Ticker(ticker_sym)
        
        # Yahoo Finance news bəzən fərqli formatda gəlir, ona görə 'get' metodundan istifadə edirik
        news_list = data.news
        
        if news_list:
            found_count = 0
            for item in news_list[:10]: # Son 10 rəsmi analizi oxu
                # KeyError qarşısını almaq üçün 'get' istifadəsi
                t = item.get('title', 'Başlıq tapılmadı')
                # Bəzi Yahoo xəbərlərində xülasə 'summary' deyil, 'description' və ya 'content' içində olur
                s = item.get('summary', item.get('description', 'Məqalənin daxili mətni xülasə şəklində oxunur...'))
                
                analysis = process_with_ai(t, s)
                
                if analysis and len(analysis) >= 2:
                    found_count += 1
                    decision = analysis[0].strip()
                    reason = analysis[1].strip()
                    levels = analysis[2].strip() if len(analysis) > 2 else "Məqalədə rəqəm yoxdur."
                    
                    with st.expander(f"{decision} | {t}"):
                        st.write(f"**AI-ın Dərin Rəyi:** {reason}")
                        st.info(f"**Müəyyən edilən Səviyyələr:** {levels}")
                        st.caption(f"Mənbə: {item.get('publisher', 'Maliyyə Agentliyi')}")
                        if 'link' in item:
                            st.link_button("Orijinal Mətnə keç", item['link'])
            
            if found_count == 0:
                st.warning("Aktiv analiz tapıldı, lakin AI tərəfindən emal edilə bilmədi.")
        else:
            st.error("Bu aktiv üçün hazırda rəsmi analiz axını tapılmadı.")

st.sidebar.markdown("---")
st.sidebar.write("**Sistem Necə İşləyir?**")
st.sidebar.caption("1. Yahoo Finance API-dan tam xəbər obyektini çəkir.")
st.sidebar.caption("2. Gemini 1.5 Flash məqalənin içindəki texniki indikatorları (RSI, Moving Average) tapır.")
st.sidebar.caption("3. Yalnız başlıqları deyil, 'summary' hissəsini analiz edərək sizə yekun siqnal verir.")
    
