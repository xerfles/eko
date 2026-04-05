import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime

# --- 📁 VERİ YÖNETİMİ ---
DB_FILE = 'macrovision_v12_final.csv'

def save_data(isim, profil, beklenti_9ay, toplam, dolar, risk, alim_kaybi, erime):
    cols = ['Tarih', 'Katılımcı', 'Profil', '9_Ay_Enf', 'Yıl_Sonu_Toplam', 'Dolar_Beklentisi', 'Ana_Risk', 'Değer_Kaybı_Yüzde', 'Bin_TL_Kalan']
    data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), isim, profil, beklenti_9ay, toplam, dolar, risk, alim_kaybi, erime]], columns=cols)
    if not os.path.isfile(DB_FILE): data.to_csv(DB_FILE, index=False)
    else: data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 2026 GÜNCEL VERİLER ---
GUNCEL_DOLAR = 44.92
GERCEKLESEN_3_AYLIK = 14.40 
TCMB_HEDEF = 22.0
MEVCUT_FAIZ = 37.0 

st.set_page_config(page_title="MacroVision v13.1 Elite", layout="wide")

# --- 🧠 OTURUM HAFIZASI ---
if 'd_val' not in st.session_state: st.session_state.d_val = 15
if 'g_val' not in st.session_state: st.session_state.g_val = 25
if 'k_val' not in st.session_state: st.session_state.k_val = 35
if 'u_val' not in st.session_state: st.session_state.u_val = 20

# --- 🔭 ÜST PANEL ---
st.title("🛰️ MacroVision v13.1: Stratejik Karar Destek Sistemi")

m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 Dolar (Spot)", f"{GUNCEL_DOLAR} TL")
m2.metric("📊 Q1 Enflasyon", f"%{GERCEKLESEN_3_AYLIK}")
m3.metric("🎯 TCMB Hedefi", f"%{TCMB_HEDEF}")
m4.metric("🏦 Mevduat Faizi", f"%{MEVCUT_FAIZ}")

st.divider()

# --- ⚙️ GİRİŞ ---
col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("⚙️ Senaryo Modelleme")
    u_name = st.text_input("Analist Adı:", "Analist_01")
    u_prof = st.selectbox("Harcama Sepeti:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
    
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

    risk_f = st.radio("⚠️ Temel Risk:", ["Doların Fırlaması", "Fiyat Artışları", "Lojistik Zamları", "Hizmet Zamları"])

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.2, 0.25, 0.40, 0.15], "Emekli": [0.10, 0.50, 0.30, 0.10], "Çalışan": [0.20, 0.30, 0.30, 0.20], "Kamu Personeli": [0.20, 0.30, 0.30, 0.20], "Esnaf": [0.35, 0.25, 0.20, 0.20]}
w = weights[u_prof]
res_9ay = (d_a * w[0] + g_a * w[1] + k_a * w[2] + u_a * w[3])
res_total = GERCEKLESEN_3_AYLIK + res_9ay
tahmini_kur_tl = GUNCEL_DOLAR * (1 + d_a/100)
alim_kaybi = (1 - (1 / (1 + res_total/100))) * 100
bin_tl_kalan = 1000 * (1 / (1 + res_total/100))

# --- 🏁 SONUÇLAR ---
with col_out:
    st.subheader("🏁 Analiz Çıktıları")
    r1, r2, r3 = st.columns(3)
    r1.metric("📈 Yıl Sonu Enflasyon", f"%{res_total:.2f}")
    r2.metric("📉 Alım Gücü Kaybı", f"%{alim_kaybi:.1f}")
    r3.metric("🎯 Hedef Sapması", f"{res_total - TCMB_HEDEF:.1f} Puan", delta_color="inverse")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.write("### 📉 1.000 TL'nin Yolculuğu")
        st.title(f"{bin_tl_kalan:.2f} TL")
        st.write("**🕰️ Zaman Makinesi:**")
        st.markdown(f"* 2020: 75 TL | 2022: 185 TL | 2024: 680 TL\n* **2026 SONU: {1000 * (1 + res_total/100):.0f} TL** 🔴")

        den = res_9ay if res_9ay > 0 else 1
        st.info(f"💡 **Katkı Analizi:** Dolar: %{(d_a*w[0]/den)*100:.1f} | Gıda: %{(g_a*w[1]/den)*100:.1f} | Kira: %{(k_a*w[2]/den)*100:.1f}")

    with c2:
        gauge = go.Figure(go.Indicator(mode = "gauge+number", value = alim_kaybi, title = {'text': "Değer Kaybı (%)"}, gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#e74c3c"}}))
        gauge.update_layout(height=230, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(gauge, use_container_width=True)

st.divider()

# --- 💾 KAYDET VE SONRADAN GÖSTER ---
if st.button("💾 ANALİZİ KAYDET VE KIYASLA", type="primary", use_container_width=True):
    save_data(u_name, u_prof, res_9ay, res_total, tahmini_kur_tl, risk_f, alim_kaybi, bin_tl_kalan)
    st.balloons()
    
    if os.path.exists(DB_FILE):
        df_hist = pd.read_csv(DB_FILE)
        avg_total = df_hist['Yıl_Sonu_Toplam'].mean()
        fark = res_total - avg_total
        
        if fark > 0:
            st.warning(f"✅ Analizin kaydedildi! Diğer katılımcıların ortalama beklentisinden (%{avg_total:.1f}) daha **karamsarsın** (Fark: {fark:.1f} puan).")
        else:
            st.success(f"✅ Analizin kaydedildi! Diğer katılımcıların ortalama beklentisinden (%{avg_total:.1f}) daha **iyimsersin** (Fark: {abs(fark):.1f} puan).")

# --- 🛡️ ADMIN ---
st.sidebar.markdown("---")
admin_key = st.sidebar.text_input("🔐 Admin", type="password")
if admin_key == "alper2026":
    if os.path.exists(DB_FILE):
        df_admin = pd.read_csv(DB_FILE)
        st.dataframe(df_admin, use_container_width=True)
