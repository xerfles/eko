import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# --- 📁 VERİ SİSTEMİ ---
DB_FILE = 'oracle_database_v9.csv'

def save_data(isim, profil, beklenti_9ay, toplam, dolar, risk, alim_gucu, tavsiye):
    data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), isim, profil, beklenti_9ay, toplam, dolar, risk, alim_gucu, tavsiye
    ]], columns=['Tarih', 'İsim', 'Profil', '9_Aylik_Enf', 'Yil_Sonu_Toplam', 'Dolar_Beklentisi', 'Temel_Risk', 'Deger_Kaybi', 'Yatirim_Tavsiyesi'])
    if not os.path.isfile(DB_FILE):
        data.to_csv(DB_FILE, index=False)
    else:
        data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 CANLI PARAMETRELER ---
GUNCEL_DOLAR = 44.92
ILK_CEYREK_ENF = 14.40
TCMB_HEDEF = 22.0
POLITIKA_FAIZI = 50.0

# --- ⚙️ SAYFA TASARIMI ---
st.set_page_config(page_title="MacroVision Oracle v9", layout="wide")

st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .metric-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_stdio=True)

# --- 🔭 DASHBOARD HEADER ---
st.title("🔮 MacroVision Oracle: v9.0 Stratejik Projeksiyon")
st.write(f"🌐 Veri Akışı Aktif | Piyasa Kuru: {GUNCEL_DOLAR} TL | {datetime.now().strftime('%H:%M')}")

top_col1, top_col2, top_col3, top_col4 = st.columns(4)
with top_col1: st.metric("💵 USD/TRY", f"{GUNCEL_DOLAR}", "Piyasa")
with top_col2: st.metric("📊 Q1 Enflasyon", f"%{ILK_CEYREK_ENF}", "Resmi")
with top_col3: st.metric("🏦 Politika Faizi", f"%{POLITIKA_FAIZI}", "Sabit")
with top_col4: st.metric("🎯 TCMB Hedefi", f"%{TCMB_HEDEF}", "Yıl Sonu")

st.divider()

# --- ⚙️ SİMÜLASYON MOTORU ---
c_input, c_viz = st.columns([1, 2])

with c_input:
    st.subheader("🛠️ Parametre Girişi")
    u_name = st.text_input("Analist Kod Adı:", "Analist_01")
    u_prof = st.selectbox("Harcama Grubu:", ["Öğrenci", "Emekli", "Çalışan", "Kamu", "Esnaf"])
    
    st.write("---")
    st.write("**📈 Gelecek Beklentileri (%)**")
    d_a = st.slider("Döviz Kuru Artışı", 0, 100, 12)
    g_a = st.slider("Gıda Enflasyonu", 0, 100, 25)
    k_a = st.slider("Kira & Barınma", 0, 100, 35)
    u_a = st.slider("Ulaşım & Akaryakıt", 0, 100, 20)
    dg_a = st.slider("Diğer Giderler", 0, 100, 15)
    
    risk_f = st.selectbox("⚠️ Kritik Sistem Riski:", ["Hiperenflasyon Döngüsü", "Döviz Likidite Şoku", "Barınma Krizi", "Üretim Maliyeti Baskısı"])

# --- 🧮 ANALİTİK HESAPLAMA ---
weights = {"Öğrenci": [0.2, 0.25, 0.35, 0.15, 0.05], "Emekli": [0.15, 0.45, 0.15, 0.10, 0.15], "Çalışan": [0.2, 0.25, 0.25, 0.15, 0.15], "Kamu": [0.2, 0.25, 0.25, 0.15, 0.15], "Esnaf": [0.3, 0.2, 0.2, 0.2, 0.1]}
w = weights[u_prof]
res_9ay = (d_a * w[0] + g_a * w[1] + k_a * w[2] + u_a * w[3] + dg_a * w[4])
res_total = ILK_CEYREK_ENF + res_9ay
res_usd = GUNCEL_DOLAR * (1 + d_a/100)
alim_kaybi = (1 - (1 / (1 + res_total/100))) * 100

# 💡 YATIRIM STRATEJİSİ ÖNERİSİ (Efsane Dokunuş)
if res_total > POLITIKA_FAIZI:
    tavsiye = "⚠️ Negatif Reel Faiz: Paranızı TL mevduatta tutmak erimesine yol açabilir. Emtia veya döviz bazlı varlıklar korunma sağlayabilir."
else:
    tavsiye = "✅ Pozitif Reel Faiz: Mevduat faizi enflasyon beklentinizin üzerinde. TL varlıklar bu senaryoda kazançlı duruyor."

with c_viz:
    st.subheader("🏁 Analitik Çıktı Paneli")
    out_1, out_2, out_3 = st.columns(3)
    out_1.metric("9 Aylık Tahmin", f"%{res_9ay:.2f}")
    out_2.metric("Yıl Sonu Enflasyon", f"%{res_total:.2f}")
    out_3.metric("Tahmini Dolar", f"{res_usd:.2f} TL")

    # RADAR CHART (Daha Şık)
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=[d_a, g_a, k_a, u_a, dg_a], theta=['Döviz','Gıda','Kira','Ulaşım','Diğer'], fill='toself', line_color='#636EFA'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400, margin=dict(l=50, r=50, t=30, b=30))
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# --- 🚀 STRATEJİ VE KAYIT ---
s_col1, s_col2 = st.columns([2, 1])
with s_col1:
    st.success(f"📌 **Stratejik Öneri:** {tavsiye}")
    st.info(f"💸 **Alım Gücü Analizi:** Bu senaryoda 1.000 TL'nizin yıl sonundaki reel değeri **{1000*(1-alim_kaybi/100):.0f} TL** olacaktır.")

with s_col2:
    if st.button("💾 ANALİZİ SİSTEME KAYDET", use_container_width=True, type="primary"):
        save_data(u_name, u_prof, res_9ay, res_total, res_usd, risk_f, alim_kaybi, tavsiye)
        st.balloons()
        st.success("Veri tabanına işlendi!")

st.divider()

# --- 🛡️ ADMIN DASHBOARD (Efsane İstatistikler) ---
with st.sidebar:
    st.write("---")
    admin_pw = st.text_input("Master Password", type="password")

if admin_pw == "alper2026":
    st.header("📊 Global Ekonomik İstihbarat")
    if os.path.exists(DB_FILE):
        df_final = pd.read_csv(DB_FILE)
        
        tab_data, tab_viz = st.tabs(["📋 Ham Veri Seti", "🔬 Derin Analiz"])
        
        with tab_data:
            st.dataframe(df_final, use_container_width=True)
            if st.button("🗑️ Veri Setini Sıfırla"):
                os.remove(DB_FILE)
                st.rerun()
                
        with tab_viz:
            st.plotly_chart(px.violin(df_final, y="Yil_Sonu_Toplam", x="Profil", box=True, points="all", title="Profil Bazlı Enflasyon Yoğunluğu"), use_container_width=True)
            st.plotly_chart(px.scatter(df_final, x="Dolar_Beklentisi", y="Yil_Sonu_Toplam", size="Deger_Kaybi", color="Profil", title="Kur/Enflasyon/Alım Gücü Korelasyonu"), use_container_width=True)
            
            # Risk Pasta Grafiği
            st.plotly_chart(px.sunburst(df_final, path=['Temel_Risk', 'Profil'], values='Yil_Sonu_Toplam', title="Risk Kaynakları ve Etkilenen Gruplar"), use_container_width=True)
