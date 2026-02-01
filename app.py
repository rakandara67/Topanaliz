import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Forex Analiz Pro", layout="wide")

def get_signal(title, desc=""):
    """Başlıq və xülasəyə əsasən siqnal təyin edir"""
    text = (title + " " + desc).lower()
    buy_words = ['bullish', 'artış', 'yükseliş', 'long', 'destek', 'alım', 'al']
    sell_words = ['bearish', 'düşüş', 'short', 'direnç', 'satış', 'sat']
    
    if any(word in text for word in buy_words):
        return "🟢 LONG (Alış Meyilli)"
    elif any(word in text for word in sell_words):
        return "🔴 SHORT (Satış Meyilli)"
    return "🟡 NEYTRAL / Gözlə"

def get_dailyforex():
    url = "https://www.dailyforex.com/forex-technical-analysis/page-1"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        # DailyForex bəzən cookies tələb edir, session istifadə edək
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        analizler = []
        
        # Selector-u daha ümumi tutaq
        items = soup.select('div.daily-analysis-item') or soup.select('article')
        
        for item in items[:10]:
            title_el = item.find('h2') or item.find('h3')
            link_el = item.find('a')
            if title_el and link_el:
                title = title_el.text.strip()
                link = "https://www.dailyforex.com" + link_el['href'] if not link_el['href'].startswith('http') else link_el['href']
                analizler.append({
                    "Mənbə": "DailyForex",
                    "Analiz": title,
                    "Siqnal": get_signal(title),
                    "Link": link
                })
        return analizler
    except:
        return []

def get_fxstreet():
    url = "https://www.fxstreet.com.tr/analysis/latest"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        analizler = []
        items = soup.select('h4.fxs_headline_tiny') or soup.find_all('h4')
        
        for item in items[:10]:
            link_el = item.find('a')
            if link_el:
                title = link_el.text.strip()
                analizler.append({
                    "Mənbə": "FXStreet TR",
                    "Analiz": title,
                    "Siqnal": get_signal(title),
                    "Link": link_el['href']
                })
        return analizler
    except:
        return []

st.title("📊 Forex Analiz və Siqnallar")

if st.sidebar.button('Məlumatları Yenilə'):
    with st.spinner('Məlumatlar hər iki saytdan çəkilir...'):
        data = get_dailyforex() + get_fxstreet()
        
        if data:
            df = pd.DataFrame(data)
            # Cədvəl görünüşü
            st.dataframe(df[['Mənbə', 'Analiz', 'Siqnal']], use_container_width=True)
            
            # Detallı xülasə hissəsi
            st.subheader("📝 Analiz Detalları")
            for item in data:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{item['Mənbə']}**: {item['Analiz']}")
                with col2:
                    st.info(item['Siqnal'])
                st.write(f"[Məqaləyə keçid]({item['Link']})")
                st.divider()
        else:
            st.error("Xəta: Saytlara qoşulmaq mümkün olmadı. Zəhmət olmasa bir az sonra yenidən yoxlayın.")
else:
    st.info("Sol paneldəki 'Yenilə' düyməsinə basaraq ən son 20 analizi (10+10) görə bilərsiniz.")
    
