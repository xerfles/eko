import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# --- 📁 VERİ YÖNETİMİ ---
DB_FILE = 'pro_database.csv'

def save_data(isim, profil, beklenti_9ay, toplam, dolar, risk):
    data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), isim, profil, beklenti_9ay, toplam, dolar, risk]], 
                        columns=['Tarih', 'İsim', 'Profil', 'Dokuz_Aylık_Enf', 'Yıl_Sonu_Toplam', 'Dolar_Beklentisi', 'Temel_Risk'])
    if not os.path.isfile(DB_FILE):
        data.to_csv(DB_FILE, index=False)
    else:
        data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 SABİT VERİLER ---
GUNCEL_DOLAR = 44.92
ILK_CEYREK_ENF = 14.40
TCMB_HEDEF = 22.0

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="MacroVision PRO 2026", layout="wide")

st.title("🔭 MacroVision PRO: Gelişmiş Enflasyon Analitiği")
st.markdown("---")

# Üst Bilgi Paneli
m1, m2, m3 = st.columns(3)
m1.metric("💵 Güncel Kur", f"{GUNCEL_DOLAR} TL")
m2.metric("📊 Q1 Enflasyon", f"%{ILK_CEYREK_ENF}")
m3.metric("🎯 TCMB Hedefi", f"%{TCMB_HEDEF}")

st.divider()

# --- ⚙️ GİRİŞ VE SİMÜLASYON ---
col_in, col_out = st.columns([1, 1.5])

with col_in:
    st.subheader("🛠️ Senaryo Parametreleri")
    name = st.text_input("Analist İsmi:", placeholder="Adınız")
    prof = st.selectbox("Harcama Grubu:", ["Öğrenci", "Emekli", "Çalışan", "Kamu", "Esnaf"])
    
    st.write("**Beklenen Artış Oranları (%)**")
    d_a = st.slider("Dolar Kuru", 0, 100, 10)
    g_a = st.slider("Gıda ve Market", 0, 100, 20)
    k_a = st.slider("Kira ve Konut", 0, 100, 25)
    u_a = st.slider("Ulaşım", 0, 100, 15)
    dg_a = st.slider("Diğer", 0, 100, 5)
    
    risk_factor = st.selectbox("En Büyük Risk:", ["Döviz Şoku", "Gıda Krizi", "Barınma Sorunu", "Hizmet Enflasyonu"])

# Hesaplama
weights = {"Öğrenci": [0.2, 0.25, 0.35, 0.15, 0.05], "Emekli": [0.15, 0.45, 0.15, 0.10, 0.15], "Çalışan": [0.2, 0.25, 0.25, 0.15, 0.15], "Kamu": [0.2, 0.25, 0.25, 0.15, 0.15], "Esnaf": [0.3, 0.2, 0.2, 0.2, 0.1]}
w = weights[prof]
res_9ay = (d_a * w[0] + g_a * w[1] + k_a * w[2] + u_a * w[3] + dg_a * w[4])
res_total = ILK_CEYREK_ENF + res_9ay
res_usd = GUNCEL_DOLAR * (1 + d_a/100)

with col_out:
    st.subheader("🏁 Projeksiyon Çıktısı")
    r1, r2, r3 = st.columns(3)
    r1.metric("9 Aylık Tahmin", f"%{res_9ay:.2f}")
    r2.metric("Yıl Sonu Toplam", f"%{res_total:.2f}")
    r3.metric("Tahmini Dolar", f"{res_usd:.2f} TL")

    # RADAR GRAFİĞİ (Plotly - Büyüleyici Görsel)
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[d_a, g_a, k_a, u_a, dg_a], theta=['Dolar','Gıda','Kira','Ulaşım','Diğer'], fill='toself', line_color='#00d1b2'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

if st.button("💾 ANALİZİ VERİ SETİNE KAYDET", use_container_width=True, type="primary"):
    if name:
        save_data(name, prof, res_9ay, res_total, res_usd, risk_factor)
        st.success("Analiz kaydedildi!")
    else: st.error("İsim giriniz.")

st.divider()

# --- 🛡️ YÖNETİCİ ANALİZ DASHBOARD ---
with st.sidebar:
    st.title("🔐 Admin")
    pw = st.text_input("Şifre", type="password")

if pw == "alper2026":
    st.header("📂 Kolektif Veri Analizi")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        t1, t2 = st.tabs(["📋 Ham Veriler", "📊 İleri Analiz"])
        with t1:
            st.dataframe(df, use_container_width=True)
            row = st.number_input("Silinecek Satır:", 0, len(df)-1 if len(df)>0 else 0)
            if st.button("Sil"):
                df.drop(df.index[row]).to_csv(DB_FILE, index=False)
                st.rerun()
        with t2:
            c1, c2 = st.columns(2)
            c1.plotly_chart(px.pie(df, names='Profil', title='Katılımcı Dağılımı'), use_container_width=True)
            c2.plotly_chart(px.pie(df, names='Temel_Risk', title='Risk Beklentileri'), use_container_width=True)
            st.plotly_chart(px.box(df, x="Profil", y="Yıl_Sonu_Toplam", color="Profil", title="Grup Bazlı Beklenti Dağılımı (Box Plot)"), use_container_width=True)
