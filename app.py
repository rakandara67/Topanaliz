import streamlit as st
import google.generativeai as genai
from googlesearch import search
import requests
from bs4 import BeautifulSoup

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI bağlantı xətası: {e}")

st.set_page_config(page_title="Forex AI Final", page_icon="📈", layout="wide")

st.title("📈 Forex AI: Həqiqi Mətn Analizi")
st.markdown("Bu sistem Google-da ən son analizləri tapır, məqalələrin daxilinə girir və tam mətni AI-ya oxudur.")

query = st.text_input("Axtarış sözü:", "EURUSD technical analysis investing.com")

if st.button('Dərindən Analiz Et'):
    with st.spinner('Məqalələr oxunur...'):
        try:
            # 1. Google-da son analizləri tapırıq
            links = []
            for j in search(query, num_results=3):
                links.append(j)
            
            if not links:
                st.warning("Məqalə tapılmadı.")
            else:
                for link in links:
                    st.write(f"📖 Oxunur: {link}")
                    
                    # 2. Saytın daxilinə girib mətni çəkirik
                    try:
                        header = {'User-Agent': 'Mozilla/5.0'}
                        page = requests.get(link, headers=header, timeout=10)
                        soup = BeautifulSoup(page.content, 'html.parser')
                        
                        # Saytdakı lazımsız reklamları atıb əsas mətni götürürük
                        paragraphs = soup.find_all('p')
                        article_text = " ".join([p.get_text() for p in paragraphs[:15]]) # İlk 15 paraqraf bəs edir
                        
                        if len(article_text) > 500:
                            # 3. AI-ya tam mətni göndərib analiz etdiririk
                            prompt = f"""
                            Aşağıdakı Forex analiz məqaləsini dərindən oxu:
                            "{article_text}"
                            
                            Səndən tələblər:
                            1. Qərar: 🟢 LONG, 🔴 SHORT və ya 🟡 NEYTRAL?
                            2. Səbəb: Azərbaycan dilində 1 cümləlik texniki izah.
                            3. Səviyyələr: Entry, SL, TP rəqəmlərini tap.
                            """
                            response = model.generate_content(prompt)
                            
                            with st.chat_message("assistant"):
                                st.markdown(response.text)
                                st.caption(f"Mənbə: {link}")
                        else:
                            st.write("⚠️ Bu saytın mətni çox qısadır, növbətiyə keçilir.")
                    except:
                        st.write("❌ Bu sayta giriş mümkün olmadı.")
                
                st.success("Bütün mümkün analizlər tamamlandı!")
                st.balloons()
        except Exception as e:
            st.error(f"Sistem xətası: {e}")

