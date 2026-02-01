import streamlit as st
import feedparser

st.set_page_config(page_title="Forex Link Hub", layout="wide")

st.title("🔗 Forex Son Analiz Linkləri")
st.write("Aşağıdakı siyahıdan aktiv seçin. Sistem 3 fərqli mənbədən son analizləri gətirəcək.")

# Aktiv seçimi
symbol = st.selectbox("Analiz linkləri üçün aktiv seçin:", ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "USDCAD", "USDJPY"])

# Mənbələr üçün sütunlar
col1, col2, col3 = st.columns(3)

def get_rss_links(url, count=10):
    feed = feedparser.parse(url)
    return feed.entries[:count]

# 1. TradingView Bölməsi
with col1:
    st.header("📊 TradingView")
    tv_url = f"https://www.tradingview.com/feed/?symbol={symbol}"
    tv_entries = get_rss_links(tv_url)
    if tv_entries:
        for i, entry in enumerate(tv_entries, 1):
            st.markdown(f"{i}. [{entry.title}]({entry.link})")
            st.write("---")
    else:
        st.info("TradingView-dan link tapılmadı.")

# 2. FXStreet Bölməsi
with col2:
    st.header("📰 FXStreet")
    # FXStreet üçün ümumi analiz lenti (Aktivə görə filtr bəzən RSS-də məhdud olur)
    fx_url = "https://www.fxstreet.com/rss/news"
    fx_entries = get_rss_links(fx_url)
    found_fx = False
    if fx_entries:
        count = 1
        for entry in fx_entries:
            if symbol[:3].lower() in entry.title.lower(): # Simvolu başlıqda axtarır
                st.markdown(f"{count}. [{entry.title}]({entry.link})")
                st.write("---")
                count += 1
                found_fx = True
            if count > 10: break
    if not found_fx:
        st.info(f"FXStreet-də {symbol} üçün son 10 xəbər tapılmadı.")

# 3. DailyFX Bölməsi
with col3:
    st.header("📉 DailyFX")
    dfx_url = "https://www.dailyfx.com/feeds/forex-market-news"
    dfx_entries = get_rss_links(dfx_url)
    found_dfx = False
    if dfx_entries:
        count = 1
        for entry in dfx_entries:
            if symbol[:3].lower() in entry.title.lower():
                st.markdown(f"{count}. [{entry.title}]({entry.link})")
                st.write("---")
                count += 1
                found_dfx = True
            if count > 10: break
    if not found_dfx:
        st.info(f"DailyFX-də {symbol} üçün son 10 xəbər tapılmadı.")

st.markdown("---")
st.caption("Qeyd: Linklərin yenilənməsi üçün səhifəni yeniləyə və ya aktivi dəyişə bilərsiniz.")
