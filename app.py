import streamlit as st
import pandas as pd
import feedparser
import google.generativeai as genai
from bs4 import BeautifulSoup 
from urllib.parse import quote
import time

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao" 

try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Başlatma xətası: {e}")

st.set_page_config(page_title="Forex Deep Pro", page_icon="💹", layout="wide")

def deep_ai_logic(title, summary_html):
    """Mətnin cəmini analiz edir"""
    # HTML təmizləmə
    soup = BeautifulSoup(summary_html, "html.parser")
    clean_text = soup.get_text()
    
    # AI üçün geniş kontekst yaradırıq
    full_context = f"Başlıq: {title}\nDetallar: {clean_text}"
    
    prompt = f"""
    Sən peşəkar Forex analitikisən. Aşağıdakı mətnə əsasən dərin analiz et:
    "{full_context}"
    
    Tapşırıq:
    1. Qərar: LONG, SHORT və ya NEYTRAL? (Mətndəki 'bullish', 'bearish', 'sell', 'buy' sözlərinə diqqət yetir).
    2. İzah: Azərbaycan dilində 1 cümləlik texniki səbəb.
    3. Səviyyələr: Varsa qiymətlər, yoxsa 'Məqalədə qeyd edilməyib'.
    
    Format: [QƏRAR] | [İZAH] | [SƏVİYYƏ]
    """
    try:
        response = ai_model.generate_content(prompt)
        res = response.text
        parts = res.split("|")
        
        decision = "🟡 NEYTRAL"
        if "LONG" in parts[0].upper() or "🟢" in parts[0]: decision = "🟢 LONG"
        elif "SHORT" in parts[0].upper() or "🔴" in parts[0]: decision = "🔴 SHORT"
        
        reason = parts[1].strip() if len(parts) > 1 else "Trend analizi."
        levels = parts[2].strip() if len(parts) > 2 else "Tapılmadı."
        
        return decision, reason, levels
    except:
        return None, None, None

# --- UI ---
st.title("💹 Forex Deep AI: Professional Analiz")
st.markdown("Bu sistem hər bir analizin xülasəsini dərindən emal edərək mütləq bir nəticə çıxarır.")

if st.button('Dərin Analizləri Gətir'):
    # Daha geniş axtarış sorğuları (məlumatın gəlməsi üçün)
    sources = [
        ("DailyForex", "dailyforex.com", "forex analysis"),
        ("FXStreet", "fxstreet.com", "technical forecast"),
        ("Investing", "investing.com", "forex technical analysis")
    ]
    
    all_results = []
    placeholder = st.empty()
    
    with st.spinner("Məlumatlar toplanır və AI tərəfindən oxunur..."):
        for src_name, site_url, query in sources:
            rss_url = f"https://news.google.com/rss/search?q={quote('site:'+site_url+' '+query)}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:8]:
                decision, reason, levels = deep_ai_logic(entry.title, entry.summary)
                
                if decision:
                    all_results.append({
                        "Mənbə": src_name,
                        "Başlıq": entry.title.split(" - ")[0],
                        "Qərar": decision,
                        "AI Şərhi": reason,
                        "Səviyyələr": levels,
                        "Link": entry.link
                    })
    
    if all_results:
        df = pd.DataFrame(all_results)
        st.subheader("📊 Bazarın Ümumi Görünüşü")
        st.dataframe(df[['Mənbə', 'Başlıq', 'Qərar']], use_container_width=True)
        
        st.subheader("🔍 Detallı AI Hesabatları")
        for item in all_results:
            with st.expander(f"{item['Qərar']} | {item['Başlıq']}"):
                st.write(f"**Mənbə:** {item['Mənbə']}")
                st.info(f"**AI Təhlili:** {item['AI Şərhi']}")
                st.warning(f"**Qiymət Səviyyələri:** {item['Səviyyələr']}")
                st.link_button("Mənbəni Orijinalda Oxu", item['Link'])
    else:
        st.error("Xəta: Heç bir analiz tapılmadı. Zəhmət olmasa axtarış sözlərini və ya interneti yoxlayın.")

st.sidebar.markdown("---")
st.sidebar.caption("Yalnız təlimat məqsədi daşıyır. Ticarət risklidir.")
    
