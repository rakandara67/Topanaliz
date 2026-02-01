import streamlit as st
import pandas as pd
import feedparser
import google.generativeai as genai
from urllib.parse import quote
import time

# --- KONFİQURASİYA ---
# API açarını buraya daxil edin
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao" 

# AI Modelini Başlatmaq (Xəta profilaktikası ilə)
try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Başlatma Xətası: {e}")

st.set_page_config(page_title="Forex AI Analitik", page_icon="🤖", layout="wide")

def get_ai_decision(title):
    """Gemini AI analizi dərindən oxuyub qərar verir"""
    prompt = f"""
    Sən peşəkar Forex treyderisən. Bu analizi oxu: "{title}"
    1. Qərar ver: LONG, SHORT və ya NEYTRAL?
    2. Səbəbini Azərbaycan dilində çox qısa (1 cümlə) izah et.
    Cavabı bu formatda yaz: QƏRAR: [LONG/SHORT/NEYTRAL] | İZAH: [Sənin izahın]
    """
    try:
        response = ai_model.generate_content(prompt)
        text = response.text
        
        decision = "🟡 NEYTRAL"
        if "LONG" in text.upper(): decision = "🟢 LONG"
        elif "SHORT" in text.upper(): decision = "🔴 SHORT"
        
        summary = text.split("|")[-1].replace("İZAH:", "").strip() if "|" in text else "İstiqamət təyin oluna bilmədi."
        return decision, summary
    except:
        return "🟡 NEYTRAL", "AI hazırda cavab verə bilmir."

def fetch_data(source_name, site_url, query="forex analysis"):
    """Google News vasitəsilə təmizlənmiş məlumat çəkir"""
    encoded_query = quote(f"site:{site_url} {query}")
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    
    results = []
    # TradingView-dakı mənasız başlıqları (Page 1, Editors' Picks və s.) filtr edirik
    junk_words = ["page", "editors' picks", "ideas for", "key facts"]
    
    for entry in feed.entries[:8]:
        title = entry.title
        if source_name == "TradingView" and any(word in title.lower() for word in junk_words):
            continue
            
        decision, summary = get_ai_decision(title)
        results.append({
            "Mənbə": source_name,
            "Analiz": title.split(" - ")[0],
            "AI Qərarı": decision,
            "AI İzahı": summary,
            "Link": entry.link
        })
        time.sleep(0.1) # API limitini qorumaq üçün kiçik fasilə
    return results

# --- INTERFACE ---
st.title("🤖 Forex AI Analiz Mərkəzi")
st.markdown("TradingView, FXStreet və DailyForex məlumatları **Gemini 1.5 Pro** tərəfindən analiz edilir.")

if st.button('Yenilə və AI ilə Təhlil Et'):
    with st.status("AI məlumatları emal edir...", expanded=True) as status:
        st.write("DailyForex oxunur...")
        data_df = fetch_data("DailyForex", "dailyforex.com")
        
        st.write("FXStreet oxunur...")
        data_fx = fetch_data("FXStreet", "fxstreet.com")
        
        st.write("TradingView oxunur...")
        # TradingView üçün daha dəqiq valyuta axtarışı
        data_tv = fetch_data("TradingView", "tradingview.com", query="EURUSD GOLD technical analysis")
        
        all_results = data_df + data_fx + data_tv
        status.update(label="Analiz tamamlandı!", state="complete", expanded=False)

    if all_results:
        df = pd.DataFrame(all_results)
        
        # Əsas Cədvəl
        st.subheader("📋 AI Qərar Cədvəli")
        st.dataframe(df[['Mənbə', 'Analiz', 'AI Qərarı']], use_container_width=True)
        
        # Detallar
        st.subheader("📝 AI-ın Detallı Şərhləri")
        tabs = st.tabs(["DailyForex", "FXStreet", "TradingView"])
        
        for i, src in enumerate(["DailyForex", "FXStreet", "TradingView"]):
            with tabs[i]:
                items = [x for x in all_results if x['Mənbə'] == src]
                if not items:
                    st.write("Bu mənbədən uyğun texniki analiz tapılmadı.")
                for item in items:
                    with st.expander(f"{item['AI Qərarı']} | {item['Analiz']}"):
                        st.write(f"**AI Təhlili:** {item['AI İzahı']}")
                        st.link_button("Mənbəyə keç", item['Link'])
    else:
        st.error("Məlumat tapılmadı. API açarını və ya interneti yoxlayın.")

st.sidebar.markdown("""
### Sistem Haqqında:
- **AI Model:** Gemini 1.5 Flash
- **Məntiq:** Kontekstual Analiz
- **Dil:** Azərbaycan dili xülasə
""")
    
