import streamlit as st
import pandas as pd
import feedparser
import google.generativeai as genai
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

st.set_page_config(page_title="Forex Live Deep AI", page_icon="🔥", layout="wide")

def get_content_carefully(url):
    """Məqaləni tək-tək və ehtiyatla oxuyur"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Lazımsız reklamları silirik
            for s in soup(['script', 'style', 'aside']): s.decompose()
            paragraphs = soup.find_all('p')
            text = " ".join([p.get_text() for p in paragraphs if len(p.get_text()) > 40])
            return text[:4000] if len(text) > 300 else None
    except:
        return None
    return None

def analyze_individually(content):
    """Tək mətn əsasında dərin AI analizi"""
    prompt = f"""
    Aşağıdakı Forex analizini oxu və qərar ver:
    "{content}"
    
    Format:
    QƏRAR: [LONG, SHORT və ya NEYTRAL]
    SƏBƏB: [1 cümlə Azərbaycan dilində]
    SƏVİYYƏLƏR: [Entry, SL, TP qiymətləri]
    """
    try:
        response = ai_model.generate_content(prompt)
        res = response.text
        decision = "🟡 NEYTRAL"
        if "LONG" in res.upper(): decision = "🟢 LONG"
        elif "SHORT" in res.upper(): decision = "🔴 SHORT"
        
        reason = res.split("SƏBƏB:")[1].split("SƏVİYYƏLƏR:")[0].strip() if "SƏBƏB:" in res else "Analiz olundu."
        levels = res.split("SƏVİYYƏLƏR:")[1].strip() if "SƏVİYYƏLƏR:" in res else "Tapılmadı."
        return decision, reason, levels
    except:
        return None, None, None

# --- UI İNTERFEYS ---
st.title("🔥 Canlı Forex AI Analizi")
st.markdown("Analizlər tək-tək oxunur və tapılan kimi dərhal aşağıda görünür.")

if st.button('Analizləri Bir-Bir Gətir'):
    sources = [
        ("DailyForex", "dailyforex.com", "forex signals forecast"),
        ("FXStreet", "fxstreet.com", "price forecast analysis"),
        ("TradingView", "tradingview.com", "technical analysis eurusd xauusd")
    ]
    
    # Boş bir yer yaradırıq ki, analizlər bura dolsun
    container = st.container()
    
    total_found = 0
    
    for src_name, site_url, query in sources:
        with st.status(f"{src_name} mənbəsindən analizlər çəkilir...", expanded=False):
            feed = feedparser.parse(f"https://news.google.com/rss/search?q={quote('site:'+site_url+' '+query)}&hl=en-US&gl=US&ceid=US:en")
            entries = feed.entries[:10]
        
        for entry in entries:
            # Hər məqaləni emal etməzdən əvvəl bir az gözləyirik (bloklanmamaq üçün)
            time.sleep(random.uniform(1, 3))
            
            content = get_content_carefully(entry.link)
            
            if content:
                decision, reason, levels = analyze_individually(content)
                
                if decision:
                    total_found += 1
                    # Canlı olaraq container-ə əlavə edirik
                    with container:
                        with st.expander(f"{decision} | {entry.title.split(' - ')[0]}", expanded=True):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**Mənbə:** {src_name}")
                                st.success(f"**AI Təhlili:** {reason}")
                                st.warning(f"**Qiymət Səviyyələri:** `{levels}`")
                            with col2:
                                st.link_button("Məqaləni Aç", entry.link)
    
    if total_found == 0:
        st.error("Heç bir dərin analiz tapılmadı. Saytlar hələ də girişi bloklayır.")
    else:
        st.balloons()
    
