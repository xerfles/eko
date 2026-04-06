import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# --- 📁 VERİ YÖNETİMİ (LiraPulse Veri Bankası) ---
DB_FILE = 'lirapulse_v15_data.csv'

def save_data(isim, profil, sehir, beklenti_9ay, toplam, dolar, risk, alim_kaybi, erime):
    user_ip = "127.0.0.1"
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        if headers:
            user_ip = headers.get("X-Forwarded-For", "127.0.0.1").split(",")[0]
    except:
        pass

    cols = ['Tarih', 'Katılımcı', 'Profil', 'Şehir', 'IP', 'Yıl_Sonu_Enf', 'Dolar_Beklentisi', 'Alım_Gücü_Kaybı', 'Reel_Kalan_TL']
    data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), isim, profil, sehir, user_ip, toplam, dolar, alim_kaybi, erime]], columns=cols)
    if not os.path.isfile(DB_FILE):
        data.to_csv(DB_FILE, index=False)
    else:
        data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 2026 GÜNCEL PİYASA VERİLERİ ---
GUNCEL_DOLAR = 44.92
GERCEKLESEN_3_AYLIK = 14.40 
TCMB_HEDEF = 22.0
MEVCUT_FAIZ = 37.0 

st.set_page_config(page_title="LiraPulse: Ekonomik Beklenti Simülatörü", layout="wide")

# --- 🧠 OTURUM HAFIZASI ---
if 'd_val' not in st.session_state: st.session_state.d_val = 15
if 'g_val' not in st.session_state: st.session_state.g_val = 25
if 'k_val' not in st.session_state: st.session_state.k_val = 35
if 'u_val' not in st.session_state: st.session_state.u_val = 20

# --- 🔭 MARKA PANELİ ---
st.title("🛰️ LiraPulse: Türkiye'nin İnteraktif Beklenti Endeksi")
st.caption("Veri odaklı gelecek vizyonu. Toplumsal nabzı simüle edin.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 Dolar/TL", f"{GUNCEL_DOLAR}")
m2.metric("🎯 TCMB Hedefi", f"%{TCMB_HEDEF}")
m3.metric("📊 Q1 Gerçekleşen", f"%{GERCEKLESEN_3_AYLIK}")
m4.metric("🏦 Politika Faizi", f"%{MEVCUT_FAIZ}")

st.divider()

# --- ⚙️ GİRİŞ BÖLÜMÜ ---
col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("⚙️ Senaryo ve Maaş Modelleme")
    u_name = st.text_input("Analist Adı/Rumuz:", "Analist_01")
    u_city = st.text_input("Şehir (Opsiyonel):", "İstanbul")
    u_salary = st.number_input("Güncel Aylık Maaşın (TL):", min_value=17002, value=35000, step=500)
    u_prof = st.selectbox("Harcama Sepeti Profili:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf", "Özel"])
    
    st.write("**🚀 Hızlı Ayarlar:**")
    s_col1, s_col2, s_col3 = st.columns(3)
    if s_col1.button("🌸 İyimser"):
        st.session_state.d_val, st.session_state.g_val, st.session_state.k_val, st.session_state.u_val = 5, 10, 15, 10
        st.rerun()
    if s_col2.button("📊 Piyasa"):
        st.session_state.d_val, st.session_state.g_val, st.session_state.k_val, st.session_state.u_val = 15, 25, 30, 20
        st.rerun()
    if s_col3.button("🌋 Kriz"):
        st.session_state.d_val, st.session_state.g_val, st.session_state.k_val, st.session_state.u_val = 50, 70, 90, 60
        st.rerun()

    d_a = st.slider("💵 Dolar Artışı (%)", 0, 100, key='d_val')
    g_a = st.slider("🛒 Gıda Artışı (%)", 0, 100, key='g_val')
    k_a = st.slider("🏠 Kira Artışı (%)", 0, 100, key='k_val')
    u_a = st.slider("🚗 Ulaşım Artışı (%)", 0, 100, key='u_val')
    risk_f = st.radio("⚠️ Temel Risk Odağı:", ["Dolar", "Fiyat Artışları", "Lojistik", "Hizmet Zamları"])

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.2, 0.25, 0.40, 0.15], "Emekli": [0.10, 0.50, 0.30, 0.10], "Çalışan": [0.20, 0.30, 0.30, 0.20], "Kamu Personeli": [0.20, 0.30, 0.30, 0.20], "Esnaf": [0.35, 0.25, 0.20, 0.20], "Özel": [0.25, 0.25, 0.25, 0.25]}
w = weights[u_prof]
katki_dolar = d_a * w[0]
katki_gida = g_a * w[1]
katki_kira = k_a * w[2]
katki_ulasim = u_a * w[3]

