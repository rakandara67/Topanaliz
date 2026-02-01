import streamlit as st
import pandas as pd
import feedparser
import google.generativeai as genai
from urllib.parse import quote
import time

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao" 

try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Konfiqurasiya xətası: {e}")

st.set_page_config(page_title="Forex AI Pro", page_icon="🤖", layout="wide")

def get_ai_decision(title):
    """Gemini-yə daha detallı təlimat veririk ki, NEYTRAL çıxmasın"""
    prompt = f"""
    Sən peşəkar Forex treyderisən. Bu başlığı analiz et: "{title}"
    Tapşırıq:
    1. Əgər başlıqda qiymətin artacağına dair (bullish, support, buy, recovery, rally, breakout) işarə varsa: "🟢 LONG"
    2. Əgər başlıqda qiymətin düşəcəyinə dair (bearish, resistance, sell, plunges, retreats, lower) işarə varsa: "🔴 SHORT"
    3. Yalnız heç bir texniki ipucu yoxdursa: "🟡 NEYTRAL"
    
    Cavabı bu formatda qaytar: QƏRAR: [LONG/SHORT/NEYTRAL] | İZAH: [Azərbaycan dilində 1 qısa cümlə]
    """
    try:
        response = ai_model.generate_content(prompt)
        text = response.text
        
        decision = "🟡 NEYTRAL"
        if "LONG" in text.upper(): decision = "🟢 LONG"
        elif "SHORT" in text.upper(): decision = "🔴 SHORT"
        
        summary = text.split("|")[-1].replace("İZAH:", "").strip() if "|" in text else "AI istiqamət təyin etdi."
        return decision, summary
    except:
        return "🟡 NEYTRAL", "AI analiz edə bilmədi."

def fetch_data(source_name, site_url, query="forex technical analysis"):
    """Daha dəqiq texniki analizləri tapmaq üçün axtarış sorğusunu gücləndirdik"""
    encoded_query = quote(f"site:{site_url} {query}")
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    
    results = []
    # TradingView-da analiz olmayan başlıqları tamamilə bloklayırıq
    junk = ["chart", "index", "features", "track all", "rates", "quotes", "market"]
    
    for entry in feed.entries[:10]:
        title = entry.title
        # Filter: İçində "chart" və ya "market" olan ümumi linkləri atırıq
        if any(word in title.lower() for word in junk) and source_name == "TradingView":
            continue
            
        decision, summary = get_ai_decision(title)
        
        # Əgər hələ də hamısı neytraldırsa, istifadəçiyə maraqlı deyil, siyahını təmiz saxlayırıq
        results.append({
            "Mənbə": source_name,
            "Analiz": title.split(" - ")[0],
            "AI Qərarı": decision,
            "AI İzahı": summary,
            "Link": entry.link
        })
        time.sleep(0.1) 
    return results

# --- İNTERFEYS ---
st.title("📊 Forex AI Strateji Mərkəzi")

if st.button('Analizləri Yenilə (Gemini AI)'):
    with st.status("AI bazarı oxuyur...", expanded=True) as status:
        # Axtarış sorğularını dəyişdik ki, "Chart" yox, "Signal/Forecast" gəlsin
        data_df = fetch_data("DailyForex", "dailyforex.com", query="forex signal forecast")
        data_fx = fetch_data("FXStreet", "fxstreet.com", query="price forecast analysis")
        data_tv = fetch_data("TradingView", "tradingview.com", query="technical analysis eurusd xauusd")
        
        all_results = data_df + data_fx + data_tv
        status.update(label="Analizlər hazır!", state="complete", expanded=False)

    if all_results:
        df = pd.DataFrame(all_results)
        
        # Cədvəl
        st.subheader("📋 AI Siqnal İcmalı")
        # Rənglərə görə sıralayırıq ki, Long/Short yuxarıda görünsün
        df['sort_order'] = df['AI Qərarı'].apply(lambda x: 0 if "🟢" in x or "🔴" in x else 1)
        df = df.sort_values('sort_order').drop('sort_order', axis=1)
        
        st.dataframe(df[['Mənbə', 'Analiz', 'AI Qərarı']], use_container_width=True)
        
        # Detallar (Tablar)
        tabs = st.tabs(["DailyForex", "FXStreet", "TradingView"])
        for i, src in enumerate(["DailyForex", "FXStreet", "TradingView"]):
            with tabs[i]:
                items = [x for x in all_results if x['Mənbə'] == src]
                for item in items:
                    with st.expander(f"{item['AI Qərarı']} | {item['Analiz']}"):
                        st.info(f"**AI Təhlili:** {item['AI İzahı']}")
                        st.link_button("Mənbəyə keç", item['Link'])
    else:
        st.warning("Yeni analiz tapılmadı.")
    
