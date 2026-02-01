import streamlit as st
import pandas as pd
import feedparser
import re

st.set_page_config(page_title="Forex Analiz Pro", page_icon="📈")

def extract_levels(text):
    """Mətndən qiymət səviyyələrini (məs: 1.1234) tapır"""
    levels = re.findall(r"\d+\.\d{2,4}", text)
    return ", ".join(list(set(levels))[:3]) if levels else "Analizdə qeyd edilməyib"

def get_sentiment(text):
    """Mətni analiz edib istiqamət və xülasə təyin edir"""
    text = text.lower()
    long_keywords = ['bullish', 'long', 'yükseliş', 'artış', 'destek', 'alım', 'buy', 'higher']
    short_keywords = ['bearish', 'short', 'düşüş', 'gerileme', 'direnç', 'satış', 'sell', 'lower']
    
    is_long = any(word in text for word in long_keywords)
    is_short = any(word in text for word in short_keywords)
    
    if is_long and not is_short:
        return "🟢 LONG", "Alıcılar üstünlük təşkil edir. Artım ehtimalı yüksəkdir."
    elif is_short and not is_long:
        return "🔴 SHORT", "Satıcılar təzyiqi artırır. Eniş gözlənilir."
    else:
        return "🟡 NEYTRAL", "Bazar hazırda qərarsızdır və ya hər iki istiqamət mümkündür."

def fetch_news(site_name, site_url):
    """Google News RSS vasitəsilə bloklanmadan məlumat çəkir"""
    rss_url = f"https://news.google.com/rss/search?q=site:{site_url}+forex+analysis&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    results = []
    for entry in feed.entries[:10]:
        decision, summary = get_sentiment(entry.title)
        levels = extract_levels(entry.title)
        results.append({
            "Mənbə": site_name,
            "Analiz": entry.title,
            "Qərar": decision,
            "Xülasə": summary,
            "Səviyyələr": levels,
            "Link": entry.link
        })
    return results

# --- INTERFACE ---
st.title("📊 Forex Son 10 Analiz və Qərarlar")

if st.button('Yenilə və Analiz Et'):
    with st.spinner('Məlumatlar toplanır...'):
        data = fetch_news("DailyForex", "dailyforex.com") + fetch_news("FXStreet", "fxstreet.com")
        
        if data:
            df = pd.DataFrame(data)
            
            # Cədvəl İcmalı
            st.subheader("📋 Analiz İcmalı")
            st.dataframe(df[['Mənbə', 'Analiz', 'Qərar']], use_container_width=True)
            
            # Detallı Kartlar (Xətasız Versiya)
            st.subheader("📝 Qərar Detalları")
            for item in data:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{item['Mənbə']}**: {item['Analiz']}")
                        st.info(f"🔍 **Xülasə:** {item['Xülasə']}")
                        st.caption(f"📍 **Tapılan Səviyyələr:** {item['Səviyyələr']}")
                    with col2:
                        st.markdown(f"### {item['Qərar']}")
                        st.link_button("Məqaləni Oxu", item['Link'])
        else:
            st.warning("Məlumat tapılmadı. İnternet bağlantısını yoxlayın.")

st.sidebar.markdown("### Məlumat\nBu tətbiq analizləri Google News vasitəsilə çəkir və bloklanmır.")