res_9ay = katki_dolar + katki_gida + katki_kira + katki_ulasim
res_total = GERCEKLESEN_3_AYLIK + res_9ay
alim_kaybi = (1 - (1 / (1 + res_total/100))) * 100
bin_tl_kalan = 1000 * (1 / (1 + res_total/100))
reel_maas = u_salary * (1 / (1 + res_total/100))

# --- 🏁 SONUÇLAR ---
with col_out:
    bg_color = "#d4edda" if res_total < 30 else ("#fff3cd" if res_total < 55 else "#f8d7da")
    st.markdown(f'<div style="background-color: {bg_color}; padding: 15px; border-radius: 10px; border: 1px solid #ddd;">'
                f'<h3 style="margin:0;">🏁 Yıl Sonu Beklentisi: %{res_total:.2f}</h3></div>', unsafe_allow_html=True)
    
    st.write("")
    r1, r2, r3 = st.columns(3)
    r1.metric("📉 Alım Gücü Kaybı", f"%{alim_kaybi:.1f}")
    r2.metric("🍞 Reel Maaş", f"{reel_maas:.0f} TL")
    world_status = "Arjantin Ligi" if res_total > 80 else ("Gelişmekte Olan" if res_total > 30 else "Stabil")
    r3.metric("🌍 Global Lig", world_status)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.write("### 📉 1.000 TL Yolculuğu")
        st.title(f"{bin_tl_kalan:.2f} TL")
        bar_color = "green" if res_total < 30 else ("orange" if res_total < 55 else "red")
        st.markdown(f'**Ekonomik Ateş Ölçer:**')
        st.markdown(f'<div style="background-color: lightgrey; border-radius: 5px;"><div style="background-color: {bar_color}; width: {min(res_total, 100)}%; height: 20px; border-radius: 5px;"></div></div>', unsafe_allow_html=True)
        
        st.info(f"💡 **Strateji:** {'Önden yüklemeli tüketim mantıklı.' if res_total > MEVCUT_FAIZ else 'TL mevduat koruyucu olabilir.'}")

    with c2:
        gauge = go.Figure(go.Indicator(mode = "gauge+number", value = alim_kaybi, title = {'text': "Değer Kaybı (%)"}, gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#e74c3c"}}))
        gauge.update_layout(height=230, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(gauge, use_container_width=True)

st.divider()

# --- 🕰️ ZAMAN TÜNELİ ---
st.subheader("📊 Fiyat Merdiveni: 1.000 TL Sepetinin Tırmanışı")
history_data = {"Yıl": ["2020", "2021", "2022", "2023", "2024", "2025", "BUGÜN", "2026 SONU"],
                "Sepet (TL)": [75, 95, 185, 350, 680, 890, 1000, 1000 * (1 + res_total/100)]}
df_line = pd.DataFrame(history_data)
fig_line = px.line(df_line, x="Yıl", y="Sepet (TL)", text="Sepet (TL)", markers=True)
fig_line.update_traces(textposition="top center", line_color="#e74c3c")
st.plotly_chart(fig_line, use_container_width=True)

# --- 💾 KAYIT ---
if st.button("💾 ANALİZİ LIRAPULSE VERİ BANKASINA KAYDET", type="primary", use_container_width=True):
    save_data(u_name, u_prof, u_city, res_9ay, res_total, GUNCEL_DOLAR*(1+d_a/100), risk_f, alim_kaybi, bin_tl_kalan)
    st.balloons()
    st.success("Analiz başarıyla kaydedildi! LiraPulse toplumsal verisine katkıda bulundunuz.")

# --- 🛡️ ADMIN ---
st.sidebar.markdown("---")
admin_key = st.sidebar.text_input("🔐 Admin", type="password")
if admin_key == "alper2026":
    if os.path.exists(DB_FILE):
        st.dataframe(pd.read_csv(DB_FILE), use_container_width=True)
