import streamlit as st
import pandas as pd
import feedparser
import re
from urllib.parse import quote

st.set_page_config(page_title="Forex & TradingView Analiz", page_icon="📈", layout="wide")

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
    """Google News RSS vasitəsilə bloklanmadan məlumat çəkir"""
    # URL daxilindəki boşluqları və simvolların təhlükəsizliyini təmin edirik
    encoded_query = quote(f"site:{site_url} {query}")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    feed = feedparser.parse(rss_url)
    results = []
    
    for entry in feed.entries[:8]:
        decision, summary = get_sentiment(entry.title)
        # Qiymət səviyyələrini təmizləyirik
        levels = re.findall(r"\d+\.\d{2,4}", entry.title)
        levels_str = ", ".join(list(set(levels))[:3]) if levels else "Qeyd edilməyib"
        
        results.append({
            "Mənbə": site_name,
            "Analiz": entry.title,
            "Qərar": decision,
            "Xülasə": summary,
            "Səviyyələr": levels_str,
            "Link": entry.link
        })
    return results

# --- INTERFACE ---
st.title("📊 Forex & TradingView Analiz Mərkəzi")
st.markdown("DailyForex, FXStreet və **TradingView Editors' Picks** analizləri.")

if st.button('Yenilə və Analiz Et'):
    with st.spinner('Məlumatlar toplanır...'):
        try:
            # Hər üç mənbədən məlumatların çəkilməsi
            df_daily = fetch_news("DailyForex", "dailyforex.com")
            df_fx = fetch_news("FXStreet", "fxstreet.com")
            df_tv = fetch_news("TradingView", "tradingview.com", query="editors picks trade ideas")
            
            all_data = df_daily + df_fx + df_tv
            
            if all_data:
                df = pd.DataFrame(all_data)
                
                # İcmal Cədvəli
                st.subheader("📋 Bütün Analizlərin İcmalı")
                st.dataframe(df[['Mənbə', 'Analiz', 'Qərar']], use_container_width=True)
                
                # Detallı Kartlar (Tab sistemi)
                st.subheader("📝 Qərar Detalları")
                tab1, tab2, tab3 = st.tabs(["DailyForex", "FXStreet", "TradingView"])
                
                def render_items(source_name):
                    items = [x for x in all_data if x['Mənbə'] == source_name]
                    if not items:
                        st.write("Bu mənbədən yeni analiz tapılmadı.")
                    for item in items:
                        with st.expander(f"{item['Qərar']} | {item['Analiz']}"):
                            st.write(f"**Vəziyyət:** {item['Xülasə']}")
                            st.write(f"**Səviyyələr:** `{item['Səviyyələr']}`")
                            st.link_button("Tam Analizi Oxu", item['Link'])

                with tab1: render_items("DailyForex")
                with tab2: render_items("FXStreet")
                with tab3: render_items("TradingView")
            else:
                st.warning("Heç bir analiz tapılmadı.")
        except Exception as e:
            st.error(f"Sistem xətası: {e}")

st.sidebar.markdown("""
**Sistem Vəziyyəti:**
- DailyForex: ✅ RSS
- FXStreet: ✅ Google News
- TradingView: ✅ Editors Picks
""")
