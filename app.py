import streamlit as st
import feedparser

st.set_page_config(page_title="Forex Link Hub Pro", layout="wide")

st.title("🔗 Forex Son Analiz Linkləri")

# Aktiv seçimi
symbol = st.selectbox("Aktiv seçin:", ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "USDCAD", "USDJPY"])
# Axtarış üçün qısa ad (məsələn: EURUSD -> EUR)
short_name = symbol[:3]

col1, col2, col3 = st.columns(3)

def display_links(url, filter_word, title_prefix):
    feed = feedparser.parse(url)
    count = 0
    if feed.entries:
        for entry in feed.entries:
            # Filtrləmə: həm tam adı, həm də qısa adı axtarırıq (məs: EUR/USD və ya Euro)
            if filter_word.lower() in entry.title.lower() or short_name.lower() in entry.title.lower():
                st.markdown(f"✅ [{entry.title}]({entry.link})")
                st.caption(f"📅 {entry.published if 'published' in entry else ''}")
                st.write("---")
                count += 1
            if count >= 10: break
    
    if count == 0:
        st.info(f"{title_prefix} üçün hazırda aktiv link tapılmadı.")

# 1. TradingView (Həmişə stabil işləyir)
with col1:
    st.header("📊 TradingView")
    tv_url = f"https://www.tradingview.com/feed/?symbol={symbol}"
    display_links(tv_url, symbol, "TradingView")

# 2. FXStreet (Daha geniş xəbər lenti)
with col2:
    st.header("📰 FXStreet")
    # Analiz lenti bəzən boş olur, ona görə həm xəbər, həm analiz lenti istifadə edirik
    fx_url = "https://www.fxstreet.com/rss/news" 
    display_links(fx_url, short_name, "FXStreet")

# 3. DailyFX (Analiz lenti dəyişdirildi)
with col3:
    st.header("📉 DailyFX")
    # DailyFX-in əsas analiz lenti
    dfx_url = "https://www.dailyfx.com/feeds/forex-market-news"
    display_links(dfx_url, short_name, "DailyFX")

st.markdown("---")
st.info("💡 Əgər linklər azdırsa, 5-10 dəqiqə sonra yenidən yoxlayın. Saytlar analizləri gün ərzində periodik yeniləyir.")
