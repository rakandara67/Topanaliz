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
    st.error(f"AI Konfiqurasiya xətası: {e}")

st.set_page_config(page_title="Forex Deep 10 Pro", page_icon="🧠", layout="wide")

def get_content_smart(url):
    """Bloklanmadan məqalə mətni çəkir"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    ]
    try:
        # Hər dəfə fərqli User-Agent istifadə edərək saytı aldadırıq
        headers = {'User-Agent': random.choice(user_agents)}
        response = requests.get(url, headers=headers, timeout=12)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Yalnız əsas məqalə gövdəsini tapmağa çalışırıq
            paragraphs = soup.find_all('p')
            text = " ".join([p.get_text() for p in paragraphs if len(p.get_text()) > 50])
            return text[:4500] if len(text) > 200 else None
    except:
        return None
    return None

def ai_deep_analyze(content):
    """Mətni oxuyub LONG/SHORT təyin edir"""
    prompt = f"""
    Sən peşəkar treyder və analitikisən. Aşağıdakı analizi TAM OXU:
    "{content}"
    
    TƏLƏB:
    1. Qərar: LONG, SHORT və ya NEYTRAL? (Mətndəki texniki göstəricilərə əsaslan).
    2. Səbəb: Azərbaycan dilində 1 cümləlik çox konkret izah.
    3. Səviyyələr: Varsa Entry, SL, TP qiymətlərini çıxar.
    
    Format: [QƏRAR] | [İZAH] | [SƏVİYYƏLƏR]
    """
    try:
        response = ai_model.generate_content(prompt)
        parts = response.text.split("|")
        
        decision_raw = parts[0].upper()
        decision = "🟡 NEYTRAL"
        if "LONG" in decision_raw: decision = "🟢 LONG"
        elif "SHORT" in decision_raw: decision = "🔴 SHORT"
        
        summary = parts[1].strip() if len(parts) > 1 else "Analiz dərindən emal edildi."
        levels = parts[2].strip() if len(parts) > 2 else "Mətndə konkret rəqəm tapılmadı."
        
        return decision, summary, levels
    except:
        return None, None, None

# --- UI ---
st.title("🧠 Deep AI: 10 Analizin Tam Təhlili")
st.info("Sistem başlıqlara baxmır, 30-a yaxın məqalənin daxilinə girib real siqnalları axtarır.")

if st.button('Analizi Başlat (Dərin Axtarış)'):
    sources = [
        ("DailyForex", "dailyforex.com", "forex signals technical analysis"),
        ("FXStreet", "fxstreet.com", "price forecast today"),
        ("TradingView", "tradingview.com", "eurusd gold analysis")
    ]
    
    all_results = []
    progress = st.progress(0)
    status = st.empty()
    
    # Bütün linkləri toplayırıq
    entries_to_process = []
    for src, url, q in sources:
        feed = feedparser.parse(f"https://news.google.com/rss/search?q={quote('site:'+url+' '+q)}&hl=en-US&gl=US&ceid=US:en")
        for e in feed.entries[:10]:
            entries_to_process.append((src, e))

    total = len(entries_to_process)
    
    for i, (src, entry) in enumerate(entries_to_process):
        status.text(f"Məqalə oxunur ({i+1}/{total}): {entry.title[:45]}...")
        progress.progress((i + 1) / total)
        
        # 1. Sayta daxil ol
        full_text = get_content_smart(entry.link)
        
        if full_text:
            # 2. AI Analizi
            decision, summary, levels = ai_deep_analyze(full_text)
            if decision:
                all_results.append({
                    "Mənbə": src,
                    "Başlıq": entry.title.split(" - ")[0],
                    "Qərar": decision,
                    "İzah": summary,
                    "Səviyyələr": levels,
                    "Link": entry.link
                })
        
        # BLOKLANMAMAQ ÜÇÜN VACİB: Hər məqalə arası təsadüfi fasilə
        time.sleep(random.uniform(0.5, 1.5))

    status.success(f"Analiz tamamlandı! {len(all_results)} dərin analiz tapıldı.")
    
    if all_results:
        df = pd.DataFrame(all_results)
        st.subheader("📋 AI Siqnal Cədvəli")
        st.dataframe(df[['Mənbə', 'Başlıq', 'Qərar']], use_container_width=True)
        
        for item in all_results:
            with st.expander(f"{item['Qərar']} | {item['Başlıq']}"):
                st.markdown(f"**AI Təhlili:** {item['İzah']}")
                st.code(f"Texniki Səviyyələr: {item['Səviyyələr']}")
                st.link_button("Mənbəni Aç", item['Link'])
    else:
        st.error("Saytlar girişi blokladı. Zəhmət olmasa 5-10 dəqiqə sonra yenidən yoxlayın.")
    
