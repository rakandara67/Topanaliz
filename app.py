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
    st.error(f"AI Konfiqurasiya xətası: {e}")

st.set_page_config(page_title="Deep Forex 10", page_icon="📈", layout="wide")

def get_content_force(url):
    """Məqalənin daxilinə mütləq daxil olur və mətni çəkir"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Reklamları və lazımsız hissələri təmizləyirik
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            paragraphs = soup.find_all('p')
            full_text = " ".join([p.get_text() for p in paragraphs])
            
            # Əgər mətn çox qısadırsa (bloklanmışıqsa)
            if len(full_text) < 200:
                return None
            return full_text[:4000] # Gemini-yə göndərilən maksimum limit
    except:
        return None
    return None

def get_deep_ai_decision(content):
    """Yalnız mətn əsasında dərin analiz"""
    prompt = f"""
    Sən peşəkar Forex treyderisən. Aşağıdakı TAM analizi oxu:
    
    "{content}"
    
    Tapşırıq:
    1. Bu mətndə konkret bir istiqamət varmı? (LONG, SHORT və ya NEYTRAL)
    2. Səbəbi Azərbaycan dilində izah et.
    3. Giriş (Entry), Stop Loss (SL) və Take Profit (TP) qiymətlərini mətndən tap.
    
    Cavabı bu formatda yaz:
    QƏRAR: [LONG/SHORT/NEYTRAL]
    İZAH: [Səbəb]
    SƏVİYYƏLƏR: [Qiymətlər]
    """
    try:
        response = ai_model.generate_content(prompt)
        res = response.text
        
        decision = "🟡 NEYTRAL"
        if "LONG" in res.upper(): decision = "🟢 LONG"
        elif "SHORT" in res.upper(): decision = "🔴 SHORT"
        
        summary = res.split("İZAH:")[1].split("SƏVİYYƏLƏR:")[0].strip() if "İZAH:" in res else "Analiz tamamlandı."
        levels = res.split("SƏVİYYƏLƏR:")[1].strip() if "SƏVİYYƏLƏR:" in res else "Tapılmadı."
        
        return decision, summary, levels
    except:
        return None, None, None

def fetch_data(source, site_url, query):
    encoded_query = quote(f"site:{site_url} {query}")
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    return feed.entries[:10] # Hər mənbədən 10 ədəd

# --- INTERFACE ---
st.title("🧠 Deep AI: 10 Analizin Tam Mətn Təhlili")
st.markdown("Bu sistem başlıqlara baxmır, məqalələri bir-bir daxilinə girib oxuyur.")

if st.button('10 Analizi Dərindən Oxu və Analiz Et'):
    sources = [
        ("DailyForex", "dailyforex.com", "forex signals forecast"),
        ("FXStreet", "fxstreet.com", "technical analysis price"),
        ("TradingView", "tradingview.com", "technical analysis eurusd xauusd")
    ]
    
    all_results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Bütün entry-ləri toplayırıq
    total_entries = []
    for src, url, q in sources:
        entries = fetch_data(src, url, q)
        for e in entries:
            total_entries.append((src, e))
    
    # Analiz prosesi
    total_count = len(total_entries)
    
    for i, (src, entry) in enumerate(total_entries):
        status_text.text(f"Analiz edilir ({i+1}/{total_count}): {entry.title[:50]}...")
        progress_bar.progress((i + 1) / total_count)
        
        # 1. Məqaləni oxu
        content = get_content_force(entry.link)
        
        if content:
            # 2. AI-a göndər
            decision, summary, levels = get_deep_ai_decision(content)
            
            if decision:
                all_results.append({
                    "Mənbə": src,
                    "Başlıq": entry.title.split(" - ")[0],
                    "Qərar": decision,
                    "İzah": summary,
                    "Səviyyələr": levels,
                    "Link": entry.link
                })
        
        time.sleep(0.5) # API və Saytların bloklamaması üçün kiçik fasilə

    status_text.text("Analiz tamamlandı!")
    
    if all_results:
        df = pd.DataFrame(all_results)
        st.subheader("📋 Yekun Strateji Cədvəli")
        st.dataframe(df[['Mənbə', 'Başlıq', 'Qərar']], use_container_width=True)
        
        st.subheader("🔍 Detallı Hesabat (Mətn Analizi)")
        for item in all_results:
            with st.expander(f"{item['Qərar']} | {item['Başlıq']}"):
                st.info(f"**AI Xülasəsi:** {item['İzah']}")
                st.warning(f"**Texniki Səviyyələr:** {item['Səviyyələr']}")
                st.link_button("Mənbəni Oxu", item['Link'])
    else:
        st.error("Məqalələrin daxilinə girmək mümkün olmadı. Zəhmət olmasa bir az sonra yenidən yoxlayın.")
    
