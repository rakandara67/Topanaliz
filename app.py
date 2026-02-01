import streamlit as st
import pandas as pd
import feedparser
import google.generativeai as genai
from bs4 import BeautifulSoup
import time

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao" 

try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Başlatma xətası: {e}")

st.set_page_config(page_title="Forex Deep Mind Pro", page_icon="🏦", layout="wide")

def analyze_full_content(text_data):
    """Mətnin daxilini dərindən oxuyub peşəkar qərar verir"""
    prompt = f"""
    Sən peşəkar bir fond menecerisən. Aşağıdakı bazar təhlilini oxu:
    "{text_data}"
    
    Tapşırıq:
    1. Qərar: LONG, SHORT və ya NEYTRAL?
    2. Səbəb: Azərbaycan dilində 1 cümləlik çox konkret texniki izah.
    3. Səviyyələr: Mətndəki Entry, Stop Loss və Take Profit qiymətlərini çıxar.
    
    Format: [QƏRAR] | [İZAH] | [SƏVİYYƏLƏR]
    """
    try:
        response = ai_model.generate_content(prompt)
        res = response.text
        parts = res.split("|")
        
        dec_raw = parts[0].upper()
        decision = "🟡 NEYTRAL"
        if "LONG" in dec_raw: decision = "🟢 LONG"
        elif "SHORT" in dec_raw: decision = "🔴 SHORT"
        
        summary = parts[1].strip() if len(parts) > 1 else "Analiz dərindən emal edildi."
        levels = parts[2].strip() if len(parts) > 2 else "Qiymət qeyd edilməyib."
        
        return decision, summary, levels
    except:
        return None, None, None

# --- UI ---
st.title("🏦 Forex Deep Mind: Professional Hub")
st.markdown("Bu versiya birbaşa xəbər agentliklərinin analiz lentini (RSS) dərindən oxuyur.")

if st.button('Həqiqi Analizləri İndi Oxu'):
    # Ən etibarlı və bloklanmayan birbaşa RSS mənbələri
    rss_feeds = {
        "FXStreet (Technical)": "https://www.fxstreet.com/rss/technical-analysis",
        "DailyForex (Signals)": "https://www.dailyforex.com/forex-technical-analysis/rss",
        "ActionForex": "https://www.actionforex.com/category/contributors/analysis/feed/"
    }
    
    all_reports = []
    
    for name, url in rss_feeds.items():
        with st.status(f"{name} mənbəsindən mətnlər çəkilir...", expanded=False):
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:5]: # Hər mənbədən ən son 5 analiz
                # RSS daxilində çox vaxt 'content' və ya 'summary' olur
                raw_html = ""
                if 'content' in entry:
                    raw_html = entry.content[0].value
                elif 'summary' in entry:
                    raw_html = entry.summary
                
                # HTML-i təmizləyib təmiz mətn alırıq (AI üçün)
                clean_text = BeautifulSoup(raw_html, "html.parser").get_text()
                
                # Əgər mətn qısadırsa, başlığı da əlavə edirik
                full_context = f"BAŞLIQ: {entry.title}\nMƏTN: {clean_text}"
                
                if len(clean_text) > 100:
                    decision, reason, levels = analyze_full_content(full_context)
                    
                    if decision:
                        all_reports.append({
                            "Mənbə": name,
                            "Başlıq": entry.title,
                            "Qərar": decision,
                            "İzah": reason,
                            "Səviyyələr": levels,
                            "Link": entry.link
                        })

    if all_reports:
        # Cədvəl görünüşü
        df = pd.DataFrame(all_reports)
        st.subheader("📋 Bazar Sinyalları (Dərin Təhlil)")
        st.dataframe(df[['Mənbə', 'Qərar', 'Başlıq']], use_container_width=True)
        
        # Detallı kartlar
        for item in all_reports:
            with st.expander(f"{item['Qərar']} | {item['Başlıq']}"):
                st.write(f"**Analiz mənbəsi:** {item['Mənbə']}")
                st.info(f"**AI Qərarının Səbəbi:** {item['İzah']}")
                st.warning(f"**Texniki Səviyyələr:** {item['Səviyyələr']}")
                st.link_button("Tam məqaləyə keçid", item['Link'])
    else:
        st.error("Xəbər lentləri müvəqqəti bağlıdır və ya AI emal edə bilmədi.")

st.sidebar.markdown("### Niyə bu sistem?")
st.sidebar.write("Bu sistem Google axtarışından asılı deyil. Birbaşa rəsmi analiz kanallarından gələn tam mətni Gemini 1.5-ə oxudur və peşəkar nəticə çıxarır.")
    
