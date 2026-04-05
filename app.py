import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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

st.set_page_config(page_title="MacroVision v12.3 Elite", layout="wide")

# --- 🧠 OTURUM HAFIZASI ---
if 'd_val' not in st.session_state: st.session_state.d_val = 15
if 'g_val' not in st.session_state: st.session_state.g_val = 25
if 'k_val' not in st.session_state: st.session_state.k_val = 35
if 'u_val' not in st.session_state: st.session_state.u_val = 20

# --- 🔭 ÜST PANEL ---
st.title("🛰️ MacroVision v12.3: Stratejik Karar Destek Sistemi")

with st.expander("🤔 Enflasyon Analiz Rehberi"):
    st.markdown("""
    Bu platform, 2026 sonu beklentilerinizin **reel satın alma gücü** üzerindeki etkisini ölçer. 
    Hesaplamalar, seçtiğiniz tüketici profiline göre (Örn: Öğrenci bütçesinde kira ağırlığı fazladır) dinamik olarak değişir.
    """)

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
    
    st.write("---")
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

    risk_f = st.radio("⚠️ Temel Risk Odağı:", ["Doların Fırlaması", "Fiyat Artışları", "Lojistik Zamları", "Hizmet Zamları"])

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
    st.subheader("🏁 Analitik Çıktılar")
    r1, r2, r3 = st.columns(3)
    r1.metric("📈 Toplam Enflasyon", f"%{res_total:.2f}")
    r2.metric("📉 Alım Gücü Kaybı", f"%{alim_kaybi:.1f}")
    # 🟢 Dolar/Enflasyon Makası (Yeni Metrik)
    r3.metric("⚖️ Kur/Fiyat Farkı", f"{res_total - d_a:.1f} Puan", delta="Enflasyon Baskın")

    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        st.write("### 📉 1.000 TL'nin Yolculuğu")
        st.title(f"{bin_tl_kalan:.2f} TL")
        st.caption(f"Bugünkü 1.000 TL, sene sonunda {bin_tl_kalan:.2f} TL değerine inecektir.")
        
        # 🟢 Dinamik Analist Notu (Yeni Detay)
        if res_total > 50:
            st.warning(f"🚨 **Analist Notu:** {u_name}, senaryon çok agresif. Bu seviyede bir enflasyon tasarrufları tamamen eritebilir!")
        elif res_total > TCMB_HEDEF:
            st.info(f"🧐 **Analist Notu:** Resmi hedeflerin üzerinde bir beklentiye sahipsin. Piyasa realizasyonu bu kadar yüksek olmayabilir.")
        else:
            st.success(f"🌟 **Analist Notu:** Oldukça iyimser bir tablo. Bu senaryo gerçekleşirse alım gücü korunabilir.")

    with c2:
        gauge = go.Figure(go.Indicator(mode = "gauge+number", value = alim_kaybi, title = {'text': "Paranın Değer Kaybı (%)"}, gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#e74c3c"}}))
        gauge.update_layout(height=230, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(gauge, use_container_width=True)

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=[d_a, g_a, k_a, u_a], theta=['Dolar','Gıda','Kira','Ulaşım'], fill='toself', line_color='#2ecc71'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=300)
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# --- 💾 KAYIT ---
if st.button("💾 ANALİZİ VERİ TABANINA İŞLE", type="primary"):
    save_data(u_name, u_prof, res_9ay, res_total, tahmini_kur_tl, risk_f, alim_kaybi, bin_tl_kalan)
    st.balloons()
