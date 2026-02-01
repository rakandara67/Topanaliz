import streamlit as st
import pandas as pd
import feedparser
import google.generativeai as genai
from urllib.parse import quote
import time
import random

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao" 

try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Xətası: {e}")

st.set_page_config(page_title="Forex Deep AI (No Block)", page_icon="🛡️", layout="wide")

def get_deep_analysis_from_snippet(title, summary):
    """Sayta girmədən, mövcud geniş xülasəni analiz edir"""
    prompt = f"""
    Sən peşəkar Forex analitikisən. Aşağıdakı məlumatlar müxtəlif saytların analizləridir:
    BAŞLIQ: {title}
    XÜLASƏ: {summary}
    
    Tapşırıq:
    1. Bu məlumatlara əsasən istiqaməti təyin et: LONG, SHORT və ya NEYTRAL?
    2. Azərbaycan dilində çox qısa (maks 10 söz) izah yaz.
    3. Əgər mətndə konkret qiymət yoxdursa, başlığa və xülasəyə əsasən cari trend səviyyəsini təxmin et.
    
    Format: [QƏRAR] | [İZAH] | [SƏVİYYƏ]
    """
    try:
        response = ai_model.generate_content(prompt)
        res = response.text
        parts = res.split("|")
        
        decision = "🟡 NEYTRAL"
        if "LONG" in parts[0].upper(): decision = "🟢 LONG"
        elif "SHORT" in parts[0].upper(): decision = "🔴 SHORT"
        
        reason = parts[1].strip() if len(parts) > 1 else "Trend analizi."
        levels = parts[2].strip() if len(parts) > 2 else "Müəyyən edilmədi."
        
        return decision, reason, levels
    except:
        return None, None, None

# --- UI ---
st.title("🛡️ Bloklanmayan Dərin AI Analiz")
st.markdown("Bu versiya saytlara birbaşa daxil olmur (bloklanmamaq üçün), Google-un məlumat bazasından istifadə edərək analiz edir.")

if st.button('Analizləri Bir-Bir Gətir (Güvənli Metod)'):
    # Google News RSS-i bir az daha geniş xülasə verən formata salırıq
    sources = [
        ("DailyForex", "dailyforex.com", "forex signals technical"),
        ("FXStreet", "fxstreet.com", "price action forecast"),
        ("TradingView", "tradingview.com", "gold eurusd analysis")
    ]
    
    container = st.container()
    total_count = 0
    
    for src_name, site_url, query in sources:
        # 'ceid=US:en' yerinə 'hl=en-US' istifadə edirik ki, daha çox ingilisdilli məzmun gəlsin
        url = f"https://news.google.com/rss/search?q={quote('site:'+site_url+' '+query)}&hl=en-US&gl=US"
        feed = feedparser.parse(url)
        
        for entry in feed.entries[:10]:
            # Hər birini tək-tək və fərqli vaxtda göstəririk
            time.sleep(random.uniform(0.2, 0.8))
            
            # Google RSS-in 'summary' hissəsində çox vaxt maraqlı detallar olur
            # Onu təmizləyirik
            clean_summary = BeautifulSoup(entry.summary, "html.parser").text if 'summary' in entry else ""
            
            decision, reason, levels = get_deep_analysis_from_snippet(entry.title, clean_summary)
            
            if decision:
                total_count += 1
                with container:
                    with st.expander(f"{decision} | {entry.title.split(' - ')[0]}", expanded=True):
                        st.markdown(f"**Mənbə:** `{src_name}`")
                        st.info(f"**AI Təhlili:** {reason}")
                        st.warning(f"**Təxmini Səviyyələr:** {levels}")
                        st.link_button("Mənbəyə keçid", entry.link)

    if total_count == 0:
        st.error("Məlumat tapılmadı. Zəhmət olmasa API açarını və ya axtarış sözlərini yoxlayın.")
    else:
        st.balloons()
        
