import streamlit as st
import pandas as pd
import feedparser
import re
from urllib.parse import quote

st.set_page_config(page_title="Forex Analiz Pro", page_icon="📈", layout="wide")

def get_sentiment(text):
    """Mətni daha geniş texniki terminlərlə analiz edir"""
    text = text.lower()
    
    # Alış meyilli terminlər
    long_list = ['bullish', 'long', 'yükseliş', 'artış', 'destek', 'alım', 'buy', 'higher', 'breakout', 'support', 'demand', 'recovery']
    # Satış meyilli terminlər
    short_list = ['bearish', 'short', 'düşüş', 'gerileme', 'direnç', 'satış', 'sell', 'lower', 'breakdown', 'resistance', 'supply', 'drop']
    
    is_long = any(word in text for word in long_list)
    is_short = any(word in text for word in short_list)
    
    if is_long and not is_short:
        return "🟢 LONG", "Analiz artım ehtimalını və alış bölgələrini vurğulayır."
    elif is_short and not is_long:
        return "🔴 SHORT", "Analiz eniş təzyiqini və satış zonalarını göstərir."
    else:
        return "🟡 NEYTRAL", "Mətn konkret istiqamət bildirmir və ya hər iki tərəf üçün risklidir."

def fetch_news(site_name, site_url, query="forex analysis"):
    """Google News RSS vasitəsilə məlumat çəkir"""
    encoded_query = quote(f"site:{site_url} {query}")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    feed = feedparser.parse(rss_url)
    results = []
    
    # TradingView-da "Page X" və ya "Editors Picks" kimi mənasız başlıqları filtrə salırıq
    forbidden_words = ["page", "editors' picks", "ideas for", "key facts"]
    
    for entry in feed.entries[:12]:
        title = entry.title
        # Əgər başlıqda analiz yoxdursa, keçirik
        if any(word in title.lower() for word in forbidden_words) and site_name == "TradingView":
            continue
            
        decision, summary = get_sentiment(title)
        levels = re.findall(r"\d+\.\d{2,4}", title)
        levels_str = ", ".join(list(set(levels))[:3]) if levels else "Qeyd edilməyib"
        
        results.append({
            "Mənbə": site_name,
            "Analiz": title.replace(" - TradingView", "").replace(" - DailyForex", ""),
            "Qərar": decision,
            "Xülasə": summary,
            "Səviyyələr": levels_str,
            "Link": entry.link
        })
    return results

# --- INTERFACE ---
st.title("📊 Forex & TradingView Analiz Mərkəzi")

if st.button('Yenilə və Analiz Et'):
    with st.spinner('Məlumatlar süzgəcdən keçirilir...'):
        # Məlumatları çəkirik
        df_daily = fetch_news("DailyForex", "dailyforex.com")
        df_fx = fetch_news("FXStreet", "fxstreet.com")
        # TradingView üçün daha spesifik axtarış: EURUSD, GOLD, BTC kimi
        df_tv = fetch_news("TradingView", "tradingview.com", query="EURUSD GOLD technical analysis")
        
        all_data = df_daily + df_fx + df_tv
        
        if all_data:
            df = pd.DataFrame(all_data)
            
            st.subheader("📋 Analiz İcmalı")
            st.dataframe(df[['Mənbə', 'Analiz', 'Qərar']], use_container_width=True)
            
            st.subheader("📝 Qərar Detalları")
            tab1, tab2, tab3 = st.tabs(["DailyForex", "FXStreet", "TradingView"])
            
            def render_tab(source_name):
                items = [x for x in all_data if x['Mənbə'] == source_name]
                if not items:
                    st.write("Hal-hazırda bu mənbədən uyğun analiz tapılmadı.")
                for item in items:
                    with st.expander(f"{item['Qərar']} | {item['Analiz']}"):
                        st.markdown(f"**Vəziyyət:** {item['Xülasə']}")
                        st.markdown(f"**Tapılan Qiymətlər:** `{item['Səviyyələr']}`")
                        st.link_button("Analizə Get", item['Link'])

            with tab1: render_tab("DailyForex")
            with tab2: render_tab("FXStreet")
            with tab3: render_tab("TradingView")
        else:
            st.error("Məlumat tapılmadı.")

st.sidebar.info("Tövsiyə: 'Neytral' olanlar adətən ümumi bazar xəbərləridir. Rəngli siqnallara diqqət yetirin.")
        
