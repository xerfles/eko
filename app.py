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

# --- 📊 5 NİSAN 2026 GÜNCEL VERİLER ---
GUNCEL_DOLAR = 44.92
GERCEKLESEN_3_AYLIK = 14.40 
TCMB_HEDEF = 22.0
MEVCUT_FAIZ = 37.0 

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="MacroVision Ultimate v10.5", layout="wide")

st.title("🔭 MacroVision Ultimate: Kur ve Alım Gücü Analiz Merkezi")
st.caption(f"Veri Seti: 2026/Q2 | Analiz Tarihi: {datetime.now().strftime('%d.%m.%Y')}")

# Üst Metrikler
m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 USD/TRY (Şu An)", f"{GUNCEL_DOLAR} TL")
m2.metric("📊 Q1 Enflasyon", f"%{GERCEKLESEN_3_AYLIK}")
m3.metric("🎯 Yıl Sonu Hedefi", f"%{TCMB_HEDEF}")
m4.metric("🏦 Mevduat Faizi", f"%{MEVCUT_FAIZ}")

st.divider()

# --- 🛠️ GİRDİ PANELİ ---
col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("⚙️ Senin Senaryon")
    user_name = st.text_input("Analist Adı:", "Analist_001")
    user_prof = st.selectbox("Harcama Sepeti:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
    
    st.write("---")
    st.write("**📈 Gelecek 9 Ay Artış Beklentiniz (%)**")
    d_a = st.slider("💵 Dolar Kuru Artışı (%)", 0, 100, 15)
    
    tahmini_kur_tl = GUNCEL_DOLAR * (1 + d_a/100)
    st.info(f"💡 Seçtiğiniz %{d_a} artış ile Dolar: **{tahmini_kur_tl:.2f} TL** olur.")
    
    g_a = st.slider("🛒 Gıda ve Market (%)", 0, 100, 25)
    k_a = st.slider("🏠 Kira ve Barınma (%)", 0, 100, 35)
    u_a = st.slider("🚗 Ulaşım ve Akaryakıt (%)", 0, 100, 20)
    
    risk_f = st.radio("⚠️ Temel Risk Odağı:", ["Kur Geçişkenliği", "Talep Enflasyonu", "Maliyet Baskısı", "Hizmet Katılığı"])

# --- 🧮 HESAPLAMA MOTORU ---
weights = {"Öğrenci": [0.2, 0.25, 0.40, 0.15], "Emekli": [0.10, 0.50, 0.30, 0.10], "Çalışan": [0.20, 0.30, 0.30, 0.20], "Kamu Personeli": [0.20, 0.30, 0.30, 0.20], "Esnaf": [0.35, 0.25, 0.20, 0.20]}
w = weights[user_prof]
res_9ay = (d_a * w[0] + g_a * w[1] + k_a * w[2] + u_a * w[3])
res_total = GERCEKLESEN_3_AYLIK + res_9ay

alim_kaybi = (1 - (1 / (1 + res_total/100))) * 100
bin_tl_kalan = 1000 * (1 / (1 + res_total/100))

# --- 🏁 SONUÇ PANELİ ---
with col_out:
    st.subheader("🏁 Enflasyon ve Alım Gücü Sonuçları")
    
    r1, r2, r3 = st.columns(3)
    r1.metric("📈 Yıl Sonu Toplam Enf.", f"%{res_total:.2f}")
    r2.metric("💵 Senin Dolar Tahminin", f"{tahmini_kur_tl:.2f} TL")
    r3.metric("📉 Alım Gücü Kaybı", f"%{alim_kaybi:.1f}")

    st.write("---")
    # 📉 ALIM GÜCÜ VURGUSU
    c1, c2 = st.columns(2)
    with c1:
        st.write("### 📉 1.000 TL'nin Yıl Sonu Değeri")
        st.title(f"{bin_tl_kalan:.2f} TL")
        st.caption(f"Yıl sonundaki bu para, bugünün {bin_tl_kalan:.2f} TL'si ile aynı malı alabilecek.")
    with c2:
        gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = alim_kaybi,
            title = {'text': "Paranın Değer Kaybı (%)"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#e74c3c"}}))
        gauge.update_layout(height=230, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(gauge, use_container_width=True)

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=[d_a, g_a, k_a, u_a], theta=['Dolar','Gıda','Kira','Ulaşım'], fill='toself', line_color='#2ecc71'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=300)
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# --- 💹 KUR ŞOKU DUYARLILIK ANALİZİ (İnsanların Anlayacağı Sürüm) ---
st.subheader("🔍 Olası Dolar Artışlarının Enflasyon Üzerindeki Etkisi")
st.write("Gıda ve kira gibi diğer tüm artış beklentilerin sabit kalsa bile, doların artması durumunda enflasyonun ve alım gücünün nasıl etkileneceğini incele:")

prices = [45, 48, 52, 55, 60, 70]
matrix_data = []
for p in prices:
    temp_d_a = ((p / GUNCEL_DOLAR) - 1) * 100
    temp_total = GERCEKLESEN_3_AYLIK + (temp_d_a * w[0] + g_a * w[1] + k_a * w[2] + u_a * w[3])
    temp_alim_gucu = 1000 / (1 + temp_total/100)
    matrix_data.append({
        "Dolar Kuru Senaryosu": f"{p} TL", 
        "Dolar Artış Oranı": f"%{temp_d_a:.1f}",
        "Tahmini Yıl Sonu Enflasyon": f"%{temp_total:.2f}", 
        "1.000 TL'nin Kalan Gücü": f"{temp_alim_gucu:.0f} TL"
    })
st.table(pd.DataFrame(matrix_data))

if st.button("💾 ANALİZİ KAYDET", type="primary"):
    save_data(user_name, user_prof, res_9ay, res_total, tahmini_kur_tl, risk_f, alim_kaybi, bin_tl_kalan)
    st.balloons()
    st.success("Veriler başarıyla loglandı!")

# --- 🛡️ ADMIN ---
st.sidebar.markdown("---")
admin_key = st.sidebar.text_input("🔐 Admin", type="password")
if admin_key == "alper2026":
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        st.dataframe(df, use_container_width=True)
