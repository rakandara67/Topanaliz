import streamlit as st
import google.generativeai as genai
from google.generativeai import types
import yfinance as yf

# --- KONFİQURASİYA ---
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao"

def start_ai():
    try:
        genai.configure(api_key=API_KEY)
        # Bura ÇOX VACİBDİR: Model obyektini birbaşa yaradırıq
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        return model
    except Exception as e:
        st.error(f"Sistem konfiqurasiya xətası: {e}")
        return None

st.set_page_config(page_title="Forex AI Final", page_icon="📈")
st.title("📈 Forex AI Professional")

# Aktivlər
symbol_map = {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "Qızıl (GOLD)": "GC=F"}
selected = st.selectbox("Aktiv seçin:", list(symbol_map.keys()))

if st.button('Analizi Tamamla'):
    model = start_ai()
    
    if model:
        with st.status("Məlumatlar emal olunur...") as status:
            # 1. Bazar məlumatı (Artıq işləyir)
            ticker = yf.Ticker(symbol_map[selected])
            hist = ticker.history(period="1d")
            price = hist['Close'].iloc[-1] if not hist.empty else "1.1850"
            
            st.metric("Cari Bazar Qiyməti", f"{price:.4f}")
            
            # 2. AI Analizi (Problem buradadır, indi düzəlir)
            status.write("AI ilə təhlükəsiz bağlantı qurulur...")
            
            prompt = f"{selected} üçün cari qiymət {price}-dir. Bu aktiv üçün qısa Forex analizi və AL/SAT tövsiyəsi ver."
            
            try:
                # Xətanın qarşısını almaq üçün ən sadə çağırış metodu
                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.success("AI Analizi Hazırdır:")
                st.write(response.text)
                status.update(label="Analiz uğurludur!", state="complete")
            except Exception as e:
                # Əgər hələ də 404 verirsə, alternativ 'v1' metodunu yoxla
                st.error(f"AI hələ də beta xətası verir. Zəhmət olmasa Reboot edin.")
                st.info(f"Sistem Mesajı: {e}")

# REBOOT TƏLİMATI
st.sidebar.warning("⚠️ Diqqət!")
st.sidebar.write("""
Əgər hələ də '404' xətası görürsünüzsə:
1. Streamlit ekranının aşağı sağındakı **'Manage app'** basın.
2. **'Reboot App'** düyməsini sıxın. 
Bu, serverdəki köhnə konfiqurasiyanı siləcək.
""")
