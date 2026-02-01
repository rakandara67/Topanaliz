import streamlit as st
import requests
import google.generativeai as genai

# --- KONFİQURASİYA ---
GEMINI_API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"
NEWS_API_KEY = "pub_8a60966e639742c09af24649e4e41784"

try:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Xətası: {e}")

st.set_page_config(page_title="Forex Deep Mind", page_icon="🔬", layout="wide")

def deep_ai_analysis(full_text):
    """Məqalənin tam mətnini oxuyub siqnal çıxaran beyin"""
    prompt = f"""
    Sən peşəkar Forex analitikisən. Aşağıdakı bazar xəbərini dərindən oxu:
    "{full_text[:4000]}"
    
    Tapşırıq:
    1. Sentiment: 🟢 LONG, 🔴 SHORT və ya 🟡 NEYTRAL?
    2. Səbəb: Azərbaycan dilində 1 cümləlik texniki izah.
    3. Qiymətlər: Entry, SL, TP rəqəmlərini mətndən tap.
    
    Format: [QƏRAR] | [İZAH] | [SƏVİYYƏLƏR]
    """
    try:
        response = ai_model.generate_content(prompt)
        return response.text.split("|")
    except:
        return None

# --- UI ---
st.title("🔬 Forex AI: Professional Deep Reader")
st.info("Bu versiya rəsmi agentliklərin tam mətnlərini analiz edir.")

# Axtarış sorğularını sadələşdirək ki, API boş nəticə verməsin
query_options = {
    "EUR/USD": "EURUSD technical analysis",
    "GOLD (XAU)": "Gold price forecast",
    "GBP/USD": "GBPUSD signal",
    "BITCOIN": "Bitcoin market update"
}

selected_pair = st.selectbox("Analiz obyekti:", list(query_options.keys()))
search_query = query_options[selected_pair]

if st.button('Dərindən Analiz Et'):
    # NewsData.io URL - Axtarışı daha effektiv etmək üçün 'q' parametrini optimallaşdırdıq
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={search_query}&language=en"
    
    with st.spinner('Tam mətnli məqalələr toplanır...'):
        try:
            r = requests.get(url)
            data = r.json()
            articles = data.get('results', [])
            
            if articles:
                found_count = 0
                for art in articles[:5]:
                    # Məqalənin içini 'content' bölməsindən götürürük
                    content = art.get('content') or art.get('description', '')
                    title = art.get('title', 'Başlıqsız Məqalə')
                    
                    if len(content) > 150: # Yalnız dolğun mətnləri analiz et
                        analysis = deep_ai_analysis(content)
                        if analysis and len(analysis) >= 2:
                            found_count += 1
                            decision = analysis[0].strip()
                            
                            with st.expander(f"{decision} | {title[:80]}..."):
                                st.write(f"**🧠 AI Təhlili:** {analysis[1].strip()}")
                                st.warning(f"**🎯 Səviyyələr:** {analysis[2].strip() if len(analysis)>2 else '-'}")
                                st.caption(f"Mənbə: {art.get('source_id')} | [Məqaləyə keçid]({art.get('link')})")
                
                if found_count == 0:
                    st.warning("Xəbərlər tapıldı, lakin içində dərin analiz üçün yetərli mətn yoxdur.")
                else:
                    st.balloons()
            else:
                st.error("NewsData API-dan məlumat gəlmədi. API açarını və ya limitinizi yoxlayın.")
                
        except Exception as e:
            st.error(f"Sistem xətası: {e}")
    
