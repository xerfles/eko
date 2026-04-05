import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# --- 📁 VERİ YÖNETİMİ ---
DB_FILE = 'macrovision_v15_final.csv'

def save_data(isim, profil, beklenti_9ay, toplam, dolar, risk, alim_kaybi, erime):
    cols = ['Tarih', 'Katılımcı', 'Profil', '9_Ay_Enf', 'Yıl_Sonu_Toplam', 'Dolar_Beklentisi', 'Ana_Risk', 'Değer_Kaybı_Yüzde', 'Bin_TL_Kalan']
    data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), isim, profil, beklenti_9ay, toplam, dolar, risk, alim_kaybi, erime]], columns=cols)
    if not os.path.isfile(DB_FILE): data.to_csv(DB_FILE, index=False)
    else: data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 6 NİSAN 2026 GÜNCEL VERİLER ---
GUNCEL_DOLAR = 44.92
GERCEKLESEN_3_AYLIK = 14.40 
TCMB_HEDEF = 22.0
MEVCUT_FAIZ = 37.0 

st.set_page_config(page_title="MacroVision v15.0 Visionary", layout="wide")

# --- 🧠 OTURUM HAFIZASI ---
if 'd_val' not in st.session_state: st.session_state.d_val = 15
if 'g_val' not in st.session_state: st.session_state.g_val = 25
if 'k_val' not in st.session_state: st.session_state.k_val = 35
if 'u_val' not in st.session_state: st.session_state.u_val = 20

# --- 🔭 ÜST PANEL ---
st.title("🛰️ MacroVision v15.0: Stratejik Simülasyon & Analiz")

m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 Dolar (Spot)", f"{GUNCEL_DOLAR} TL")
m2.metric("📊 Q1 Enflasyon", f"%{GERCEKLESEN_3_AYLIK}")
m3.metric("🎯 TCMB Hedefi", f"%{TCMB_HEDEF}")
m4.metric("🏦 Mevduat Faizi", f"%{MEVCUT_FAIZ}")

st.divider()

# --- ⚙️ GİRİŞ ---
col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("⚙️ Senaryo ve Maaş Modelleme")
    u_name = st.text_input("Analist Adı:", "Analist_01")
    
    # 🟢 FİKİR 2: Maaş Simülatörü Girişi
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

    risk_f = st.radio("⚠️ Temel Risk Odağı:", ["Doların Fırlaması", "Fiyat Artışları", "Lojistik Zamları", "Hizmet Zamları"])

# --- 🧮 HESAPLAMA MOTORU ---
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

# 🟢 Maaş Kaybı Hesabı
reel_maas = u_salary * (1 / (1 + res_total/100))
maas_erimesi = u_salary - reel_maas

# --- 🏁 SONUÇLAR ---
with col_out:
    # 🟢 FİKİR 1: Dinamik Atmosfer (Enflasyona göre renk)
    bg_color = "#d4edda" if res_total < 30 else ("#fff3cd" if res_total < 55 else "#f8d7da")
    st.markdown(f'<div style="background-color: {bg_color}; padding: 15px; border-radius: 10px; border: 1px solid #ddd;">'
                f'<h3 style="margin:0;">🏁 Analiz Özeti: %{res_total:.2f} Enflasyon</h3></div>', unsafe_allow_html=True)
    
    st.write("")
    r1, r2, r3 = st.columns(3)
    r1.metric("📉 Alım Gücü Kaybı", f"%{alim_kaybi:.1f}")
    r2.metric("🍞 Reel Maaş Değeri", f"{reel_maas:.0f} TL", delta=f"-{maas_erimesi:.0f} TL")
    
    # 🟢 FİKİR 3: Dünya ile Kıyasla
    world_status = "Arjantin Seviyesi" if res_total > 80 else ("Gelişmekte Olan" if res_total > 30 else "Global Ortalama")
    r3.metric("🌍 Global Lig", world_status)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        # 🟢 FİKİR 5: Görsel Zaman Tüneli (İkonik)
        st.write("### 🕰️ Alım Gücü Dönüşümü (1.000 TL)")
        st.markdown(f"""
        * **2020:** 🧀🧀🧀🧀🧀🧀 (75 TL)
        * **2022:** 🧀🧀🧀 (185 TL)
        * **BUGÜN:** 🧀 (1.000 TL)
        * **2026 SONU:** {bin_tl_kalan:.0f} TL Değerinde 🔴
        """)
        
        # 🟢 FİKİR 4: Tüketim Stratejisti
        if res_total > MEVCUT_FAIZ:
            st.error(f"💡 **Strateji:** Enflasyon faizden yüksek. İhtiyaçlarını öteleme, önden yüklemeli tüketim mantıklı.")
        else:
            st.success(f"💡 **Strateji:** Beklentin faizin altında. TL mevduat değerini koruyabilir.")

    with c2:
        gauge = go.Figure(go.Indicator(mode = "gauge+number", value = alim_kaybi, title = {'text': "Değer Kaybı (%)"}, gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#e74c3c"}}))
        gauge.update_layout(height=230, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(gauge, use_container_width=True)

st.divider()

# --- 🕰️ ZAMAN TÜNELİ GRAFİĞİ ---
st.subheader("📊 Fiyat Merdiveni: Sepetin 2020'den 2026'ya Tırmanışı")
history_data = {"Yıl": ["2020", "2021", "2022", "2023", "2024", "2025", "BUGÜN", "2026 SONU"],
                "Sepet (TL)": [75, 95, 185, 350, 680, 890, 1000, 1000 * (1 + res_total/100)]}
st.plotly_chart(px.line(pd.DataFrame(history_data), x="Yıl", y="Sepet (TL)", text="Sepet (TL)", markers=True).update_traces(line_color="#e74c3c"), use_container_width=True)

# 🟢 FİKİR 6: Isı Haritalı Anket (Özet)
if os.path.exists(DB_FILE):
    st.sidebar.subheader("🌍 Toplumsal Beklenti Dağılımı")
    df_db = pd.read_csv(DB_FILE)
    st.sidebar.write(f"Ortalama Tahmin: %{df_db['Yıl_Sonu_Toplam'].mean():.1f}")
    st.sidebar.bar_chart(df_db.groupby('Profil')['Yıl_Sonu_Toplam'].mean())

# --- 💾 KAYIT ---
if st.button("💾 ANALİZİ KAYDET VE KIYASLA", type="primary", use_container_width=True):
    save_data(u_name, u_prof, res_9ay, res_total, GUNCEL_DOLAR*(1+d_a/100), risk_f, alim_kaybi, bin_tl_kalan)
    st.balloons()
