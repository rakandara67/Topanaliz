import streamlit as st
import pandas as pd
import feedparser
import google.generativeai as genai
from urllib.parse import quote

# --- KONFİQURASİYA ---
GEMINI_API_KEY = "SİZİN_API_AÇARINIZ" # Buraya öz açarınızı yazın
genai.configure(api_key=AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Forex Analiz", page_icon="🤖", layout="wide")

def get_ai_decision(title):
    """Gemini AI mətni oxuyub qərar verir"""
    prompt = f"""
    Sən peşəkar bir Forex analitikisən. Aşağıdakı analiz başlığını oxu:
    "{title}"
    
    Bu analizə əsasən qərar ver: LONG, SHORT və ya NEYTRAL? 
    Həmçinin çox qısa (maksimum 1 cümlə) Azərbaycan dilində xülasə yaz.
    Cavabı yalnız bu formatda qaytar:
    Qərar: [LONG/SHORT/NEYTRAL]
    Xülasə: [Sənin xülasən]
    """
    try:
        response = model.generate_content(prompt)
        res_text = response.text
        # Cavabı parçalayırıq
        decision = "NEYTRAL"
        summary = "Analiz emal edilə bilmədi."
        
        if "LONG" in res_text.upper(): decision = "🟢 LONG"
        elif "SHORT" in res_text.upper(): decision = "🔴 SHORT"
        
        if "Xülasə:" in res_text:
            summary = res_text.split("Xülasə:")[1].strip()
            
        return decision, summary
    except Exception:
        return "🟡 NEYTRAL", "AI xidməti hazırda əlçatmazdır."

def fetch_news(site_name, site_url, query="forex analysis"):
    encoded_query = quote(f"site:{site_url} {query}")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    results = []
    
    for entry in feed.entries[:8]:
        # AI Analizi burada işə düşür
        decision, summary = get_ai_decision(entry.title)
        
        results.append({
            "Mənbə": site_name,
            "Analiz": entry.title.split(" - ")[0],
            "AI Qərarı": decision,
            "Xülasə (AZ)": summary,
            "Link": entry.link
        })
    return results

# --- INTERFACE ---
st.title("🤖 AI Destekli Forex Analiz Merkezi")
st.write("Google Gemini AI hər bir analizi dərindən oxuyaraq qərar verir.")

if st.button('Məlumatları Yenilə və AI ilə Analiz Et'):
    with st.status("AI analizləri oxuyur...", expanded=True) as status:
        st.write("DailyForex toplanır...")
        df_daily = fetch_news("DailyForex", "dailyforex.com")
        st.write("FXStreet toplanır...")
        df_fx = fetch_news("FXStreet", "fxstreet.com")
        st.write("TradingView toplanır...")
        df_tv = fetch_news("TradingView", "tradingview.com", query="technical analysis gold eurusd")
        
        all_data = df_daily + df_fx + df_tv
        status.update(label="Analiz tamamlandı!", state="complete", expanded=False)

    if all_data:
        df = pd.DataFrame(all_data)
        
        st.subheader("📋 AI İcmal Cədvəli")
        st.dataframe(df[['Mənbə', 'Analiz', 'AI Qərarı']], use_container_width=True)
        
        st.subheader("📝 AI Detallı Hesabat")
        tabs = st.tabs(["DailyForex", "FXStreet", "TradingView"])
        
        for i, source in enumerate(["DailyForex", "FXStreet", "TradingView"]):
            with tabs[i]:
                items = [x for x in all_data if x['Mənbə'] == source]
                for item in items:
                    with st.expander(f"{item['AI Qərarı']} | {item['Analiz']}"):
                        st.write(f"**AI Təhlili:** {item['Xülasə (AZ)']}")
                        st.link_button("Orijinal Analiz", item['Link'])
    else:
        st.error("Məlumat tapılmadı.")

st.sidebar.warning("Qeyd: Gemini AI analizləri başlıqlara əsasən şərh edir. Riskli ticarətdən çəkinin.")
    
