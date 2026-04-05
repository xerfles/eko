import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# --- 📁 VERİ YÖNETİMİ ---
DB_FILE = 'macrovision_v10_final.csv'

def save_data(isim, profil, beklenti_9ay, toplam, dolar, risk, alim_kaybi, erime):
    cols = ['Tarih', 'Katılımcı', 'Profil', '9_Ay_Enf', 'Yıl_Sonu_Toplam', 'Dolar_Beklentisi', 'Ana_Risk', 'Değer_Kaybı_Yüzde', 'Bin_TL_Kalan']
    data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), isim, profil, beklenti_9ay, toplam, dolar, risk, alim_kaybi, erime
    ]], columns=cols)
    
    if not os.path.isfile(DB_FILE):
        data.to_csv(DB_FILE, index=False)
    else:
        data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 5 NİSAN 2026 GÜNCEL EKONOMİK VERİLER ---
GUNCEL_DOLAR = 44.92
GERCEKLESEN_3_AYLIK = 14.40 
TCMB_HEDEF = 22.0
MEVCUT_FAIZ = 37.0  # 🎯 Kanka burayı senin dediğin gibi 37'ye çektim

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="MacroVision Ultimate v10.3", layout="wide")

# --- 🔭 ÜST PANEL ---
st.title("🔭 MacroVision Ultimate: Nisan 2026 Analiz Paneli")
st.caption(f"Veri Seti: 2026/Q2 | Analiz Tarihi: {datetime.now().strftime('%d.%m.%Y')}")

m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 USD/TRY (Spot)", f"{GUNCEL_DOLAR} TL", "Piyasa")
m2.metric("📊 Q1 Enflasyon", f"%{GERCEKLESEN_3_AYLIK}", "Gerçekleşen")
m3.metric("🎯 TCMB Hedefi", f"%{TCMB_HEDEF}", "Yıl Sonu")
m4.metric("🏦 Mevduat Faizi", f"%{MEVCUT_FAIZ}", "Güncel")

st.divider()

# --- 🛠️ PARAMETRE VE SİMÜLASYON ---
col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("⚙️ Senin Senaryon")
    user_name = st.text_input("Analist Adı:", "Analist_001")
    user_prof = st.selectbox("Harcama Sepeti:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
    
    st.write("---")
    st.write("**📈 Gelecek 9 Ay Artış Beklentiniz (%)**")
    d_a = st.slider("💵 Dolar Kuru", 0, 100, 15)
    g_a = st.slider("🛒 Gıda ve Market", 0, 100, 25)
    k_a = st.slider("🏠 Kira ve Barınma", 0, 100, 35)
    u_a = st.slider("🚗 Ulaşım ve Akaryakıt", 0, 100, 20)
    
    risk_f = st.radio("⚠️ Temel Risk Odağı:", ["Kur Geçişkenliği", "Talep Enflasyonu", "Maliyet Baskısı", "Hizmet Katılığı"])

# --- 🧮 HESAPLAMA MOTORU ---
weights = {"Öğrenci": [0.2, 0.25, 0.40, 0.15], "Emekli": [0.10, 0.50, 0.30, 0.10], "Çalışan": [0.20, 0.30, 0.30, 0.20], "Kamu Personeli": [0.20, 0.30, 0.30, 0.20], "Esnaf": [0.35, 0.25, 0.20, 0.20]}
w = weights[user_prof]
res_9ay = (d_a * w[0] + g_a * w[1] + k_a * w[2] + u_a * w[3])
res_total = GERCEKLESEN_3_AYLIK + res_9ay
res_usd = GUNCEL_DOLAR * (1 + d_a/100)

alim_kaybi = (1 - (1 / (1 + res_total/100))) * 100
bin_tl_kalan = 1000 * (1 / (1 + res_total/100))

with col_out:
    st.subheader("🏁 Projeksiyon Çıktıları")
    c1, c2 = st.columns(2)
    with c1:
        st.write("### 📉 1.000 TL'nin Yıl Sonu Değeri")
        st.title(f"{bin_tl_kalan:.2f} TL")
        st.caption(f"Paran sene sonunda bugünkü 1.000 TL'ye göre bu alım gücüne sahip olacak.")
    with c2:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = alim_kaybi,
            title = {'text': "Alım Gücü Kaybı (%)"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#e74c3c"}}))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=[d_a, g_a, k_a, u_a], theta=['Dolar','Gıda','Kira','Ulaşım'], fill='toself', line_color='#2ecc71'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350)
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# --- 💹 DUYARLILIK ANALİZİ ---
st.subheader("🔍 Kur Duyarlılık Analizi")
prices = [45, 48, 52, 55, 60]
matrix_data = []
for p in prices:
    temp_d_a = ((p / GUNCEL_DOLAR) - 1) * 100
    temp_9ay = (temp_d_a * w[0] + g_a * w[1] + k_a * w[2] + u_a * w[3])
    temp_total = GERCEKLESEN_3_AYLIK + temp_9ay
    matrix_data.append({"Dolar": f"{p} TL", "Enflasyon": f"%{temp_total:.2f}", "1.000 TL Gücü": f"{1000/(1+temp_total/100):.0f} TL"})
st.table(pd.DataFrame(matrix_data))

if st.button("💾 ANALİZİ KAYDET", type="primary"):
    save_data(user_name, user_prof, res_9ay, res_total, res_usd, risk_f, alim_kaybi, bin_tl_kalan)
    st.balloons()
    st.success("Veriler başarıyla loglandı!")

# --- 🛡️ ADMIN PANEL ---
st.sidebar.markdown("---")
admin_key = st.sidebar.text_input("🔐 Admin", type="password")

if admin_key == "alper2026":
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        st.dataframe(df, use_container_width=True)
        st.plotly_chart(px.violin(df, y="Yıl_Sonu_Toplam", x="Profil", box=True, color="Profil"))
