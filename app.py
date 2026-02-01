import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai

# --- KONFİQURASİYA ---
GEMINI_API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"
NEWS_API_KEY = "pub_8a60966e639742c09af24649e4e41784" # newsdata.io saytından aldığınız açar

try:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Xətası: {e}")

st.set_page_config(page_title="Forex Deep Intelligence", page_icon="🔬", layout="wide")

def deep_ai_analysis(full_text):
    """Məqalənin tam mətni daxilinə girib texniki siqnalları tapır"""
    prompt = f"""
    Sən milyard dollarlıq fondların baş Forex analitikisən. Aşağıdakı bazar təhlilini dərindən oxu:
    
    "{full_text}"
    
    Tapşırıq:
    1. Sentiment: 🟢 LONG, 🔴 SHORT və ya 🟡 NEYTRAL?
    2. Niyə?: Azərbaycan dilində 1 cümləlik peşəkar texniki izah.
    3. Səviyyələr: Mətndə tapdığın bütün qiymət hədəflərini (Entry, SL, TP) çıxar.
    
    Format: [QƏRAR] | [İZAH] | [SƏVİYYƏLƏR]
    """
    try:
        response = ai_model.generate_content(prompt)
        return response.text.split("|")
    except:
        return None

# --- UI ---
st.title("🔬 Forex AI: Professional Deep Reader")
st.markdown("Bu sistem rəsmi xəbər agentliklərinin **tam mətnli** məqalələrini oxuyaraq qərar verir.")

query = st.text_input("Axtarış üçün açar söz (Məs: EURUSD technical analysis):", "EURUSD forecast")

if st.button('Dərindən Analiz Et (Full Text Search)'):
    with st.spinner('Dünya agentliklərinin tam mətnləri çəkilir...'):
        # NewsData.io vasitəsilə tam mətnli xəbər axtarışı
        url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={query}&language=en&category=business"
        
        try:
            response = requests.get(url)
            data = response.json()
            articles = data.get('results', [])
            
            if articles:
                found = 0
                for art in articles[:7]: # İlk 7 tam mətnli analizi oxu
                    # Məqalənin tam mətnini götürürük (description və ya content)
                    content = art.get('content') or art.get('description', '')
                    title = art.get('title', 'Başlıqsız Analiz')
                    
                    if len(content) > 200: # Yalnız dolğun mətnləri analiz et
                        analysis = deep_ai_analysis(content)
                        if analysis and len(analysis) >= 2:
                            found += 1
                            decision = analysis[0].strip()
                            with st.expander(f"{decision} | {title[:80]}..."):
                                st.write(f"**🧠 AI Təhlili:** {analysis[1].strip()}")
                                st.warning(f"**🎯 Texniki Səviyyələr:** {analysis[2].strip() if len(analysis)>2 else '-'}")
                                st.caption(f"Mənbə: {art.get('source_id')} | Tarix: {art.get('pubDate')}")
                                st.link_button("Məqalənin özünə bax", art.get('link'))
                
                if found == 0:
                    st.warning("Xəbərlər tapıldı, lakin içində yetərli analiz mətni yoxdur.")
                else:
                    st.balloons()
            else:
                st.error("Heç bir rəsmi analiz mətni tapılmadı. API limitini və ya açar sözü yoxlayın.")
        except Exception as e:
            st.error(f"Sistem xətası: {e}")

st.sidebar.info("Bu versiya Google və ya Yahoo-nun qısa başlıqları ilə kifayətlənmir, birbaşa News API-dan gələn 500-2000 sözlük məqalələri emal edir.")
    
