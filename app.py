import streamlit as st
import pandas as pd
import feedparser
import re

st.set_page_config(page_title="Forex Analiz Pro", page_icon="📈", layout="wide")

def extract_levels(text):
    """Mətndən qiymət səviyyələrini tapır"""
    levels = re.findall(r"\d+\.\d{2,4}", text)
    return ", ".join(list(set(levels))[:3]) if levels else "Analizdə qeyd edilməyib"

def get_sentiment(text):
    """Mətni analiz edib istiqamət və xülasə təyin edir"""
    text = text.lower()
    long_keywords = ['bullish', 'long', 'yükseliş', 'artış', 'destek', 'alım', 'buy', 'higher', 'breakout']
    short_keywords = ['bearish', 'short', 'düşüş', 'gerileme', 'direnç', 'satış', 'sell', 'lower', 'breakdown']
    
    is_long = any(word in text for word in long_keywords)
    is_short = any(word in text for word in short_keywords)
    
    if is_long and not is_short:
        return "🟢 LONG", "Alıcılar üstünlük təşkil edir. Artım ehtimalı yüksəkdir."
    elif is_short and not is_long:
        return "🔴 SHORT", "Satıcılar təzyiqi artırır. Eniş gözlənilir."
    else:
        return "🟡 NEYTRAL", "Bazar hazırda qərarsızdır və ya gözləmə mövqeyindədir."

def fetch_news(site_name, site_url, query="forex analysis"):
    """RSS vasitəsilə bloklanmadan məlumat çəkir"""
    rss_url = f"https://news.google.com/rss/search?q=site:{site_url}+{query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    results = []
    for entry in feed.entries[:8]: # Hər mənbədən ən son 8 analiz
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
st.title("📊 Forex & TradingView Analiz Mərkəzi")
st.markdown("DailyForex, FXStreet və **TradingView Editors' Picks** analizləri bir yerdə.")

if st.button('Yenilə və Analiz Et'):
    with st.spinner('Bütün mənbələrdən analizlər toplanır...'):
        # Mənbələri birləşdiririk
        data = (
            fetch_news("DailyForex", "dailyforex.com") + 
            fetch_news("FXStreet", "fxstreet.com") +
            fetch_news("TradingView", "tradingview.com", query="editors picks trade ideas")
        )
        
        if data:
            df = pd.DataFrame(data)
            
            # Cədvəl İcmalı
            st.subheader("📋 Bütün Analizlərin İcmalı")
            st.dataframe(df[['Mənbə', 'Analiz', 'Qərar']], use_container_width=True)
            
            # Detallı Kartlar
            st.subheader("📝 Qərar Detalları")
            
            # Mənbələrə görə filtrləmək üçün tablar
            tab1, tab2, tab3 = st.tabs(["DailyForex", "FXStreet", "TradingView"])
            
            with tab1:
                for item in [x for x in data if x['Mənbə'] == "DailyForex"]:
                    with st.expander(f"{item['Qərar']} | {item['Analiz']}"):
                        st.write(f"**Xülasə:** {item['Xülasə']}")
                        st.caption(f"📍 Səviyyələr: {item['Səviyyələr']}")
                        st.link_button("Məqaləni Oxu", item['Link'])

            with tab2:
                for item in [x for x in data if x['Mənbə'] == "FXStreet"]:
                    with st.expander(f"{item['Qərar']} | {item['Analiz']}"):
                        st.write(f"**Xülasə:** {item['Xülasə']}")
                        st.caption(f"📍 Səviyyələr: {item['Səviyyələr']}")
                        st.link_button("Məqaləni Oxu", item['Link'])

            with tab3:
                for item in [x for x in data if x['Mənbə'] == "TradingView"]:
                    with st.expander(f"{item['Qərar']} | {item['Analiz']}"):
                        st.write(f"**Xülasə:** {item['Xülasə']}")
                        st.caption(f"📍 Səviyyələr: {item['Səviyyələr']}")
                        st.link_button("İdeyaya bax", item['Link'])
        else:
            st.warning("Məlumat tapılmadı. İnternet bağlantısını yoxlayın.")

st.sidebar.success("DailyForex ✅\nFXStreet ✅\nTradingView ✅")
                
