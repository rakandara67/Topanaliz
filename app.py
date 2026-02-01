import streamlit as st
import google.generativeai as genai

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

try:
    genai.configure(api_key=API_KEY)
    # Google Search funksiyasını aktivləşdiririk
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        tools=[{"google_search_retrieval": {}}] 
    )
except Exception as e:
    st.error(f"Sistem xətası: {e}")

st.set_page_config(page_title="Forex AI Oracle", page_icon="🔮", layout="wide")

# --- UI ---
st.title("🔮 Forex AI Oracle: Canlı Bazar Təhlili")
st.markdown("""
Bu sistem artıq saytlara girmir. O, birbaşa **Google-un ən son məlumat bazasını** tarayaraq 
peşəkar agentliklərin (Reuters, Investing, FXStreet) tam təhlillərini oxuyur.
""")

col1, col2 = st.columns([2, 1])
with col1:
    pair = st.text_input("Analiz ediləcək cütlük/aktiv:", "EURUSD technical analysis today")
with col2:
    style = st.selectbox("Analiz dərinliyi:", ["Normal", "Çox Dərin (Full Text)"])

if st.button('Məqalələri Oxu və Qərar Ver'):
    with st.spinner('Google üzərindən dünya agentliklərinin tam mətnləri analiz edilir...'):
        prompt = f"""
        Aşağıdakı mövzu üzrə internetdəki son 24 saatın ən peşəkar maliyyə analizlərini (Reuters, FXStreet, Investing) tap:
        "{pair}"
        
        Tapşırıq:
        1. Ən azı 3 fərqli analitikin fikrini dərindən oxu.
        2. Qəti bir qərar çıxar: 🟢 LONG (Alış), 🔴 SHORT (Satış) və ya 🟡 NEYTRAL.
        3. Azərbaycan dilində mətndəki texniki səbəbləri (RSI, Trend, Support/Resistance) izah et.
        4. Mətndə gördüyün bütün qiymət səviyyələrini (Entry, SL, TP) qeyd et.
        
        Cavabı bu formatda ver:
        [QƏRAR]: ...
        [DETALLI ANALİZ]: ...
        [TEXNİKİ SƏVİYYƏLƏR]: ...
        [MƏNBƏLƏR]: (Oxuduğun saytların adları)
        """
        
        try:
            response = model.generate_content(prompt)
            
            if response.text:
                st.success("Analiz tamamlandı!")
                # Nəticəni vizual bloklara bölək
                res_text = response.text
                
                # Ekranda gözəl göstərmək
                st.markdown("### 📊 AI-ın Yekun Bazar Rəyi")
                st.write(res_text)
                
                st.balloons()
            else:
                st.warning("Məlumat tapılmadı. Zəhmət olmasa başqa bir cütlük yoxlayın.")
                
        except Exception as e:
            st.error(f"Analiz zamanı xəta: {e}")

st.sidebar.markdown("---")
st.sidebar.info("Bu metod saytların 'bot bloklamasını' tamamilə aşır, çünki məlumatı Google AI özü daxildən gətirir.")
        
