import streamlit as st
import requests
import google.generativeai as genai
import feedparser
from bs4 import BeautifulSoup

# --- KONFİQURASİYA ---
GEMINI_API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"
NEWS_API_KEY = "pub_8a60966e639742c09af24649e4e41784"

try:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Xətası: {e}")

st.set_page_config(page_title="Forex Deep Mind Pro", page_icon="🏦", layout="wide")

def deep_ai_analysis(full_text):
    """Mətnin daxilinə girib texniki süzgəcdən keçirir"""
    prompt = f"""
    Sən peşəkar Forex analitikisən. Aşağıdakı bazar təhlilini dərindən oxu:
    "{full_text[:4000]}"
    
    Tapşırıq:
    1. Qərar: 🟢 LONG, 🔴 SHORT və ya 🟡 NEYTRAL?
    2. Səbəb: Azərbaycan dilində 1 cümləlik dəqiq texniki izah.
    3. Səviyyələr: Entry, SL, TP rəqəmlərini tap.
    
    Format: [QƏRAR] | [İZAH] | [SƏVİYYƏLƏR]
    """
    try:
        response = ai_model.generate_content(prompt)
        return response.text.split("|")
    except:
        return None

# --- UI ---
st.title("🏦 Forex Deep Mind: Professional Hub")
st.markdown("Bu sistem rəsmi API və ehtiyat xəbər kanallarından **tam mətnləri** toplayıb analiz edir.")

selected_pair = st.selectbox("Analiz obyekti:", ["EURUSD", "GBPUSD", "XAUUSD (Gold)", "BTCUSD"])

if st.button('Hər Bir Analizi Dərindən Oxu'):
    reports = []
    
    with st.status("Məlumatlar müxtəlif mənbələrdən toplanır...", expanded=True) as status:
        # 1-Cİ MƏNBƏ: NewsData API
        st.write("🔍 NewsData API yoxlanılır...")
        url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={selected_pair}&language=en"
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            for art in data.get('results', [])[:3]:
                content = art.get('content') or art.get('description', '')
                if len(content) > 100:
                    reports.append({"title": art['title'], "text": content, "source": "NewsData"})
        except:
            st.write("⚠️ NewsData limitdədir və ya xəta verdi.")

        # 2-Cİ MƏNBƏ (Fallback): RSS Feeds (Bloklanmayan rəsmi lentlər)
        if len(reports) < 2:
            st.write("🔄 Ehtiyat xəbər kanallarına keçid edilir...")
            rss_url = "https://www.dailyforex.com/forex-technical-analysis/rss"
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:5]:
                if selected_pair.lower() in entry.title.lower():
                    clean_text = BeautifulSoup(entry.summary, "html.parser").get_text()
                    reports.append({"title": entry.title, "text": clean_text, "source": "DailyForex RSS"})

        # ANALİZ MƏRHƏLƏSİ
        if reports:
            st.write(f"✅ {len(reports)} analiz mətni tapıldı. AI oxumağa başlayır...")
            for rep in reports:
                analysis = deep_ai_analysis(rep['text'])
                if analysis and len(analysis) >= 2:
                    decision = analysis[0].strip()
                    with st.expander(f"{decision} | {rep['title']}"):
                        st.write(f"**🧠 AI Təhlili:** {analysis[1].strip()}")
                        st.warning(f"**🎯 Texniki Səviyyələr:** {analysis[2].strip() if len(analysis)>2 else '-'}")
                        st.caption(f"Mənbə: {rep['source']}")
            status.update(label="Analiz tamamlandı!", state="complete")
        else:
            st.error("Heç bir mənbədən məlumat alınmadı. Lütfən API açarını və ya interneti yoxlayın.")
    
