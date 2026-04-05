import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# --- 📁 VERİ YÖNETİMİ ---
DB_FILE = 'macrovision_v11_elite.csv'

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

st.set_page_config(page_title="MacroVision v11 Elite", layout="wide")

# --- 🛰️ ÜST PANEL ---
st.title("🛰️ MacroVision v11: Ekonomik Beklenti & Strateji Paneli")
with st.expander("🤔 Bu Uygulama Neyi Ölçer? (Halk İçin Özet)"):
    st.markdown("""
    Enflasyon, paranızın 'satın alma gücünün' erimesidir. Bu panel, senin tahminlerine göre 
    **bugün 1.000 TL'ye alabildiğin bir pazar sepetinin yıl sonunda kaç TL olacağını** ve bu süreçte senin için en mantıklı korunma yönteminin ne olabileceğini analiz eder.
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
    st.subheader("⚙️ Senin Senaryon")
    u_name = st.text_input("Analist Takma Adı:", "Analist_001")
    u_prof = st.selectbox("Harcama Sepeti:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
    st.write("---")
    d_a = st.slider("💵 Dolar Kuru Artışı (%)", 0, 100, 15)
    g_a = st.slider("🛒 Gıda ve Market (%)", 0, 100, 25)
    k_a = st.slider("🏠 Kira ve Barınma (%)", 0, 100, 35)
    u_a = st.slider("🚗 Ulaşım ve Akaryakıt (%)", 0, 100, 20)
    risk_f = st.radio("⚠️ En Çok Korktuğunuz Risk:", ["Doların Birden Fırlaması", "Fiyatların Durdurulamadan Artması", "Lojistik ve Nakliye Zamları", "Hizmet/Dışarıda Yemek Zamları"])

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
    r1.metric("📈 Yıl Sonu Toplam Enf.", f"%{res_total:.2f}")
    r2.metric("📉 Alım Gücü Kaybı", f"%{alim_kaybi:.1f}")
    r3.metric("🎯 Beklenti Sapması", f"{res_total - TCMB_HEDEF:.1f} Puan", delta="Hedefin Üzerinde", delta_color="inverse")

    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        st.write("### 📉 1.000 TL'nin Yıl Sonu Değeri")
        st.title(f"{bin_tl_kalan:.2f} TL")
        # 🛒 SEPET KARŞILAŞTIRMASI
        st.write("**🛒 Sembolik Market Sepeti Tahmini:**")
        st.write(f"- Bugün **1.000 TL** olan sepet yıl sonunda **{1000 * (1 + res_total/100):.0f} TL** olur.")
    with c2:
        gauge = go.Figure(go.Indicator(mode = "gauge+number", value = alim_kaybi, title = {'text': "Paranın Değer Kaybı (%)"}, gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#e74c3c"}}))
        gauge.update_layout(height=230, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(gauge, use_container_width=True)

st.divider()

# --- 💡 STRATEJİK TAVSİYE PANELİ ---
st.subheader("💡 Kişiselleştirilmiş Ekonomik Strateji")
if res_total > MEVCUT_FAIZ:
    st.error(f"📍 **Dikkat {u_name}:** Tahminine göre enflasyon faizden yüksek. Paran bankada beklerse erir! Tüketimini öne çekmek veya varlıklarını korumak mantıklı olabilir.")
else:
    st.success(f"📍 **Analiz {u_name}:** Beklentin faizden düşük. Bu durumda paranı mevduatta tutmak sana 'Reel Getiri' sağlayabilir.")

if st.button("💾 ANALİZİ KAYDET", type="primary"):
    save_data(u_name, u_prof, res_9ay, res_total, tahmini_kur_tl, risk_f, alim_kaybi, bin_tl_kalan)
    st.balloons()

# --- 🛡️ ADMIN ---
st.sidebar.markdown("---")
admin_key = st.sidebar.text_input("🔐 Admin", type="password")
if admin_key == "alper2026":
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        st.dataframe(df, use_container_width=True)
        st.plotly_chart(px.scatter(df, x="Dolar_Beklentisi", y="Yıl_Sonu_Toplam", size="Değer_Kaybı_Yüzde", color="Profil", title="Kur/Enflasyon Korelasyonu"))
