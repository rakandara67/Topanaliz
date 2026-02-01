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
    st.error(f"AI Xətası: {e}")

st.set_page_config(page_title="Deep AI Forex Analiz", page_icon="🧠", layout="wide")

def get_full_article_content(url):
    """Linkə daxil olur və analizin mətnini çəkir"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Saytdakı əsas mətn bloklarını tapırıq (p teqləri)
        paragraphs = soup.find_all('p')
        full_text = " ".join([p.get_text() for p in paragraphs[:10]]) # İlk 10 paraqraf bəs edir
        return full_text[:3000] # Gemini-ni yormamaq üçün limit
    except:
        return ""

def get_deep_ai_analysis(title, content):
    """Mətnin hamısını oxuyub qərar verir"""
    if not content:
        return "🟡 NEYTRAL", "Məzmun oxuna bilmədi."

    prompt = f"""
    Sən peşəkar Forex analitikisən. Aşağıdakı analizi TAM oxu:
    BAŞLIQ: {title}
    MƏTN: {content}
    
    Tapşırıq:
    1. Analizin nəticəsini tap: LONG (Alış), SHORT (Satış) yoxsa NEYTRAL?
    2. Giriş (Entry), Stop Loss və Take Profit səviyyələri qeyd olunubsa tap.
    3. Azərbaycan dilində 1-2 cümləlik çox konkret xülasə yaz.
    
    Format:
    QƏRAR: [LONG/SHORT/NEYTRAL]
    XÜLASƏ: [İzah]
    SƏVİYYƏLƏR: [Varsa qiymətlər, yoxsa 'Yoxdur']
    """
    try:
        response = ai_model.generate_content(prompt)
        res = response.text
        
        decision = "🟡 NEYTRAL"
        if "LONG" in res.upper(): decision = "🟢 LONG"
        elif "SHORT" in res.upper(): decision = "🔴 SHORT"
        
        summary = res.split("XÜLASƏ:")[1].split("SƏVİYYƏLƏR:")[0].strip() if "XÜLASƏ:" in res else "Analiz olundu."
        levels = res.split("SƏVİYYƏLƏR:")[1].strip() if "SƏVİYYƏLƏR:" in res else "Tapılmadı."
        
        return decision, summary, levels
    except:
        return "🟡 NEYTRAL", "AI xətası.", "Yoxdur"

def fetch_and_analyze(source, site_url, query):
    encoded_query = quote(f"site:{site_url} {query}")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    results = []
    for entry in feed.entries[:5]: # Hər mənbədən 5 dənə (Daha dərindir deyə az götürürük)
        with st.spinner(f"Oxunur: {entry.title[:30]}..."):
            full_content = get_full_article_content(entry.link)
            decision, summary, levels = get_deep_ai_analysis(entry.title, full_content)
            
            results.append({
                "Mənbə": source,
                "Başlıq": entry.title.split(" - ")[0],
                "Qərar": decision,
                "AI Xülasə": summary,
                "Səviyyələr": levels,
                "Link": entry.link
            })
    return results

# --- UI ---
st.title("🧠 Deep AI: Tam Mətn Analizi")

if st.button('Məqalələri İçindən Oxu və Analiz Et'):
    all_data = []
    sources = [
        ("DailyForex", "dailyforex.com", "forex signals"),
        ("FXStreet", "fxstreet.com", "technical analysis"),
        ("TradingView", "tradingview.com", "eurusd gold analysis")
    ]
    
    for src, url, q in sources:
        all_data.extend(fetch_and_analyze(src, url, q))
        
    if all_data:
        df = pd.DataFrame(all_data)
        st.subheader("📋 Dərin Analiz Nəticələri")
        st.dataframe(df[['Mənbə', 'Başlıq', 'Qərar']], use_container_width=True)
        
        st.subheader("🔍 Detallı Hesabat")
        for item in all_data:
            with st.expander(f"{item['Qərar']} | {item['Başlıq']}"):
                st.write(f"**Mənbə:** {item['Mənbə']}")
                st.info(f"**AI Təhlili:** {item['AI Xülasə']}")
                st.warning(f"**Qiymət Səviyyələri:** {item['Səviyyələr']}")
                st.link_button("Mənbəni Aç", item['Link'])
                
