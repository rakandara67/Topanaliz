import streamlit as st
import pandas as pd
import feedparser
import google.generativeai as genai
# VACİB: Aşağıdakı iki sətir xətaları həll edir
import requests
from bs4 import BeautifulSoup 
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

st.set_page_config(page_title="Forex Deep AI (Safe)", page_icon="🛡️", layout="wide")

def get_deep_analysis(title, summary_text):
    """Google-un verdiyi xülasə əsasında analiz edir"""
    prompt = f"""
    Forex analitikisən. Bu məlumatı oxu:
    BAŞLIQ: {title}
    MƏTN: {summary_text}
    
    Tapşırıq:
    1. Qərar: LONG, SHORT və ya NEYTRAL?
    2. Səbəb: Azərbaycan dilində 1 cümlə.
    3. Səviyyələr: Varsa Entry, SL, TP qiymətləri.
    
    Format: [QƏRAR] | [İZAH] | [SƏVİYYƏ]
    """
    try:
        response = ai_model.generate_content(prompt)
        parts = response.text.split("|")
        
        decision = "🟡 NEYTRAL"
        if "LONG" in parts[0].upper(): decision = "🟢 LONG"
        elif "SHORT" in parts[0].upper(): decision = "🔴 SHORT"
        
        reason = parts[1].strip() if len(parts) > 1 else "Trend təhlili."
        levels = parts[2].strip() if len(parts) > 2 else "Məlumat yoxdur."
        
        return decision, reason, levels
    except:
        return None, None, None

# --- İNTERFEYS ---
st.title("🛡️ Bloklanmayan Dərin AI Analiz")
st.info("Bu versiya Google-un təhlükəsiz bazasından istifadə edir və saytlar tərəfindən bloklanmır.")

if st.button('Analizləri Bir-Bir Gətir'):
    sources = [
        ("DailyForex", "dailyforex.com", "forex signals technical"),
        ("FXStreet", "fxstreet.com", "price forecast analysis"),
        ("TradingView", "tradingview.com", "gold eurusd news")
    ]
    
    container = st.container()
    total_count = 0
    
    for src_name, site_url, query in sources:
        # RSS vasitəsilə Google News-dan məlumat alırıq
        rss_url = f"https://news.google.com/rss/search?q={quote('site:'+site_url+' '+query)}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:10]:
            # Hər analiz arası kiçik fasilə
            time.sleep(random.uniform(0.1, 0.4))
            
            # BeautifulSoup xətasını burada həll etdik:
            raw_html = entry.summary if 'summary' in entry else ""
            clean_text = BeautifulSoup(raw_html, "html.parser").get_text()
            
            decision, reason, levels = get_deep_analysis(entry.title, clean_text)
            
            if decision:
                total_count += 1
                with container:
                    with st.expander(f"{decision} | {entry.title.split(' - ')[0]}", expanded=True):
                        st.markdown(f"**Mənbə:** `{src_name}`")
                        st.success(f"**AI Təhlili:** {reason}")
                        st.warning(f"**Təxmini Səviyyələr:** {levels}")
                        st.link_button("Mənbəyə bax", entry.link)

    if total_count == 0:
        st.error("Məlumat tapılmadı. İnternet bağlantısını və ya API açarını yoxlayın.")
    else:
        st.balloons()
        
