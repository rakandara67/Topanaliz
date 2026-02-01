import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(page_title="Forex Analiz Xülasəsi", layout="wide")

def get_dailyforex():
    url = "https://www.dailyforex.com/forex-technical-analysis/page-1"
    # Saytın bizi bloklamaması üçün daha geniş headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        analizler = []
        
        # DailyForex-in ən son strukturu: adətən 'article' və ya spesifik class-lar
        items = soup.find_all('div', class_='daily-analysis-item')
        if not items: # Alternativ struktur yoxlaması
            items = soup.select('.analysis-list-item') or soup.find_all('article')

        for item in items[:10]:
            title_el = item.find('h2') or item.find('h3')
            link_el = item.find('a')
            if title_el and link_el:
                title = title_el.text.strip()
                link = "https://www.dailyforex.com" + link_el['href'] if not link_el['href'].startswith('http') else link_el['href']
                
                analizler.append({
                    "Mənbə": "DailyForex",
                    "Analiz": title,
                    "Link": link
                })
        return analizler
    except Exception as e:
        return [{"Mənbə": "DailyForex", "Analiz": f"Xəta: {e}", "Link": ""}]

def get_fxstreet():
    url = "https://www.fxstreet.com.tr/analysis/latest"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        analizler = []
        
        # FXStreet TR strukturu
        items = soup.select('h4.fxs_headline_tiny') or soup.find_all('article')
        
        for item in items[:10]:
            link_el = item.find('a')
            if link_el:
                title = link_el.text.strip()
                link = link_el['href']
                analizler.append({
                    "Mənbə": "FXStreet TR",
                    "Analiz": title,
                    "Link": link
                })
        return analizler
    except Exception as e:
        return [{"Mənbə": "FXStreet TR", "Analiz": f"Xəta: {e}", "Link": ""}]

st.title("📊 Forex Son 10 Analiz")

if st.button('Məlumatları Yenilə'):
    with st.spinner('Analizlər toplanır...'):
        all_data = get_dailyforex() + get_fxstreet()
        if all_data:
            df = pd.DataFrame(all_data)
            st.dataframe(df, use_container_width=True)
            
            st.subheader("📌 Qısa Xülasələr")
            for item in all_data:
                if item["Link"]:
                    st.markdown(f"**[{item['Mənbə']}]** {item['Analiz']} — [Məqaləni oxu]({item['Link']})")
        else:
            st.warning("Heç bir məlumat tapılmadı. Sayt strukturu dəyişmiş ola bilər.")

st.sidebar.info("Əgər 'empty' görürsünüzsə, saytlar anlıq girişi bloklayır. Bir neçə saniyə sonra yenidən cəhd edin.")
