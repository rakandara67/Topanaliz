import streamlit as st
import google.generativeai as genai
import yfinance as yf

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

def get_ai_analysis(price, context):
    try:
        # Xətanın qarşısını almaq üçün birbaşa stabil model təyin edirik
        genai.configure(api_key=API_KEY)
        # 'models/' prefiksi olmadan yoxlayırıq
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Forex Analizi:
        Aktivin cari qiyməti: {price}
        Son xəbərlər: {context}
        
        Tapşırıq (Azərbaycan dilində):
        1. Qərar (AL/SAT/GÖZLƏ)
        2. Texniki səbəb
        3. Entry, SL və TP səviyyələri.
        """
        # 'v1beta' xətasından qaçmaq üçün ən sadə çağırış
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI xətası: {str(e)}"

st.set_page_config(page_title="Forex AI Final", page_icon="🏦")
st.title("🏦 Forex AI: Ultra Stable")

symbol_map = {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "GOLD": "GC=F"}
selected = st.selectbox("Aktiv:", list(symbol_map.keys()))

if st.button('Analizi Başlat'):
    with st.status("Məlumatlar emal edilir...") as status:
        ticker = yf.Ticker(symbol_map[selected])
        
        # Qiyməti çəkirik
        hist = ticker.history(period="1d")
        price = hist['Close'].iloc[-1] if not hist.empty else "Bilinmir"
        st.metric("Cari Qiymət", f"{price}")
        
        # Xəbərləri çəkirik
        news = ticker.news
        context_text = ""
        if news:
            for n in news[:3]:
                context_text += f"{n.get('title', '')}. "
        
        # AI-ya müraciət
        status.write("AI təhlil aparır...")
        result = get_ai_analysis(price, context_text)
        
        st.markdown("---")
        st.write(result)
        status.update(label="Tamamlandı!", state="complete")
        
