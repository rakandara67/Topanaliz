import streamlit as st
import feedparser

st.set_page_config(page_title="Forex Link Hub Pro", layout="wide")

st.title("🔗 Forex Son Analiz Linkləri")

# Aktiv seçimi
symbol = st.selectbox("Aktiv seçin:", ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "USDCAD", "USDJPY"])

# Axtarış üçün açar sözlər
primary_keyword = symbol[:3] # Məsələn: EUR
secondary_keyword = symbol[3:] # Məsələn: USD

col1, col2, col3 = st.columns(3)

def fetch_and_filter(url, title_label):
    feed = feedparser.parse(url)
    count = 0
    if feed.entries:
        for entry in feed.entries:
            title = entry.title.upper()
            # Dəqiq filtr: Başlıqda həm EUR, həm USD keçməlidir (və ya tam EURUSD)
            if (primary_keyword in title and secondary_keyword in title) or (symbol in title):
                st.markdown(f"✅ [{entry.title}]({entry.link})")
                st.caption(f"📅 {entry.published if 'published' in entry else 'Bugün'}")
                st.write("---")
                count += 1
            if count >= 10: break
    
    if count == 0:
        st.info(f"{title_label} mənbəsində '{symbol}' üçün xüsusi analiz tapılmadı.")

# 1. TradingView (Stabil)
with col1:
    st.header("📊 TradingView")
    tv_url = f"https://www.tradingview.com/feed/?symbol={symbol}"
    # TradingView zatən filtrli gəldiyi üçün birbaşa göstəririk
    tv_feed = feedparser.parse(tv_url)
    for i, entry in enumerate(tv_feed.entries[:10], 1):
        st.markdown(f"{i}. [{entry.title}]({entry.link})")
        st.write("---")

# 2. FXStreet (Dəqiq Filtr)
with col2:
    st.header("📰 FXStreet")
    # FXStreet-in əsas analiz lenti
    fx_url = "https://www.fxstreet.com/rss/analysis" 
    fetch_and_filter(fx_url, "FXStreet")

# 3. DailyFX (Alternativ Yol)
with col3:
    st.header("📉 DailyFX")
    # DailyFX-in fərqli xəbər kanallarını yoxlayırıq
    dfx_url = "https://www.dailyfx.com/feeds/market-news"
    fetch_and_filter(dfx_url, "DailyFX")

st.markdown("---")
st.warning("💡 Qeyd: Əgər FXStreet və DailyFX-də nəticə yoxdursa, bu o deməkdir ki, son 24 saatda həmin saytlarda seçdiyiniz aktivlə bağlı xüsusi məqalə dərc edilməyib.")
