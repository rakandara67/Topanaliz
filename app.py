import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Səhifə konfiqurasiyası
st.set_page_config(page_title="Forex Analiz Xülasəsi", layout="wide")

def translate_to_az(text):
    """Sadə lüğət əsaslı və ya süni intellekt əvəzi tərcümə (Nümunə üçün)"""
    translations = {
        "Technical Analysis": "Texniki Analiz",
        "Forecast": "Proqnoz",
        "US Dollar": "ABŞ Dolları",
        "Gold": "Qızıl",
        "Silver": "Gümüş",
        "Bullish": "Artım meyilli",
        "Bearish": "Eniş meyilli",
        "Buying": "Alış",
        "Selling": "Satış"
    }
    for eng, aze in translations.items():
        text = text.replace(eng, aze)
    return text

def extract_levels(text):
    """Mətndən rəqəmləri (Entry, TP, SL) tapmağa çalışır"""
    levels = re.findall(r"(\d+\.\d+)", text)
    return ", ".join(levels) if levels else "Qeyd olunmayıb"

def get_dailyforex():
    url = "https://www.dailyforex.com/forex-technical-analysis/page-1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    analizler = []
    items = soup.find_all('div', class_='daily-analysis-item', limit=10)
    
    for item in items:
        title = item.find('h2').text.strip()
        desc = item.find('p').text.strip()
        link = "https://www.dailyforex.com" + item.find('a')['href']
        
        analizler.append({
            "Mənbə": "DailyForex",
            "Analiz": translate_to_az(title),
            "Xülasə": translate_to_az(desc[:150] + "..."),
            "Səviyyələr (E/TP/SL)": extract_levels(desc),
            "Link": link
        })
    return analizler

def get_fxstreet():
    url = "https://www.fxstreet.com.tr/analysis/latest"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    analizler = []
    # FXStreet TR strukturu üçün uyğunlaşdırma
    items = soup.find_all('article', limit=10)
    
    for item in items:
        title_el = item.find('h4') or item.find('h2')
        if not title_el: continue
        
        title = title_el.text.strip()
        link = item.find('a')['href']
        
        analizler.append({
            "Mənbə": "FXStreet TR",
            "Analiz": title,
            "Xülasə": "Ətraflı linkdə",
            "Səviyyələr (E/TP/SL)": "Məqalədə",
            "Link": link
        })
    return analizler

# UI Hissəsi
st.title("📊 Forex Son 10 Analiz (Xülasə)")

if st.button('Məlumatları Yenilə'):
    with st.spinner('Analizlər toplanır...'):
        try:
            df_data = get_dailyforex() + get_fxstreet()
            df = pd.DataFrame(df_data)
            
            # Cədvəli göstər
            st.table(df)
            
            for i, row in df.iterrows():
                with st.expander(f"{row['Mənbə']}: {row['Analiz']}"):
                    st.write(f"**Xülasə:** {row['Xülasə']}")
                    st.write(f"**Ehtimal olunan səviyyələr:** {row['Səviyyələr (E/TP/SL)']}")
                    st.write(f"[Mənbəyə keçid]({row['Link']})")
        except Exception as e:
            st.error(f"Xəta baş verdi: {e}")
else:
    st.info("Analizləri görmək üçün 'Yenilə' düyməsinə basın.")

st.sidebar.markdown("""
### Necə işləyir?
1. **DailyForex** və **FXStreet TR** saytlarına sorğu göndərir.
2. Ən son 10 analizi skan edir.
3. Başlıqları AZ dilinə çevirir və mətndəki rəqəmləri ayırır.
""")
