import streamlit as st
import pandas as pd
import feedparser
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Forex Analiz Pro", layout="wide")

def analyze_signal(text):
    """Mətndən Long/Short qərarını və xülasəni çıxarır"""
    text = text.lower()
    
    # Açar sözlər
    long_patterns = [r'bullish', r'buy', r'long', r'yükseliş', r'artış', r'destek', r'alım']
    short_patterns = [r'bearish', r'sell', r'short', r'düşüş', r'gerileme', r'direnç', r'satış']
    
    is_long = any(re.search(p, text) for p in long_patterns)
    is_short = any(re.search(p, text) for p in short_patterns)
    
    if is_long:
        return "🟢 LONG (Alış)", "Analiz qiymətlərin artacağını və alış təzyiqinin güclü olduğunu göstərir."
    elif is_short:
        return "🔴 SHORT (Satış)", "Analiz qiymətlərin enəcəyini və satış təzyiqinin artdığını göstərir."
    else:
        return "🟡 NEYTRAL", "Bazar hazırda qeyri-müəyyəndir, konkret istiqamət siqnalı yoxdur."

def get_dailyforex():
    # RSS bloklanmır və daha sürətlidir
    feed_url = "https://www.dailyforex.com/forex-technical-analysis/rss"
    feed = feedparser.parse(feed_url)
    results = []
    
    for entry in feed.entries[:10]:
        qerar, xulasa = analyze_signal(entry.title + " " + entry.description)
        results.append({
            "Mənbə": "DailyForex",
            "Analiz": entry.title,
            "Qərar": qerar,
            "Xülasə (AZ)": xulasa,
            "Link": entry.link
        })
    return results

def get_fxstreet():
    url = "https://www.fxstreet.com.tr/analysis/latest"
    headers = {'User-Agent': 'Mozilla/5.0'}
    results = []
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.content, 'html.parser')
        # FXStreet TR-nin xüsusi strukturu
        items = soup.find_all('h4', class_='fxs_headline_tiny')
        
        for item in items[:10]:
            a_tag = item.find('a')
            if a_tag:
                title = a_tag.text.strip()
                link = a_tag['href']
                qerar, xulasa = analyze_signal(title)
                results.append({
                    "Mənbə": "FXStreet TR",
                    "Analiz": title,
                    "Qərar": qerar,
                    "Xülasə (AZ)": xulasa,
                    "Link": link
                })
    except:
        pass
    return results

# UI
st.title("📊 Forex Analiz: Long/Short Qərarları")

if st.button('Məlumatları Yenilə və Analiz Et'):
    with st.spinner('Canlı analizlər toplanır...'):
        all_data = get_dailyforex() + get_fxstreet()
        
        if all_data:
            df = pd.DataFrame(all_data)
            
            # Cədvəl görünüşü
            st.subheader("📌 Son 20 Analiz İcmalı")
            st.table(df[['Mənbə', 'Analiz', 'Qərar']])
            
            # Detallı Kartlar
            st.subheader("📝 Detallı Xülasələr")
            for item in all_data:
                with st.expander(f"{item['Qərar']} | {item['Mənbə']}: {item['Analiz']}"):
                    st.write(f"**Vəziyyət:** {item['Xülasə (AZ)']}")
                    st.write(f"[Mənbəyə keçid]({item['Link']})")
        else:
            st.error("Məlumat tapılmadı. Zəhmət olmasa bir az sonra yenidən cəhd edin.")
        
