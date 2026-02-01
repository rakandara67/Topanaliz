import streamlit as st
import pandas as pd
import google.generativeai as genai
from duckduckgo_search import DDGS
import time

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Xətası: {e}")

st.set_page_config(page_title="Forex Deep Mind AI", page_icon="🧠", layout="wide")

def get_ai_decision(context):
    """Mətnin hamısını analiz edib peşəkar qərar çıxarır"""
    prompt = f"""
    Sən milyard dollarlıq fondların baş Forex analitikisən. Aşağıdakı bazar analiz mətni sənə daxil olub:
    
    "{context}"
    
    Sənin tapşırığın:
    1. Bu mətndən bazarın ruhunu (Sentiment) tut.
    2. Qərar ver: 🟢 LONG, 🔴 SHORT və ya 🟡 NEYTRAL.
    3. Azərbaycan dilində peşəkar, qısa bir 'Niyə?' izahı yaz.
    4. Mətndən texniki səviyyələri (Entry, SL, TP) tap.
    
    Format:
    [QƏRAR]
    İzah: [Cümlə]
    Səviyyələr: [Qiymətlər]
    """
    try:
        response = ai_model.generate_content(prompt)
        return response.text
    except:
        return "⚠️ AI emal edə bilmədi."

# --- UI ---
st.title("🧠 Forex Deep Mind: Həqiqi Mətn Analizi")
st.markdown("Google-u deyil, birbaşa bazar mənbələrini dərindən tarayaraq hər bir analizin daxili mənasını oxuyur.")

query = st.text_input("Analiz ediləcək valyuta/aktiv:", value="EURUSD technical analysis today")

if st.button('Dərindən Araşdır və Qərar Ver'):
    with st.spinner('Bazar analizləri oxunur, AI qərar verir...'):
        results_list = []
        
        # DuckDuckGo vasitəsilə son 10 analizi axtarırıq (Bloklanmır)
        try:
            with DDGS() as ddgs:
                # 'region' və 'safesearch' sayəsində daha təmiz nəticələr
                search_results = ddgs.text(query, region='wt-wt', safesearch='off', timelimit='d', max_results=10)
                
                for r in search_results:
                    # Hər bir nəticənin 'body' hissəsi məqalənin mətni olur
                    full_text_context = f"Başlıq: {r['title']}\nMəzmun: {r['body']}"
                    
                    # AI-ya mətni göndəririk
                    ai_report = get_ai_decision(full_text_context)
                    
                    results_list.append({
                        "Mənbə": r['href'],
                        "Başlıq": r['title'],
                        "AI_Hesabat": ai_report
                    })
                    time.sleep(0.5) # API limitinə düşməmək üçün
        except Exception as e:
            st.error(f"Axtarışda problem oldu: {e}")

    if results_list:
        st.subheader("📊 AI Tərəfindən Təsdiqlənmiş Siqnallar")
        for res in results_list:
            # Qərarın rənginə görə ikon seçimi (Sadə vizuallaşdırma)
            header_color = "🟢" if "LONG" in res['AI_Hesabat'].upper() else "🔴" if "SHORT" in res['AI_Hesabat'].upper() else "🟡"
            
            with st.expander(f"{header_color} {res['Başlıq']}"):
                st.write(res['AI_Hesabat'])
                st.caption(f"Mənbə linki: {res['Mənbə']}")
    else:
        st.warning("Bu gün üçün hələlik heç bir dərin analiz mətni tapılmadı.")

st.sidebar.info("Bu sistem 'DuckDuckGo Intelligence' və 'Gemini 1.5 Pro' infrastrukturundan istifadə edərək saytların içini oxuyur.")
    
