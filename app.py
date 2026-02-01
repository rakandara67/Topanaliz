import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Səhifə Ayarları
st.set_page_config(page_title="Forex Analiz Mərkəzi", layout="wide")

def get_action_logic(text):
    """Mətni analiz edib Long/Short qərarı verir"""
    text = text.lower()
    long_keywords = ['bullish', 'long', 'yükseliş', 'artış', 'destek', 'alım', 'buy', 'target higher']
    short_keywords = ['bearish', 'short', 'düşüş', 'gerileme', 'direnç', 'satış', 'sell', 'target lower']
    
    # Xülasə üçün sadə tərcümə məntiqi
    summary = "Analiz bazarda qeyri-müəyyənlik və ya neytral zona göstərir."
    action = "🟡 Neytral / Gözlə"
    
    if any(word in text for word in long_keywords):
        action = "🟢 LONG (Alış)"
        summary = "Texniki göstəricilər artım meylini və alış fürsətlərini dəstəkləyir."
    elif any(word in text for word in short_keywords):
        action = "🔴 SHORT (Satış)"
        summary = "Texniki göstəricilər eniş meylini və satış təzyiqini göstərir."
        
    return action, summary

def fetch_dailyforex_rss():
    """RSS vasitəsilə DailyForex-dən məlumat çəkir (Bloklanmır)"""
    url = "https://www.dailyforex.com/forex-technical-analysis/rss"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, features="xml")
        items = soup.find_all('item')
        
        results = []
        for item in items[:10]:
            title = item.title.text
            link = item.link.text
            desc = item.description.text if item.description else ""
            action, summary = get_action_logic(title + " " + desc)
            
            results.append({
                "Mənbə": "DailyForex",
                "Analiz": title,
                "Qərar": action,
                "Məna (AZ)": summary,
                "Link": link
            })
        return results
    except:
        return []

def fetch_fxstreet_tr():
    """FXStreet TR saytından məlumat çəkir"""
    url = "https://www.fxstreet.com.tr/analysis/latest"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        # FXStreet başlıqlarını tapmaq
        items = soup.select('h4.fxs_headline_tiny') or soup.find_all('h4')
        
        for item in items[:10]:
            link_tag = item.find('a')
            if link_tag:
                title = link_tag.text.strip()
                link = link_tag['href']
                action, summary = get_action_logic(title)
                
                results.append({
                    "Mənbə": "FXStreet TR",
                    "Analiz": title,
                    "Qərar": action,
                    "Məna (AZ)": summary,
                    "Link": link
                })
        return results
    except:
        return []

# --- UI GÖSTƏRİCİSİ ---
st.title("📈 Forex Son 10 Analiz və Qərarlar")
st.markdown("Hər iki saytdan ən son texniki analizlər toplanaraq avtomatik qiymətləndirilir.")

if st.button('Yenilə və Analiz Et'):
    with st.spinner('Məlumatlar emal olunur...'):
        all_data = fetch_dailyforex_rss() + fetch_fxstreet_tr()
        
        if all_data:
            df = pd.DataFrame(all_data)
            
            # Əsas cədvəl
            st.subheader("📋 İcmal Cədvəli")
            st.dataframe(df[['Mənbə', 'Analiz', 'Qərar']], use_container_width=True)
            
            # Detallı kartlar
            st.subheader("🔍 Analizlərin Xülasəsi")
            for entry in all_data:
                with st.expander(f"{entry['Qərar']} | {entry['Mənbə']}: {entry['Analiz']}"):
                    st.write(f"**Vəziyyət:** {entry['Məna (AZ)']}")
                    st.write(f"**Konkret Addım:** Bu analiz {entry['Qərar'].split(' ')[1]} istiqamətli hərəkət ehtimalını vurğulayır.")
                    st.write(f"[Tam analizi oxu]({entry['Link']})")
        else:
            st.error("Məlumat tapılmadı. İnternet bağlantısını yoxlayın.")

st.sidebar.markdown("""
### Məlumat:
- **DailyForex:** RSS kanalı ilə çəkilir (Bloklanma riski yoxdur).
- **FXStreet:** Birbaşa veb-saytdan çəkilir.
- **Qərar Məntiqi:** Başlıqdakı açar sözlərə əsasən **Long/Short** təyin edilir.
""")
