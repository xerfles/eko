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
    ]], columns=['Tarih', 'İsim', 'Profil', 'Dokuz_Aylık_Enf', 'Yıl_Sonu_Toplam', 'Dolar_Beklentisi', 'Temel_Risk', 'Alım_Gücü_Kaybı'])
    
    if not os.path.isfile(DB_FILE):
        data.to_csv(DB_FILE, index=False)
    else:
        data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 GÜNCEL EKONOMİK PARAMETRELER (Nisan 2026) ---
GUNCEL_DOLAR = 44.92
ILK_CEYREK_ENF = 14.40
TCMB_HEDEF = 22.0

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="MacroVision Elite 2026", layout="wide")

# --- 🔭 ÜST PANEL (Dashboard Metrikleri) ---
st.title("🔭 MacroVision Elite: 2026 Beklenti Analitiği")
st.caption("Yapay Zeka Destekli Stratejik Finansal Simülasyon Sistemi")

m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 Spot USD/TRY", f"{GUNCEL_DOLAR} TL", "Piyasa Değeri")
m2.metric("📊 Q1 Enflasyon", f"%{ILK_CEYREK_ENF}", "Gerçekleşen")
m3.metric("🎯 TCMB Hedefi", f"%{TCMB_HEDEF}", "Yıl Sonu")
m4.metric("📉 Reel Faiz Farkı", "-%12.4", "Tahmini", delta_color="inverse")

st.divider()

# --- ⚙️ GİRDİ VE ANALİZ ALANI ---
col_in, col_out = st.columns([1.2, 2])

with col_in:
    st.subheader("🛠️ Simülasyon Parametreleri")
    user_name = st.text_input("Analist Adı/Rumuz:", placeholder="Örn: Alper_Elite")
    user_prof = st.selectbox("Harcama Sepeti Profili:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
    
    st.write("---")
    st.write("**📈 Nisan-Aralık Beklentileri (%)**")
    d_a = st.slider("💵 Döviz Kuru Değişimi", 0, 100, 15)
    g_a = st.slider("🛒 Gıda & Temel Tüketim", 0, 100, 25)
    k_a = st.slider("🏠 Konut & Kira", 0, 100, 30)
    u_a = st.slider("🚗 Ulaşım & Lojistik", 0, 100, 20)
    dg_a = st.slider("🎭 Diğer Harcamalar", 0, 100, 10)
    
    risk_f = st.selectbox("📌 Öncelikli Makro Risk:", ["Döviz Şoku (Overshooting)", "Gıda Arz Güvenliği", "Barınma Maliyeti", "Hizmet Enflasyonu (Yapışkanlık)"])

# --- 🧮 HESAPLAMA MOTORU ---
weights = {"Öğrenci": [0.2, 0.25, 0.35, 0.15, 0.05], "Emekli": [0.15, 0.45, 0.15, 0.10, 0.15], "Çalışan": [0.2, 0.25, 0.25, 0.15, 0.15], "Kamu Personeli": [0.2, 0.25, 0.25, 0.15, 0.15], "Esnaf": [0.3, 0.2, 0.2, 0.2, 0.1]}
w = weights[user_prof]
res_9ay = (d_a * w[0] + g_a * w[1] + k_a * w[2] + u_a * w[3] + dg_a * w[4])
res_total = ILK_CEYREK_ENF + res_9ay
res_usd = GUNCEL_DOLAR * (1 + d_a/100)

# Alım Gücü Kaybı Modeli
alim_gucu_kaybi = (1 - (1 / (1 + res_total/100))) * 100

with col_out:
    st.subheader("🏁 Stratejik Analiz Çıktısı")
    
    # Metrik Sonuçlar
    r1, r2, r3 = st.columns(3)
    r1.metric("9 Aylık Tahmin", f"%{res_9ay:.2f}")
    r2.metric("Yıl Sonu Toplam", f"%{res_total:.2f}")
    r3.metric("Yıl Sonu USD", f"{res_usd:.2f} TL")

    # 📊 GELİŞMİŞ GÖRSELLEŞTİRME
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        # Radar Grafik
        radar_fig = go.Figure()
        radar_fig.add_trace(go.Scatterpolar(
            r=[d_a, g_a, k_a, u_a, dg_a],
            theta=['Döviz','Gıda','Kira','Ulaşım','Diğer'],
            fill='toself', line_color='#1E88E5'
        ))
        radar_fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350, margin=dict(l=40, r=40, t=20, b=20))
        st.plotly_chart(radar_fig, use_container_width=True)

    with g_col2:
        # Gauge Chart (Alım Gücü)
        gauge_fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = alim_gucu_kaybi,
            title = {'text': "Paranın Değer Kaybı (%)", 'font': {'size': 18}},
            gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#E53935"},
                     'steps' : [{'range': [0, 25], 'color': "#C8E6C9"}, {'range': [25, 60], 'color': "#FFF9C4"}],
                     'threshold' : {'line': {'color': "black", 'width': 4}, 'value': 85}}))
        gauge_fig.update_layout(height=350, margin=dict(l=40, r=40, t=40, b=20))
        st.plotly_chart(gauge_fig, use_container_width=True)

st.divider()

# --- 💾 ANALİZ KAYIT ---
c_btn, c_msg = st.columns([1, 2])
with c_btn:
    if st.button("💾 ANALİZİ VERİ SETİNE KAYDET", use_container_width=True, type="primary"):
        if user_name:
            save_data(user_name, user_prof, res_9ay, res_total, res_usd, risk_f, alim_gucu_kaybi)
            st.success("Veri İşlendi.")
        else: st.warning("İsim gerekli.")

with c_msg:
    st.info(f"💡 **Uzman Notu:** Bu senaryoda bugün 10.000 TL olan birikiminiz, yıl sonunda reel olarak {10000 * (1 - alim_gucu_kaybi/100):.0f} TL değerine gerileyecektir.")

st.divider()

# --- 🛡️ YÖNETİCİ ANALİZ DASHBOARD ---
with st.sidebar:
    st.header("🔐 Admin")
    pw = st.text_input("Master Key", type="password")

if pw == "alper2026":
    st.header("📂 Makroekonomik Veri Analitiği")
    if os.path.exists(DB_FILE):
        df_p = pd.read_csv(DB_FILE)
        t1, t2 = st.tabs(["📋 Ham Veriler", "🔍 Dağılım ve Varyans"])
        
        with t1:
            st.dataframe(df_p, use_container_width=True)
        
        with t2:
            # Violin Plot (Akademik Görsel)
            st.plotly_chart(px.violin(df_p, y="Yıl_Sonu_Toplam", x="Profil", box=True, color="Profil", title="Grup Bazlı Beklenti Yoğunluğu"), use_container_width=True)
            # Scatter Plot (Korelasyon)
            st.plotly_chart(px.scatter(df_p, x="Dolar_Beklentisi", y="Yıl_Sonu_Toplam", color="Profil", title="Kur/Enflasyon Geçişkenliği Analizi"), use_container_width=True)
