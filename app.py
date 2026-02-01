import streamlit as st
import yfinance as yf
import google.generativeai as genai

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Xətası: {e}")

st.set_page_config(page_title="Forex Deep Intelligence", page_icon="📈", layout="wide")

def deep_ai_reader(title, content):
    """Mətnin hər bir detalını oxuyan AI beyni"""
    if not title or len(title) < 5:
        return None
        
    prompt = f"""
    Sən peşəkar Forex analitikisən. Aşağıdakı maliyyə məlumatını dərindən təhlil et:
    BAŞLIQ: {title}
    MƏZMUN: {content}
    
    Tapşırıq:
    1. Qərar: 🟢 LONG (Alış), 🔴 SHORT (Satış) və ya 🟡 NEYTRAL?
    2. Səbəb: Azərbaycan dilində 1 cümləlik texniki izah.
    3. Səviyyələr: Mətndəki Entry, Stop Loss və Take Profit rəqəmlərini tap və qeyd et.
    
    Format: [QƏRAR] | [İZAH] | [SƏVİYYƏ]
    """
    try:
        response = ai_model.generate_content(prompt)
        parts = response.text.split("|")
        return [p.strip() for p in parts]
    except:
        return None

# --- UI ---
st.title("📈 Forex Deep Intelligence: Full Text Reader")
st.info("Bu sistem rəsmi Yahoo Finance xəbər obyektlərinin daxili mətnlərini AI-ya oxudur.")

pairs = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "QIZIL (Gold)": "GC=F",
    "NEFT (Oil)": "CL=F",
    "USD/JPY": "JPY=X",
    "BITCOIN": "BTC-USD"
}

selected_label = st.selectbox("Analiz üçün aktiv seçin:", list(pairs.keys()))

if st.button('Dərindən Analiz Et'):
    with st.spinner('Maliyyə məlumatları dərindən oxunur...'):
        ticker = yf.Ticker(pairs[selected_label])
        
        try:
            # yfinance xəbərlərini çəkirik
            raw_news = ticker.news
            
            if not raw_news:
                st.warning("Bu aktiv üçün hazırda canlı xəbər axını tapılmadı.")
            else:
                count = 0
                for item in raw_news[:10]:
                    # Məlumatları təhlükəsiz şəkildə çıxarırıq
                    title = item.get('title', '')
                    # Yahoo News-da bəzən 'summary' bəzən 'description' olur
                    summary = item.get('summary', item.get('description', 'Mətn xülasəsi tapılmadı, başlıq əsasında analiz edilir.'))
                    
                    analysis = deep_ai_reader(title, summary)
                    
                    if analysis and len(analysis) >= 2:
                        count += 1
                        decision_text = analysis[0].upper()
                        
                        # Rəng kodlaması
                        icon = "🟡"
                        if "LONG" in decision_text or "🟢" in decision_text: icon = "🟢"
                        elif "SHORT" in decision_text or "🔴" in decision_text: icon = "🔴"
                        
                        with st.expander(f"{icon} {decision_text} | {title[:70]}..."):
                            st.write(f"**🧠 AI Təhlili:** {analysis[1]}")
                            if len(analysis) > 2:
                                st.warning(f"**🎯 Texniki Səviyyələr:** {analysis[2]}")
                            st.markdown(f"*Mənbə: {item.get('publisher', 'Maliyyə Agentliyi')}*")
                            if 'link' in item:
                                st.link_button("Məqalənin tamamını oxu", item['link'])
                
                if count == 0:
                    st.error("Xəbərlər tapıldı, lakin AI tərəfindən emal edilə biləcək kifayət qədər mətn yoxdur.")
                else:
                    st.balloons()
                    
        except Exception as e:
            st.error(f"Məlumat çəkilərkən xəta baş verdi: {e}")

st.sidebar.markdown("---")
st.sidebar.write("**Sistem Necə Analiz Edir?**")
st.sidebar.caption("Sistem başlıqdakı 'Bullish/Bearish' sözlərinə baxmaqla qalmır, xəbərin içindəki iqtisadi şərhləri Gemini 1.5 Flash modelinə göndərir və ondan 'mentally process' etməsini istəyir.")
