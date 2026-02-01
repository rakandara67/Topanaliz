import streamlit as st
import feedparser

st.set_page_config(page_title="Forex Pro Hub", layout="wide")

st.title("🏛️ Forex Professional Analysis Hub")

# Aktiv seçimi
symbol = st.selectbox("Aktiv seçin:", ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "USDJPY", "AUDUSD"])
short_name = symbol[:3]

# Mitrade-ə birbaşa keçid düyməsi (çünki RSS-i yoxdur, amma analizi əladır)
st.markdown(f"🚀 **Mitrade Özəl Analiz:** [Mitrade {symbol} Analizinə Get](https://www.mitrade.com/en/financial-tools/trading-analysis)")

col1, col2, col3 = st.columns(3)

def fetch_and_filter(url, title_label, filter_keyword):
    feed = feedparser.parse(url)
    count = 0
    if feed.entries:
        for entry in feed.entries:
            title = entry.title.upper()
            # Daha dəqiq filtr
            if filter_keyword.upper() in title:
                st.markdown(f"✅ [{entry.title}]({entry.link})")
                st.caption(f"📅 {entry.published if 'published' in entry else 'Bugün'}")
                st.write("---")
                count += 1
            if count >= 10: break
    
    if count == 0:
        st.info(f"{title_label}-də hazırda '{filter_keyword}' üçün yeni analiz yoxdur.")

# 1. TradingView (Həmişə stabil)
with col1:
    st.header("📊 TradingView")
    tv_url = f"https://www.tradingview.com/feed/?symbol={symbol}"
    tv_feed = feedparser.parse(tv_url)
    for i, entry in enumerate(tv_feed.entries[:10], 1):
        st.markdown(f"{i}. [{entry.title}]({entry.link})")
        st.write("---")

# 2. FXStreet (Analiz Fokuslu)
with col2:
    st.header("📰 FXStreet")
    fx_url = "https://www.fxstreet.com/rss/analysis" 
    fetch_and_filter(fx_url, "FXStreet", short_name)

# 3. Investing.com (DailyFX əvəzinə - Ən zəngin mənbə)
with col3:
    st.header("📉 Investing.com")
    # Investing.com-un əsas Forex analiz lenti
    inv_url = "https://www.investing.com/rss/market_overview_forex.rss"
    fetch_and_filter(inv_url, "Investing.com", short_name)

st.markdown("---")
st.info("💡 **İstifadə qaydası:** Siyahıda link yoxdursa, digər mənbəyə baxın və ya Mitrade düyməsinə klikləyərək canlı analizə keçin.")
