import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import urllib.parse
from datetime import datetime

# --- 📁 VERİ YÖNETİMİ ---
DB_FILE = 'lirapulse_v15_data.csv'

def save_data(isim, profil, sehir, beklenti_9ay, toplam, dolar, risk, alim_kaybi, erime):
    user_ip = "127.0.0.1"
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        if headers: user_ip = headers.get("X-Forwarded-For", "127.0.0.1").split(",")[0]
    except: pass
    cols = ['Tarih', 'Katılımcı', 'Profil', 'Şehir', 'IP', 'Yıl_Sonu_Enf', 'Dolar_Beklentisi', 'Alım_Gücü_Kaybı', 'Reel_Kalan_TL']
    data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), isim, profil, sehir, user_ip, toplam, dolar, alim_kaybi, erime]], columns=cols)
    if not os.path.isfile(DB_FILE): data.to_csv(DB_FILE, index=False)
    else: data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 2026 GÜNCEL PİYASA ---
GUNCEL_DOLAR, GERCEKLESEN_3_AYLIK, TCMB_HEDEF, MEVCUT_FAIZ = 44.92, 14.40, 22.0, 37.0 

st.set_page_config(page_title="LiraPulse Pro: Hayatta Kalma Simülatörü", layout="wide")

# --- 🎨 CSS (Daha Vurgulu Renkler) ---
st.markdown("""
    <style>
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
    .stSlider > div [data-baseweb="slider"] { color: #00d4ff; }
    .sefalet-box { background-color: #ff4b4b; color: white; padding: 20px; border-radius: 15px; text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.3); }
    .tokat-metin { color: #ffbd45; font-style: italic; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 OTURUM HAFIZASI ---
for key, val in [('d_val', 15), ('g_val', 25), ('k_val', 35), ('u_val', 20)]:
    if key not in st.session_state: st.session_state[key] = val

# --- 🔭 HEADER (Pazarlama Odaklı) ---
st.title("🛰️ LiraPulse Pro: Ekonomik Survivor v16.2")
st.markdown("🔍 *Resmi rakamları değil, kendi cüzdanını simüle et. Geleceği tahmin etme, hesapla.*")

top_col1, top_col2, top_col3, top_col4 = st.columns(4)
top_col1.metric("💵 Dolar/TL", f"{GUNCEL_DOLAR}")
top_col2.metric("🎯 TCMB Hedefi", f"%{TCMB_HEDEF}")
top_col3.metric("📊 Gerçekleşen (Q1)", f"%14.40")
top_col4.metric("🏦 Politika Faizi", f"%{MEVCUT_FAIZ}")

st.divider()

col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("🕵️ Analist Girişi")
    u_name = st.text_input("Rumuz (Twitter'da görünecek):", "Analist_01")
    u_salary = st.number_input("Aylık Net Gelir (TL):", min_value=0, value=45000)
    u_prof = st.selectbox("Harcama Sepeti Profili:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf", "Özel"])
    
    st.write("**🚀 Senaryo Seçimi:**")
    sc1, sc2, sc3 = st.columns(3)
    if sc1.button("🌸 İyimser"):
        st.session_state.d_val, st.session_state.g_val, st.session_state.k_val, st.session_state.u_val = 8, 12, 15, 10
        st.rerun()
    if sc2.button("📊 Realist"):
        st.session_state.d_val, st.session_state.g_val, st.session_state.k_val, st.session_state.u_val = 18, 28, 35, 22
        st.rerun()
    if sc3.button("🌋 Kriz"):
        st.session_state.d_val, st.session_state.g_val, st.session_state.k_val, st.session_state.u_val = 45, 65, 80, 55
        st.rerun()

    d_a = st.slider("💵 Dolar Artışı (%)", 0, 100, key='d_val')
    g_a = st.slider("🛒 Gıda Artışı (%)", 0, 100, key='g_val')
    k_a = st.slider("🏠 Kira Artışı (%)", 0, 100, key='k_val')
    u_a = st.slider("🚗 Ulaşım Artışı (%)", 0, 100, key='u_val')

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.2, 0.25, 0.40, 0.15], "Emekli": [0.10, 0.50, 0.30, 0.10], "Çalışan": [0.20, 0.30, 0.30, 0.20], "Kamu Personeli": [0.20, 0.30, 0.30, 0.20], "Esnaf": [0.35, 0.25, 0.20, 0.20], "Özel": [0.25, 0.25, 0.25, 0.25]}
w = weights[u_prof]
res_9ay = (d_a*w[0] + g_a*w[1] + k_a*w[2] + u_a*w[3])
res_total = GERCEKLESEN_3_AYLIK + res_9ay
alim_kaybi = (1 - (1 / (1 + res_total/100))) * 100
reel_maas = u_salary * (1 / (1 + res_total/100))

# --- 🏆 SEFALET PUANI & UNVAN ---
sefalet_puanı = int((res_total * 0.6) + (alim_kaybi * 0.4))
if res_total < 30: rank, r_emoji = "Merkez Bankası Başkanı", "🏦"
elif res_total < 55: rank, r_emoji = "Piyasa Analisti", "📊"
else: rank, r_emoji = "Ekonomik Survivor", "🌋"

# --- 🏁 ANALİZ PANELİ ---
with col_out:
    st.markdown(f'<div class="sefalet-box">📉 SEFALET PUANIN: {sefalet_puanı}/100</div>', unsafe_allow_html=True)
    
    r1, r2, r3 = st.columns(3)
    r1.metric("📉 Alım Gücü Kaybı", f"%{alim_kaybi:.1f}")
    r2.metric("🍞 Reel Maaşın", f"{reel_maas:.0f} TL")
    r3.metric("📈 Kişisel Enflasyonun", f"%{res_total:.2f}")

    st.markdown(f'<p class="tokat-metin">⚠️ Not: Senin senaryonda maaşının %{alim_kaybi:.1f}\'i buharlaşıyor. Gelecek zam görüşmesinde bu tabloyu göster!</p>', unsafe_allow_html=True)

    st.divider()
    st.subheader("💎 Hayallerin 2026 Fiyatı (Senin Tahminine Göre)")
    h1, h2 = st.columns(2)
    iphone_tahmin = 85000 * (1 + (d_a*0.7 + res_total*0.3)/100)
    araba_tahmin = 1200000 * (1 + (d_a*0.5 + res_total*0.5)/100)
    h1.metric("📱 iPhone 17 Pro Max", f"~{iphone_tahmin:,.0f} TL")
    h2.metric("🚗 Orta Segment Araba", f"~{araba_tahmin:,.0f} TL")

st.divider()

# --- 📊 NOSTALJİ VE ŞOK ---
c_g1, c_g2 = st.columns([2, 1])
with c_g1:
    st.subheader("🕰️ Zaman Makinesi: 1.000 TL'nin Hazin Sonu")
    history_data = {"Yıl": ["2020", "2021", "2022", "2023", "2024", "2025", "BUGÜN", "2026 SONU"],
                    "1000 TL Sepeti": [75, 95, 185, 350, 680, 890, 1000, 1000 * (1 + res_total/100)]}
    st.plotly_chart(px.line(pd.DataFrame(history_data), x="Yıl", y="1000 TL Sepeti", text="1000 TL Sepeti", markers=True).update_traces(line_color="#ff4b4b"), use_container_width=True)

with c_g2:
    st.subheader("🧀 Nostalji Endeksi")
    kg_bugun = 1000 / 350
    kg_2026 = kg_bugun / (1 + res_total/100)
    st.write(f"**2020:** 25.0 kg Peynir 🧀")
    st.write(f"**BUGÜN:** {kg_bugun:.1f} kg Peynir 🧀")
    st.write(f"**2026 (Tahmin):** {kg_2026:.1f} kg Peynir 🔴")
    st.markdown('<p style="font-size:12px; color:gray;">*2020 verileri ortalama market fiyatlarıdır.</p>', unsafe_allow_html=True)

st.divider()

# --- 💾 PAYLAŞIM VE KAYIT ---
btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    if st.button("💾 ANALİZİ RESMİ VERİYE EKLE", use_container_width=True):
        save_data(u_name, u_prof, "Genel", res_9ay, res_total, GUNCEL_DOLAR*(1+d_a/100), "Genel", alim_kaybi, 1000*(1-alim_kaybi/100))
        st.balloons()

with btn_col2:
    tweet_text = f"LiraPulse Sefalet Puanım: {sefalet_puanı}/100! 🌋 Unvanım: {rank}. Maaşım {reel_maas:.0f} TL'ye düşüyor. Senin puanın kaç? Hesapla: https://huspevhztwxasrstrhne7z.streamlit.app"
    encoded_tweet = urllib.parse.quote(tweet_text)
    st.markdown(f'<a href="https://twitter.com/intent/tweet?text={encoded_tweet}" target="_blank"><button style="width:100%; height:45px; background-color:#1DA1F2; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold; font-size:16px;">🐦 PUANINI PAYLAŞ & MEYDAN OKU</button></a>', unsafe_allow_html=True)

# --- 🛡️ ADMIN ---
st.sidebar.markdown("---")
if st.sidebar.text_input("🔐 Admin", type="password") == "alper2026":
    if os.path.exists(DB_FILE): st.dataframe(pd.read_csv(DB_FILE))
