import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# --- 📁 VERİ TABANI YÖNETİMİ ---
DB_FILE = 'tubitak_2209_data.csv'

def save_data(isim, profil, beklenti_9ay, toplam, dolar, risk, alim_kaybi, durum):
    data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), isim, profil, beklenti_9ay, toplam, dolar, risk, alim_kaybi, durum
    ]], columns=['Tarih', 'Katılımcı', 'Profil', '9_Aylık_Tahmin', 'Yıl_Sonu_Toplam', 'Dolar_Beklentisi', 'Risk_Faktörü', 'Alım_Gücü_Kaybı', 'Piyasa_Analizi'])
    if not os.path.isfile(DB_FILE):
        data.to_csv(DB_FILE, index=False)
    else:
        data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 GÜNCEL MAKRO PARAMETRELER ---
GUNCEL_DOLAR = 44.92
ILK_CEYREK_ENF = 14.40
TCMB_HEDEF = 22.0
FAIZ_ORANI = 50.0

# --- ⚙️ SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="MacroVision 2209-A Project", layout="wide")

# --- 🛰️ DASHBOARD ÜST PANEL ---
st.title("🛰️ MacroVision 2209-A: Beklenti Ölçüm ve Analiz Sistemi")
st.markdown(f"**Proje Durumu:** Saha Veri Toplama Aşaması | **Canlı Kur:** {GUNCEL_DOLAR} TL")

m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 Piyasa Kuru", f"{GUNCEL_DOLAR} TL")
m2.metric("📊 Baz Enflasyon (Q1)", f"%{ILK_CEYREK_ENF}")
m3.metric("🎯 Resmi Hedef", f"%{TCMB_HEDEF}")
m4.metric("🏦 Gösterge Faizi", f"%{FAIZ_ORANI}")

st.divider()

# --- 🛠️ VERİ GİRİŞİ VE MODELLEME ---
c_left, c_right = st.columns([1.2, 2])

with c_left:
    st.subheader("📋 Veri Toplama Formu")
    u_name = st.text_input("Katılımcı Tanımlayıcı (İsim/Nick):", "Katılımcı_1")
    u_prof = st.selectbox("Tüketim Sepeti Profili (Ağırlıklandırma):", ["Öğrenci", "Emekli", "Çalışan", "Kamu", "Esnaf"])
    
    st.write("---")
    st.write("**📈 Nisan-Aralık Projeksiyonu (%)**")
    d_a = st.slider("Dolar Kuru Artışı (%)", 0, 100, 15)
    g_a = st.slider("Gıda Enflasyonu (%)", 0, 100, 25)
    k_a = st.slider("Barınma/Kira Artışı (%)", 0, 100, 30)
    u_a = st.slider("Ulaşım Maliyeti (%)", 0, 100, 20)
    dg_a = st.slider("Diğer Harcamalar (%)", 0, 100, 10)
    
    risk = st.selectbox("⚠️ Tespit Edilen Makro Risk:", ["Döviz Şoku", "Gıda Enflasyonu", "Barınma Krizi", "Maliyet Enflasyonu"])

# --- 🧮 EKONOMETRİK HESAPLAMA ---
# TÜBİTAK Formuna yazabileceğin ağırlıklandırma mantığı
weights = {"Öğrenci": [0.2, 0.25, 0.35, 0.15, 0.05], "Emekli": [0.15, 0.45, 0.15, 0.10, 0.15], "Çalışan": [0.2, 0.25, 0.25, 0.15, 0.15], "Kamu": [0.2, 0.25, 0.25, 0.15, 0.15], "Esnaf": [0.3, 0.2, 0.2, 0.2, 0.1]}
w = weights[u_prof]
res_9ay = (d_a * w[0] + g_a * w[1] + k_a * w[2] + u_a * w[3] + dg_a * w[4])
res_total = ILK_CEYREK_ENF + res_9ay
res_usd = GUNCEL_DOLAR * (1 + d_a/100)
alim_kaybi = (1 - (1 / (1 + res_total/100))) * 100

# Analiz Durumu
if res_total > FAIZ_ORANI:
    durum = "⚠️ Negatif Reel Getiri Senaryosu"
else:
    durum = "✅ Pozitif Reel Getiri Senaryosu"

with c_right:
    st.subheader("📊 Senaryo Analiz Çıktıları")
    r1, r2, r3 = st.columns(3)
    r1.metric("Dokuz Aylık Beklenti", f"%{res_9ay:.2f}")
    r2.metric("Yıl Sonu Projeksiyonu", f"%{res_total:.2f}")
    r3.metric("Tahmini Dolar Kuru", f"{res_usd:.2f} TL")

    # 🟢 RADAR ANALİZİ
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=[d_a, g_a, k_a, u_a, dg_a], theta=['Döviz','Gıda','Kira','Ulaşım','Diğer'], fill='toself', name='Tahmin'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400, margin=dict(l=50, r=50, t=30, b=30))
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# --- 🚀 KARAR DESTEK VE KAYIT ---
s_col1, s_col2 = st.columns([2, 1])
with s_col1:
    st.warning(f"💡 **Analitik Çıkarım:** {durum} | Paran yıl sonunda %{alim_kaybi:.1f} oranında alım gücü kaybedecek.")
with s_col2:
    if st.button("💾 VERİYİ TÜBİTAK VERİ SETİNE KAYDET", use_container_width=True, type="primary"):
        save_data(u_name, u_prof, res_9ay, res_total, res_usd, risk, alim_kaybi, durum)
        st.balloons()
        st.success("Veri Başarıyla Loglandı!")

st.divider()

# --- 🛡️ YÖNETİCİ PANELİ (Araştırmacı Ekranı) ---
with st.sidebar:
    st.write("### 🔐 Araştırmacı Erişimi")
    pw = st.text_input("Proje Şifresi", type="password")

if pw == "alper2026":
    st.header("🔬 Saha Veri Analiz Merkezi")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        t1, t2 = st.tabs(["📋 Ham Saha Verisi", "📊 İleri İstatistik"])
        with t1:
            st.dataframe(df, use_container_width=True)
        with t2:
            st.plotly_chart(px.violin(df, y="Yıl_Sonu_Toplam", x="Profil", box=True, points="all", title="Grup Bazlı Enflasyon Beklenti Dağılımı"), use_container_width=True)
            st.plotly_chart(px.sunburst(df, path=['Risk_Faktörü', 'Profil'], values='Yıl_Sonu_Toplam', title="Risk Kaynakları Analizi"), use_container_width=True)
