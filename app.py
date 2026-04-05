import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# --- 📁 VERİ YÖNETİMİ ---
DB_FILE = 'elite_pro_database.csv'

def save_data(isim, profil, beklenti_9ay, toplam, dolar, risk, alim_gucu):
    data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), 
        isim, profil, beklenti_9ay, toplam, dolar, risk, alim_gucu
    ]], columns=['Tarih', 'İsim', 'Profil', 'Dokuz_Aylık_Enf', 'Yıl_Sonu_Toplam', 'Dolar_Beklentisi', 'Temel_Risk', 'Alim_Gucu_Kaybi'])
    
    if not os.path.isfile(DB_FILE):
        data.to_csv(DB_FILE, index=False)
    else:
        data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 SABİT VERİLER (5 Nisan 2026) ---
GUNCEL_DOLAR = 44.92
ILK_CEYREK_ENF = 14.40
TCMB_HEDEF = 22.0

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="MacroVision Elite 2026", layout="wide", initial_sidebar_state="expanded")

# --- ✨ ÖZEL CSS (Daha Modern Görünüm) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    .stSlider { padding-top: 20px; }
    </style>
    """, unsafe_allow_stdio=True)

# --- 🔭 ÜST PANEL ---
st.title("🔭 MacroVision Elite: 2026 Beklenti Analitiği")
st.caption("Yapay Zeka Destekli Ekonomik Simülasyon Sistemi")

m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 Spot Dolar Kuru", f"{GUNCEL_DOLAR} TL", "Canlı")
m2.metric("📊 Q1 Enflasyon", f"%{ILK_CEYREK_ENF}", "Resmi")
m3.metric("🎯 TCMB Hedefi", f"%{TCMB_HEDEF}", "Yıl Sonu")
m4.metric("📉 Reel Faiz (Tahmini)", "-%12.4", "Negatif", delta_color="inverse")

st.divider()

# --- ⚙️ GİRİŞ VE SİMÜLASYON ---
col_in, col_out = st.columns([1.2, 2])

with col_in:
    st.subheader("🛠️ Parametre Yönetimi")
    with st.container():
        user_name = st.text_input("Analist Takma Adı:", placeholder="Örn: Alper_Econ")
        user_prof = st.selectbox("Harcama Sepeti Profili:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
        
        st.write("---")
        st.write("**📈 Nisan-Aralık Beklentileri (%)**")
        d_a = st.slider("💵 Döviz Kuru Artışı", 0, 100, 15)
        g_a = st.slider("🛒 Gıda & Market", 0, 100, 25)
        k_a = st.slider("🏠 Konut & Kira", 0, 100, 30)
        u_a = st.slider("🚗 Ulaşım & Yakıt", 0, 100, 20)
        dg_a = st.slider("🎭 Diğer Giderler", 0, 100, 10)
        
        risk_f = st.selectbox("📌 Öncelikli Risk Faktörü:", ["Döviz Şoku (Overshooting)", "Gıda Arz Güvenliği", "Barınma Maliyeti", "Hizmet Enflasyonu (Yapışkanlık)"])

# --- 🧮 HESAPLAMA VE ANALİZ MOTORU ---
weights = {"Öğrenci": [0.2, 0.25, 0.35, 0.15, 0.05], "Emekli": [0.15, 0.45, 0.15, 0.10, 0.15], "Çalışan": [0.2, 0.25, 0.25, 0.15, 0.15], "Kamu Personeli": [0.2, 0.25, 0.25, 0.15, 0.15], "Esnaf": [0.3, 0.2, 0.2, 0.2, 0.1]}
w = weights[user_prof]
res_9ay = (d_a * w[0] + g_a * w[1] + k_a * w[2] + u_a * w[3] + dg_a * w[4])
res_total = ILK_CEYREK_ENF + res_9ay
res_usd = GUNCEL_DOLAR * (1 + d_a/100)

# Alım Gücü Kaybı Hesaplama (Matematiksel Model)
alim_gucu_kaybi = (1 - (1 / (1 + res_total/100))) * 100

with col_out:
    st.subheader("🏁 Simülasyon Çıktısı")
    
    # Üst Sonuç Kartları
    r1, r2, r3 = st.columns(3)
    r1.metric("9 Aylık Enf.", f"%{res_9ay:.2f}")
    r2.metric("Yıl Sonu Toplam", f"%{res_total:.2f}")
    r3.metric("Hedef Dolar", f"{res_usd:.2f} TL")

    # 📊 RADAR VE ALIM GÜCÜ GRAFİKLERİ (Yan Yana)
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        # Radar Chart
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[d_a, g_a, k_a, u_a, dg_a],
            theta=['Döviz','Gıda','Kira','Ulaşım','Diğer'],
            fill='toself', line_color='#1E88E5', name='Beklenti'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350, margin=dict(l=40, r=40, t=20, b=20))
        st.plotly_chart(fig_radar, use_container_width=True)

    with g_col2:
        # Alım Gücü Kaybı Göstergesi (Gauge Chart)
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = alim_gucu_kaybi,
            title = {'text': "Paranın Değer Kaybı (%)"},
            gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#E53935"},
                     'steps' : [{'range': [0, 20], 'color': "#C8E6C9"}, {'range': [20, 50], 'color': "#FFF9C4"}],
                     'threshold' : {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 80}}))
        fig_gauge.update_layout(height=350, margin=dict(l=40, r=40, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

st.divider()

# --- 💾 KAYIT VE ÖZET ANALİZ ---
c_msg, c_btn = st.columns([2, 1])
with c_msg:
    if res_total > 50:
        st.error(f"⚠️ **Kritik Uyarı:** %{res_total:.2f} enflasyon senaryosunda, bugün 1.000 TL olan paranız yıl sonunda sadece {1000 * (1 - alim_gucu_kaybi/100):.0f} TL alım gücüne sahip olacak.")
    else:
        st.info(f"ℹ️ **Analiz Notu:** Bu senaryo, resmi hedeflere kıyasla daha { 'karamsar' if res_total > TCMB_HEDEF else 'iyimser' } bir tablo çiziyor.")

with c_btn:
    if st.button("💾 ANALİZİ VERİ SETİNE KAYDET", use_container_width=True, type="primary"):
        if user_name:
            save_data(user_name, user_prof, res_9ay, res_total, res_usd, risk_f, alim_gucu_kaybi)
            st.success("Veriler Elite Veritabanına İşlendi!")
        else: st.warning("İsim alanı zorunludur.")

st.divider()

# --- 🛡️ YÖNETİCİ PANELİ (ADVANCED) ---
with st.sidebar:
    st.write("### 🔐 Yönetici Girişi")
    pw = st.text_input("Master Password", type="password")

if pw == "alper2026":
    st.header("📂 Makroekonomik Veri Ambarı")
    if os.path.exists(DB_FILE):
        df_p = pd.read_csv(DB_FILE)
        t1, t2 = st.tabs(["📋 Ham Veriler", "🔍 Korelasyon ve Dağılım"])
        
        with t1:
            st.dataframe(df_p, use_container_width=True)
            # Toplu silme butonu ekledik
            if st.button("🗑️ Tüm Veritabanını Sıfırla (Dikkat!)"):
                os.remove(DB_FILE)
                st.rerun()
        
        with t2:
            st.plotly_chart(px.scatter(df_p, x="Dolar_Beklentisi", y="Yıl_Sonu_Toplam", color="Profil", title="Dolar/Enflasyon Korelasyon Analizi"), use_container_width=True)
            st.plotly_chart(px.violin(df_p, y="Yıl_Sonu_Toplam", x="Profil", box=True, title="Grup Bazlı Beklenti Dağılımı (Violin Plot)"), use_container_width=True)
