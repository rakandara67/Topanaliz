import streamlit as st
import pandas as pd
import feedparser
import re

st.set_page_config(page_title="Forex Analiz & Qərar", page_icon="📈")

def get_sentiment(text):
    """Mətni analiz edib istiqamət və xülasə təyin edir"""
    text = text.lower()
    
    # Açar sözlər bazası
    long_keywords = ['bullish', 'long', 'yükseliş', 'artış', 'destek', 'alım', 'buy', 'higher']
    short_keywords = ['bearish', 'short', 'düşüş', 'gerileme', 'direnç', 'satış', 'sell', 'lower']
    
    # Qərar tərəfi
    is_long = any(word in text for word in long_keywords)
    is_short = any(word in text for word in short_keywords)
    
    if is_long and not is_short:
        return "🟢 LONG", "Alıcılar üstünlük təşkil edir. Artım ehtimalı yüksəkdir."
    elif is_short and not is_long:
        return "🔴 SHORT", "Satıcılar təzyiqi artırır. Eniş gözlənilir."
    else:
        return "🟡 NEYTRAL", "Bazar hazırda qərarsızdır, gözləmək tövsiyə olunur."

def fetch_news(site_name, site_url):
    """Google News vasitəsilə saytın son xəbərlərini bloklanmadan çəkir"""
    rss_url = f"https://news.google.com/rss/search?q=site:{site_url}+forex+analysis&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    results = []
    for entry in feed.entries[:10]:
        decision, summary = get_sentiment(entry.title)
        results.append({
            "Mənbə": site_name,
            "Analiz": entry.title,
            "Qərar": decision,
            "Xülasə (AZ)": summary,
            "Link": entry.link
        })
    return results

# --- INTERFACE ---
st.title("📊 Forex Canlı Analiz Mərkəzi")
st.info("DailyForex və FXStreet analizləri əsasında avtomatik qərarlar.")

if st.button('Məlumatları Yenilə'):
    with st.spinner('Analizlər emal edilir...'):
        # Bloklanmayan mənbələrdən çəkim
        df_daily = fetch_news("DailyForex", "dailyforex.com")
        df_fx = fetch_news("FXStreet", "fxstreet.com")
        
        all_data = df_daily + df_fx
        
        if all_data:
            df = pd.DataFrame(all_data)
            
            # 1. Cədvəl Görünüşü
            st.subheader("📌 Son Analizlər və Siqnallar")
            st.dataframe(df[['Mənbə', 'Analiz', 'Qərar']], use_container_width=True)
            
            # 2. Detallı Analiz Kartları
            st.subheader("📝 Qərar Xülasələri")
            for item in all_data:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{item['Mənbə']}**: {item['Analiz']}")
                    st.caption(f"İzah: {item['Xülasə (AZ)']}")
                with col2:
                    st.success(item['Qərar']) if "LONG" in item['Qərar'] else st.error(item['Qərar']) if "SHORT" in item['Qərar'] else st.warning(item['Qərar'])
                    st.markdown(f"[Oxu]({item['Link']})")
                st.divider()
        else:
            st.warning("Hal-hazırda yeni analiz tapılmadı. Bir az sonra yenidən yoxlayın.")

st.sidebar.markdown("""
### Necə istifadə etməli?
1. **Yenilə** düyməsini basın.
2. **Qərar** sütununda LONG və ya SHORT siqnallarına baxın.
3. **Xülasə** hissəsində Azərbaycan dilində qısa izahı oxuyun.
""")
