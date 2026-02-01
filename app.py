import streamlit as st
import feedparser
import requests

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

def get_ai_analysis(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    prompt = f"Sən peşəkar tradersən. Bu analizi Azərbaycan dilində xülasə et. Trend (Long/Short), Entry, SL və TP nöqtələrini aydın göstər: {text}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=15)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "AI hazırda cavab verə bilmir. Mətni düzgün kopyaladığınızdan əmin olun."

st.set_page_config(page_title="Forex Master Analyzer", layout="wide")

st.title("🏆 Forex AI: Editor's Pick & Analysis")

# Aktiv seçimi
symbol = st.selectbox("Analiz ediləcək aktivi seçin:", ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "ETHUSD"])

# RSS lentini çəkirik
rss_url = f"https://www.tradingview.com/feed/?symbol={symbol}"
feed = feedparser.parse(rss_url)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🌟 Redaktorun Seçdiyi Analizlər")
    if feed.entries:
        for i, entry in enumerate(feed.entries[:5], 1):
            # Editor's pick məntiqi: Ən son və ən dolğun analizləri göstəririk
            with st.expander(f"{i}. {entry.title[:50]}..."):
                st.write(f"📅 Tarix: {entry.published if 'published' in entry else 'Bugün'}")
                st.markdown(f"[🔗 Tam analizi aç və mətni kopyala]({entry.link})")
                st.caption("Məsləhət: Linki açdıqdan sonra əsas məqalə hissəsini kopyalayın.")
    else:
        st.info("Analizlər yüklənir və ya tapılmadı...")

with col2:
    st.subheader("🤖 AI Analizator")
    st.write("Aşağıdakı qutuya mətni yapışdırın:")
    
    # Mətn qutusunun aktiv olması üçün 'key' əlavə edirik
    user_input = st.text_area(
        "Analiz mətni (Kopyaladığınız mətni bura daxil edin):", 
        height=300, 
        placeholder="Mətni bura yapışdırın...",
        key="main_input"
    )
    
    if st.button("Analiz et", use_container_width=True):
        if user_input and len(user_input) > 20:
            with st.spinner('AI dərindən analiz edir...'):
                result = get_ai_analysis(user_input)
                st.markdown("---")
                st.success("✅ Yekun Bazar Rəyi:")
                st.markdown(result)
        else:
            st.warning("Zəhmət olmasa kifayət qədər analiz mətni daxil edin.")

# Canlı Qrafik (TradingView Widget)
st.markdown("---")
st.subheader(f"📊 {symbol} Canlı Qrafik")
st.components.v1.html(f"""
    <div style="height:400px;">
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({{
      "width": "100%",
      "height": 400,
      "symbol": "{symbol}",
      "interval": "H1",
      "timezone": "Etc/UTC",
      "theme": "dark",
      "style": "1",
      "locale": "en",
      "toolbar_bg": "#f1f3f6",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "container_id": "tradingview_chart"
    }});
    </script>
    <div id="tradingview_chart"></div>
    </div>
""", height=420)
