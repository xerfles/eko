import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# --- 📁 VERİ YÖNETİMİ ---
DB_FILE = 'ultimate_database_v10.csv'

def save_data(isim, profil, beklenti_9ay, toplam, dolar, risk, alim_kaybi, erime):
    # Sütun isimlerini sabitledik
    columns = ['Tarih', 'Katılımcı', 'Profil', '9_Ay_Enf', 'Yıl_Sonu_Toplam', 'Dolar_Beklentisi', 'Ana_Risk', 'Değer_Kaybı_Yüzde', 'Bin_TL_Kalan']
    data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), isim, profil, beklenti_9ay, toplam, dolar, risk, alim_kaybi, erime
    ]], columns=columns)
    
    if not os.path.isfile(DB_FILE):
        data.to_csv(DB_FILE, index=False)
    else:
        data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 GÜNCEL VERİLER (5 Nisan 2026) ---
GUNCEL_DOLAR = 44.92
ILK_CEYREK_ENF = 14.40
TCMB_HEDEF = 22.0
POLITIKA_FAIZI = 50.0

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="MacroVision Ultimate v10", layout="wide")

# --- 🔭 ÜST PANEL ---
st.title("🔭 MacroVision Ultimate: v10.1 Stratejik Öngörü Sistemi")
st.caption(f"Veri Kaynağı: Canlı Simülasyon | Güncelleme: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 USD/TRY", f"{GUNCEL_DOLAR} TL", "Canlı")
m2.metric("📊 Baz Enflasyon", f"%{ILK_CEYREK_ENF}", "Q1 Gerçekleşen")
m3.metric("🎯 Yıl Sonu Hedefi", f"%{TCMB_HEDEF}", "TCMB")
m4.metric("🏦 Gösterge Faizi", f"%{POLITIKA_FAIZI}", "Resmi")

st.divider()

# --- 🛠️ PARAMETRE VE SİMÜLASYON ---
col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("⚙️ Senaryo Girdileri")
    user_name = st.text_input("Analist Adı:", "Analist_001")
    user_prof = st.selectbox("Harcama Sepeti:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
    
    st.write("---")
    d_a = st.slider("💵 Dolar Kuru Artış Beklentisi (%)", 0, 100, 15)
    g_a = st.slider("🛒 Gıda Grubu Artışı (%)", 0, 100, 25)
    k_a = st.slider("🏠 Kira ve Konut Artışı (%)", 0, 100, 35)
    u_a = st.slider("🚗 Ulaşım/Lojistik Artışı (%)", 0, 100, 20)
    
    risk_f = st.radio("⚠️ Temel Makro Risk Odağı:", ["Döviz Geçişkenliği", "Yapışkan Enflasyon", "Hizmet Enflasyonu", "Arz Şoku"])

# --- 🧮 HESAPLAMA MOTORU ---
weights = {"Öğrenci": [0.2, 0.25, 0.40, 0.15], "Emekli": [0.10, 0.50, 0.30, 0.10], "Çalışan": [0.20, 0.30, 0.30, 0.20], "Kamu Personeli": [0.20, 0.30, 0.30, 0.20], "Esnaf": [0.35, 0.25, 0.20, 0.20]}
w = weights[user_prof]
res_9ay = (d_a * w[0] + g_a * w[1] + k_a * w[2] + u_a * w[3])
res_total = ILK_CEYREK_ENF + res_9ay
res_usd = GUNCEL_DOLAR * (1 + d_a/100)

alim_kaybi_yüzde = (1 - (1 / (1 + res_total/100))) * 100
bin_tl_kalan = 1000 * (1 / (1 + res_total/100))

with col_out:
    st.subheader("🏁 Simülasyon Analiz Paneli")
    c1, c2 = st.columns(2)
    with c1:
        st.write("### 📉 1.000 TL'nin Akıbeti")
        st.title(f"{bin_tl_kalan:.2f} TL")
        st.caption(f"Bugünkü 1.000 TL, yıl sonunda yukarıdaki değere düşecektir.")
    with c2:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = alim_kaybi_yüzde,
            title = {'text': "Paranın Değer Kaybı (%)"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#e74c3c"}}))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=[d_a, g_a, k_a, u_a], theta=['Dolar','Gıda','Kira','Ulaşım'], fill='toself', line_color='#2ecc71'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350)
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# --- 💹 DUYARLILIK ANALİZİ ---
st.subheader("🔍 Kur Duyarlılık Matrisi")
prices = [45, 48, 52, 55, 60]
matrix_data = []
for p in prices:
    temp_d_a = ((p / GUNCEL_DOLAR) - 1) * 100
    temp_9ay = (temp_d_a * w[0] + g_a * w[1] + k_a * w[2] + u_a * w[3])
    temp_total = ILK_CEYREK_ENF + temp_9ay
    matrix_data.append({"Dolar Seviyesi": f"{p} TL", "Yıl Sonu Enflasyon": f"%{temp_total:.2f}", "1.000 TL'nin Gücü": f"{1000/(1+temp_total/100):.0f} TL"})
st.table(pd.DataFrame(matrix_data))

if st.button("💾 ANALİZİ SİSTEME LOGLA", type="primary"):
    save_data(user_name, user_prof, res_9ay, res_total, res_usd, risk_f, alim_kaybi_yüzde, bin_tl_kalan)
    st.balloons()
    st.success("Veriler kaydedildi!")

# --- 🛡️ ADMIN PANEL (Görseldeki Hatayı Gideren Kısım) ---
st.sidebar.markdown("---")
admin_key = st.sidebar.text_input("🔐 Şifre", type="password")

if admin_key == "alper2026":
    st.header("🔬 Analiz Merkezi")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        
        # 🛠️ HATAYI ÇÖZEN KONTROL: Sütun isimleri tutuyor mu?
        expected_cols = ['Tarih', 'Katılımcı', 'Profil', '9_Ay_Enf', 'Yıl_Sonu_Toplam', 'Dolar_Beklentisi', 'Ana_Risk', 'Değer_Kaybı_Yüzde', 'Bin_TL_Kalan']
        
        if not all(col in df.columns for col in expected_cols):
            st.error("⚠️ Veritabanı yapısı eski sürümden kalma! Lütfen aşağıdaki butona basarak veritabanını güncelleyiniz.")
            if st.button("🔄 Veritabanını Yeni Sürüme Göre Sıfırla"):
                os.remove(DB_FILE)
                st.rerun()
        else:
            tab1, tab2 = st.tabs(["📋 Ham Veri", "📊 Derin Analiz"])
            with tab1: st.dataframe(df, use_container_width=True)
            with tab2:
                # Görseldeki hataya sebep olan grafik çizimlerini korumaya aldık
                st.plotly_chart(px.violin(df, y="Yıl_Sonu_Toplam", x="Profil", box=True, color="Profil", title="Grup Bazlı Dağılım"))
                st.plotly_chart(px.scatter(df, x="Dolar_Beklentisi", y="Yıl_Sonu_Toplam", size="Değer_Kaybı_Yüzde", color="Profil", title="Kur/Enflasyon Korelasyonu"))
    else:
        st.info("Veri yok.")
