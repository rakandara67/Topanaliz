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

def deep_ai_analysis(text_content):
    """Mətni tam oxuyub peşəkar qərar çıxarır"""
    prompt = f"""
    Sən peşəkar bir fond menecerisən. Aşağıdakı bazar təhlilini dərindən oxu:
    "{text_content}"
    
    Tapşırıq:
    1. Qərar: 🟢 LONG, 🔴 SHORT və ya 🟡 NEYTRAL?
    2. Səbəb: Azərbaycan dilində 1 cümləlik çox konkret texniki izah.
    3. Səviyyələr: Mətndəki Entry, Stop Loss və Take Profit qiymətlərini tap.
    
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
        levels = parts[2].strip() if len(parts) > 2 else "Mətndə rəqəm tapılmadı."
        
        return decision, summary, levels
    except:
        return None, None, None

# --- UI ---
st.title("🏦 Forex Deep Mind: Professional Hub")
st.markdown("Bu sistem hər bir analizin xülasəsini dərindən emal edərək mütləq bir nəticə çıxarır.")

if st.button('Həqiqi Analizləri İndi Oxu'):
    # Mənbələri artırdıq ki, mütləq məlumat gəlsin
    rss_feeds = {
        "DailyForex Analysis": "https://www.dailyforex.com/forex-technical-analysis/rss",
        "FXStreet Technical": "https://www.fxstreet.com/rss/technical-analysis",
        "Investing Analysis": "https://www.investing.com/rss/forex_TechnicalAnalysis.rss",
        "Forexlive": "https://www.forexlive.com/rss"
    }
    
    all_reports = []
    
    for name, url in rss_feeds.items():
        with st.status(f"{name} mənbəsindən mətnlər çəkilir...", expanded=False):
            # Ehtiyat tədbiri: bəzi serverlərin bloklanmaması üçün fərqli user-agent simulyasiyası yoxdur, feedparser birbaşa oxuyur
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:6]: 
                # Mətni toplamaq
                raw_html = entry.get('summary', '') + entry.get('description', '')
                if 'content' in entry:
                    raw_html += entry.content[0].value
                
                clean_text = BeautifulSoup(raw_html, "html.parser").get_text()
                
                # AI-ya həm başlığı, həm də daxili mətni göndəririk
                full_context = f"BAŞLIQ: {entry.title}\nMƏTN: {clean_text}"
                
                if len(clean_text) > 50:
                    decision, reason, levels = deep_ai_analysis(full_context)
                    
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
        # Cədvəl
        df = pd.DataFrame(all_reports)
        st.subheader("📋 Bazar Sinyalları (Dərin Təhlil)")
        st.dataframe(df[['Mənbə', 'Qərar', 'Başlıq']], use_container_width=True)
        
        # Detallı kartlar
        for item in all_reports:
            with st.expander(f"{item['Qərar']} | {item['Başlıq']}"):
                st.write(f"**Mənbə:** {item['Mənbə']}")
                st.success(f"**AI Təhlili:** {item['İzah']}")
                st.warning(f"**Qiymət Səviyyələri:** {item['Səviyyələr']}")
                st.link_button("Tam məqaləyə keçid", item['Link'])
    else:
        st.error("Mənbələr müvəqqəti məlumat vermir. Zəhmət olmasa bir neçə dəqiqə sonra yenidən yoxlayın.")

st.sidebar.markdown("### Sistemin Üstünlüyü")
st.sidebar.write("Bu versiya Google axtarışını tamamilə ləğv etdi və birbaşa maliyyə agentliklərinin 'raw data' (xammal) xəbər lentlərinə bağlandı.")
    
