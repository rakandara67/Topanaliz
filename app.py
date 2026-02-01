import streamlit as st
import google.generativeai as genai
from googlesearch import search
import requests
from bs4 import BeautifulSoup

# --- KONFİQURASİYA ---
# API açarınızı bura tək dırnaq içində yazın
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

try:
    genai.configure(api_key=API_KEY)
    # Heç bir beta versiya və ya tool istifadə etmədən birbaşa model
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI bağlantı xətası: {e}")

st.set_page_config(page_title="Forex Deep Reader", page_icon="📈")

st.title("📈 Forex AI: Deep Reader")

pair = st.text_input("Axtarış sözü (Məs: EURUSD technical analysis):", "EURUSD forecast news")

if st.button('Analiz Et'):
    with st.spinner('İnternetdə analizlər axtarılır və oxunur...'):
        try:
            # Google-da axtarış edirik
            # googlesearch-python kitabxanası burada işə düşür
            search_results = list(search(pair, num_results=3))
            
            if not search_results:
                st.warning("Google-da heç bir məqalə tapılmadı.")
            else:
                for link in search_results:
                    st.write(f"🔍 Oxunur: {link}")
                    try:
                        # Saytın daxili mətnini çəkirik
                        res = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                        soup = BeautifulSoup(res.content, 'html.parser')
                        text = " ".join([p.get_text() for p in soup.find_all('p')[:10]])

                        if len(text) > 200:
                            # AI-ya mətni göndəririk
                            prompt = f"Aşağıdakı mətni oxu və Forex analizi çıxar (Qərar, Səbəb, Səviyyələr): {text}"
                            response = model.generate_content(prompt)
                            
                            with st.expander(f"Analiz nəticəsi: {link[:40]}..."):
                                st.write(response.text)
                        else:
                            st.info("Mətn çox qısadır, növbəti mənbəyə keçilir.")
                    except:
                        st.error(f"Bu sayt oxuna bilmədi: {link}")
        except Exception as e:
            st.error(f"Sistem xətası: {e}")
