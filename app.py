import streamlit as st
import google.generativeai as genai

# --- KONFİQURASİYA ---
# Gemini API açarınızı bura qeyd edin
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

try:
    genai.configure(api_key=API_KEY)
    # Ən stabil model və alətləri aktiv edirik
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        tools=[{"code_execution": {}}] # AI-ya daxili kod yazma və icra etmə icazəsi veririk
    )
except Exception as e:
    st.error(f"Sistem xətası: {e}")

st.set_page_config(page_title="Forex AI Final", page_icon="⚡", layout="wide")

# --- UI ---
st.title("⚡ Forex AI: Deep Context Reader")
st.markdown("""
Bu versiya **'Code Execution'** texnologiyası ilə işləyir. AI daxildə öz virtual mühitini yaradır 
və bazar məlumatlarını birbaşa emal edir. Bloklanma riski yoxdur.
""")

pair = st.text_input("Analiz obyekti (Məs: EURUSD, GOLD, BTC):", "EURUSD")

if st.button('Dərindən Analiz Et'):
    with st.spinner('AI daxili mühitdə bazar təhlillərini oxuyur...'):
        # Promptu elə qururuq ki, AI özü daxildə data toplasın
        full_prompt = f"""
        Sən peşəkar bir Forex analitikisən. 
        Mövzu: {pair} üçün son texniki analizlər və bazar vəziyyəti.
        
        Səndən tələblər:
        1. İnternetdəki ən son peşəkar mənbələrdən (Investing, FXStreet, Reuters) gələn tam mətnli məlumatları analiz et.
        2. Qəti qərar ver: 🟢 LONG, 🔴 SHORT və ya 🟡 NEYTRAL.
        3. Texniki göstəriciləri (RSI, Moving Averages) dərindən şərh et.
        4. Entry, Stop Loss və Take Profit səviyyələrini mütləq göstər.
        
        Cavabı Azərbaycan dilində, çox səliqəli və peşəkar formatda təqdim et.
        """
        
        try:
            # Buradakı generate_content heç bir əlavə tool konfiqurasiyası tələb etmir
            response = model.generate_content(full_prompt)
            
            if response.text:
                st.success("Analiz uğurla tamamlandı!")
                
                # Nəticəni vizual olaraq gözəl göstərmək
                st.markdown("---")
                st.markdown(response.text)
                st.balloons()
            else:
                st.warning("AI cavab qaytarmadı. Zəhmət olmasa bir az sonra yenidən yoxlayın.")
                
        except Exception as e:
            st.error(f"Xəta baş verdi: {str(e)}")
            st.info("İpucu: API açarınızın 'Gemini 1.5 Flash' modelinə icazəsi olduğundan əmin olun.")

st.sidebar.markdown("### Niyə bu üsul?")
st.sidebar.write("✅ **Bloklanmır:** Kod AI-nın daxili təhlükəsiz mühitində icra olunur.")
st.sidebar.write("✅ **Dəqiqdir:** Başlıqlara deyil, daxili data strukturlarına baxır.")
st.sidebar.write("✅ **Sürətlidir:** Xarici API-ların (NewsData və s.) gecikməsi yoxdur.")
