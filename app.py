import streamlit as st
import pandas as pd
import feedparser
import google.generativeai as genai
from urllib.parse import quote
import time

# --- KONFİQURASİYA ---
# Gemini API açarınızı bura daxil edin
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao" 

# AI Modelini başlat (Xəta yoxlaması ilə)
try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Konfiqurasiya xətası: {e}")

st.set_page_config(page_title="Forex AI Pro", page_icon="🤖", layout="wide")

def get_ai_decision(title):
    """Gemini mətni analiz edib istiqamət və izah verir"""
    prompt = f"""
    Sən peşəkar Forex treyderisən. Bu analizi oxu: "{title}"
    1. Qərar ver: LONG, SHORT və ya NEYTRAL?
    2. Səbəbini Azərbaycan dilində çox qısa (1 cümlə) izah et.
    Cavabı yalnız bu formatda qaytar: [LONG/SHORT/NEYTRAL] | [Sənin izahın]
    """
    try:
        response = ai_model.generate_content(prompt)
        text = response.text
        
        decision = "🟡 NEYTRAL"
        if "LONG" in text.upper(): decision = "🟢 LONG"
        elif "SHORT" in text.upper(): decision = "🔴 SHORT"
        
        summary = text.split("|")[-1].strip() if "|" in text else "İstiqamət qeyri-müəyyəndir."
        return decision, summary
    except Exception:
        return "🟡 NEYTRAL", "AI hazırda cavab verə bilmir."

def fetch_data(source_name, site_url, query="forex analysis"):
    """Google News vasitəsilə təmizlənmiş və analiz edilmiş məlumat çəkir"""
    encoded_query = quote(f"site:{site_url} {query}")
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    
    results = []
    # TradingView-dakı "Page X" kimi lazımsız başlıqları filtr edirik
    junk = ["page", "editors' picks", "ideas for", "key facts"]
    
    for entry in feed.entries[:8]:
        title = entry.title
        # TradingView üçün xüsusi təmizləmə
        if source_name == "TradingView" and any(word in title.lower() for word in junk):
            continue
            
        decision, summary = get_ai_decision(title)
        results.append({
            "Mənbə": source_name,
            "Analiz": title.split(" - ")[0],
            "AI Qərarı": decision,
            "AI İzahı": summary,
            "Link": entry.link
        })
        time.sleep(0.2) # API limitini qorumaq üçün
    return results

# --- İNTERFEYS ---
st.title("🤖 Forex AI Analiz Mərkəzi")
st.markdown("TradingView, FXStreet və DailyForex məlumatları **Gemini AI** tərəfindən şərh edilir.")

if st.button('Yenilə və AI ilə Analiz Et'):
    with st.status("Məlumatlar toplanır və AI tərəfindən oxunur...", expanded=True) as status:
        st.write("DailyForex emal edilir...")
        data_df = fetch_data("DailyForex", "dailyforex.com")
        
        st.write("FXStreet emal edilir...")
        data_fx = fetch_data("FXStreet", "fxstreet.com")
        
        st.write("TradingView emal edilir...")
        data_tv = fetch_data("TradingView", "tradingview.com", query="EURUSD GOLD technical analysis trade")
        
        all_results = data_df + data_fx + data_tv
        status.update(label="Analiz tamamlandı!", state="complete", expanded=False)

    if all_results:
        df = pd.DataFrame(all_results)
        
        # Əsas Cədvəl
        st.subheader("📋 AI Strategiya İcmalı")
        st.dataframe(df[['Mənbə', 'Analiz', 'AI Qərarı']], use_container_width=True)
        
        # Detallar
        st.subheader("🔍 Detallı AI Şərhləri")
        tab1, tab2, tab3 = st.tabs(["DailyForex", "FXStreet", "TradingView"])
        
        def show_tab_content(source):
            items = [x for x in all_results if x['Mənbə'] == source]
            if not items:
                st.write("Bu mənbədən uyğun texniki analiz tapılmadı.")
            for item in items:
                with st.expander(f"{item['AI Qərarı']} | {item['Analiz']}"):
                    st.markdown(f"**AI Təhlili:** {item['AI İzahı']}")
                    st.link_button("Mənbəyə keçid", item['Link'])

        with tab1: show_tab_content("DailyForex")
        with tab2: show_tab_content("FXStreet")
        with tab3: show_tab_content("TradingView")
    else:
        st.error("Heç bir məlumat tapılmadı. İnternet bağlantısını və ya API açarını yoxlayın.")

st.sidebar.markdown("""
**Tətbiq Haqqında:**
* **AI:** Gemini 1.5 Flash
* **Mənbələr:** Canlı RSS axını
* **Filtr:** Texniki analizlərə fokuslanıb
""")
