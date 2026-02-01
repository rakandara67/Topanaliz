import streamlit as st
import pandas as pd
import feedparser
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import time

# --- KONFİQURASİYA ---
API_KEY = "SİZİN_API_AÇARINIZ" 

try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Başlatma Xətası: {e}")

st.set_page_config(page_title="Forex Deep AI", page_icon="🧠", layout="wide")

def get_full_article_content(url):
    """Məqalənin içini oxuyur"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        # İlk 8 paraqrafı götürürük ki, AI-a çox yük düşməsin
        text = " ".join([p.get_text() for p in paragraphs[:8]])
        return text.strip()[:2500] 
    except:
        return ""

def get_deep_ai_analysis(title, content):
    """Mətnin hamısını analiz edir və xətalara qarşı davamlıdır"""
    source_text = content if len(content) > 100 else title
    
    prompt = f"""
    Sən peşəkar Forex analitikisən. Aşağıdakı analizi oxu və konkret istiqamət müəyyən et:
    "{source_text}"
    
    Tapşırıq:
    1. Qərar (Yalnız biri): LONG, SHORT, NEYTRAL.
    2. Səbəb (Azərbaycan dilində 1 cümlə).
    3. Tapılan Səviyyələr (Giriş, TP, SL - varsa).
    
    Cavabı MÜTLƏQ bu formatda ver:
    Qərar: [LONG/SHORT/NEYTRAL]
    Xülasə: [İzahın]
    Səviyyə: [Qiymətlər]
    """
    try:
        response = ai_model.generate_content(prompt)
        res = response.text
        
        # Xətanın qarşısını almaq üçün təhlükəsiz parçalama
        decision = "🟡 NEYTRAL"
        if "LONG" in res.upper(): decision = "🟢 LONG"
        elif "SHORT" in res.upper(): decision = "🔴 SHORT"
        
        summary = "Analiz olundu."
        if "Xülasə:" in res:
            summary = res.split("Xülasə:")[1].split("\n")[0].strip()
            
        levels = "Qeyd edilməyib"
        if "Səviyyə:" in res:
            levels = res.split("Səviyyə:")[1].strip()
            
        return decision, summary, levels
    except:
        return "🟡 NEYTRAL", "AI cavab verə bilmədi.", "Yoxdur"

def fetch_and_analyze(source, site_url, query):
    encoded_query = quote(f"site:{site_url} {query}")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    results = []
    # TradingView üçün mənasız linkləri filtr edirik
    junk = ["chart", "index", "rates", "quotes", "market", "page"]
    
    for entry in feed.entries[:6]:
        title = entry.title
        if source == "TradingView" and any(x in title.lower() for x in junk):
            continue
            
        with st.spinner(f"AI oxuyur: {title[:40]}..."):
            full_text = get_full_article_content(entry.link)
            decision, summary, levels = get_deep_ai_analysis(title, full_text)
            
            results.append({
                "Mənbə": source,
                "Başlıq": title.split(" - ")[0],
                "Qərar": decision,
                "İzah": summary,
                "Səviyyələr": levels,
                "Link": entry.link
            })
            time.sleep(0.5) # Limitə düşməmək üçün
    return results

# --- INTERFACE ---
st.title("🧠 Deep AI Forex Analitik")
st.markdown("Bu versiya məqalələri tam oxuyur və **Entry/TP/SL** səviyyələrini axtarır.")

if st.button('Dərin Analizi Başlat'):
    sources = [
        ("DailyForex", "dailyforex.com", "forex signals technical analysis"),
        ("FXStreet", "fxstreet.com", "forex price forecast"),
        ("TradingView", "tradingview.com", "technical analysis gold eurusd")
    ]
    
    all_data = []
    for src, url, q in sources:
        all_data.extend(fetch_and_analyze(src, url, q))
        
    if all_data:
        df = pd.DataFrame(all_data)
        st.subheader("📊 Canlı Strateji Cədvəli")
        st.dataframe(df[['Mənbə', 'Başlıq', 'Qərar']], use_container_width=True)
        
        st.subheader("🔍 Detallı AI Hesabatları")
        for item in all_data:
            with st.expander(f"{item['Qərar']} | {item['Başlıq']}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**AI Təhlili:** {item['İzah']}")
                    st.write(f"**Qiymət Səviyyələri:** `{item['Səviyyələr']}`")
                with col2:
                    st.link_button("Məqaləni tam oxu", item['Link'])
    else:
        st.warning("Heç bir analiz tapılmadı.")
    
