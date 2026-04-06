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

# --- 📊 GÜNCEL VERİLER (6 Nisan 2026) ---
GUNCEL_DOLAR, Q1_ENF, TCMB_FAIZ, TCMB_2026_HEDEF = 44.92, 14.40, 37.0, 22.0

st.set_page_config(page_title="LiraPulse: The Truth Keeper", layout="wide")

# --- 🎨 CSS ---
st.markdown("""
    <style>
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border-left: 5px solid #00d4ff; }
    .cert-card { background: linear-gradient(135deg, #00d4ff 0%, #0055ff 100%); color: white; padding: 25px; border-radius: 15px; text-align: center; border: 3px solid #fff; margin-bottom: 20px; }
    .receipt-box { background-color: #fff; color: #333; padding: 20px; border-radius: 5px; font-family: 'Courier New'; border: 2px dashed #333; margin-top: 20px; animation: slideIn 0.5s ease-out; }
    .ozet-panel { background-color: #1e1e26; padding: 20px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
    @keyframes slideIn { from {opacity: 0; transform: translateY(-20px);} to {opacity: 1; transform: translateY(0);} }
    </style>
    """, unsafe_allow_html=True)

if 'd_val' not in st.session_state: 
    st.session_state.update({'d_val': 15, 'g_val': 25, 'k_val': 35, 'u_val': 20})

st.title("🛰️ LiraPulse Intelligence v21.1")

# --- 📊 ÜST DASHBOARD ---
top1, top2, top3, top4 = st.columns(4)
top1.metric("💵 Güncel Dolar", f"{GUNCEL_DOLAR} TL")
top2.metric("📊 2026 Q1 Enflasyon", f"%{Q1_ENF}")
top3.metric("🏦 TCMB Faiz Oranı", f"%{TCMB_FAIZ}")
top4.metric("🎯 TCMB 2026 Hedefi", f"%{TCMB_2026_HEDEF}")

st.divider()

# --- 🎭 HIZLI SENARYOLAR ---
s_col1, s_col2, s_col3 = st.columns(3)
if s_col1.button("🌸 Pembe Rüya", use_container_width=True):
    st.session_state.d_val, st.session_state.g_val, st.session_state.k_val, st.session_state.u_val = 10, 15, 20, 12
    st.rerun()
if s_col2.button("📊 Gri Gerçek", use_container_width=True):
    st.session_state.d_val, st.session_state.g_val, st.session_state.k_val, st.session_state.u_val = 25, 35, 45, 30
    st.rerun()
if s_col3.button("🌋 Kara Delik", use_container_width=True):
    st.session_state.d_val, st.session_state.g_val, st.session_state.k_val, st.session_state.u_val = 60, 85, 100, 75
    st.rerun()

col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("🕵️ Analist Girişi")
    u_name = st.text_input("Rumuz:", "Analist_01")
    u_city = st.selectbox("Şehir:", ["İstanbul", "Ankara", "İzmir", "Kırklareli", "Bursa", "Antalya", "Diğer"])
    u_prof = st.selectbox("Harcama Sepeti:", ["Öğrenci", "Emekli", "Beyaz Yakalı", "Esnaf", "Yeni Evli 💍", "Gamer 🎮", "Araç Sahibi 🚗"])
    
    st.write("✨ **Hedef Ürünler (Bugün)**")
    p_ps5, p_iphone, p_car = st.number_input("PS5 (TL):", value=24000), st.number_input("iPhone 17 Pro (TL):", value=85000), st.number_input("Araba (TL):", value=1200000)

    d_a = st.slider("💵 Dolar Artışı (%)", 0, 150, key='d_val')
    g_a = st.slider("🛒 Gıda Artışı (%)", 0, 150, key='g_val')
    k_a = st.slider("🏠 Kira Artışı (%)", 0, 150, key='k_val')
    u_a = st.slider("🚗 Ulaşım Artışı (%)", 0, 150, key='u_val')

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.15, 0.25, 0.45, 0.15], "Emekli": [0.05, 0.55, 0.30, 0.10], "Beyaz Yakalı": [0.20, 0.30, 0.30, 0.20], "Esnaf": [0.40, 0.20, 0.20, 0.20], "Yeni Evli 💍": [0.15, 0.20, 0.50, 0.15], "Gamer 🎮": [0.40, 0.20, 0.20, 0.20], "Araç Sahibi 🚗": [0.15, 0.20, 0.25, 0.40]}
w = weights[u_prof]
res_total = Q1_ENF + (d_a*w[0] + g_a*w[1] + k_a*w[2] + u_a*w[3])
alim_kaybi, tahmini_kur = (1 - (1 / (1 + res_total/100))) * 100, GUNCEL_DOLAR * (1 + d_a/100)
f_ps5, f_iphone, f_car = p_ps5*(1+res_total/90), p_iphone*(1+(d_a*0.8+res_total*0.2)/100), p_car*(1+(d_a*0.6+res_total*0.4)/100)

with col_out:
    st.markdown(f'<div class="ozet-panel"><small>Senin Enflasyonun</small><br><b style="font-size:32px; color:#ff4b4b;">%{res_total:.1f}</b><br><small>Tahmini Kur: {tahmini_kur:.2f} TL</small></div>', unsafe_allow_html=True)
    st.write("")
    
    c_gauge, c_erime = st.columns(2)
    with c_gauge:
        st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=alim_kaybi, title={'text': "Değer Kaybı (%)"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#ff4b4b"}, 'steps': [{'range': [0, 30], 'color': "green"}, {'range': [30, 60], 'color': "orange"}, {'range': [60, 100], 'color': "red"}]})).update_layout(height=230, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}), use_container_width=True)
    with c_erime:
        st.write("### 📉 1.000 TL Yolculuğu")
        st.title(f"{1000/(1+res_total/100):.2f} TL")
        st.markdown(f'<div style="background-color: lightgrey; border-radius: 5px;"><div style="background-color: red; width: {min(res_total, 100)}%; height: 20px; border-radius: 5px;"></div></div>', unsafe_allow_html=True)

    h_col1, h_col2, h_col3 = st.columns(3)
    h_col1.metric("🎮 2026 PS5", f"{f_ps5:,.0f} TL")
    h_col2.metric("📱 2026 iPhone", f"{f_iphone:,.0f} TL")
    h_col3.metric("🚗 2026 Araba", f"{f_car:,.0f} TL")

st.divider()

# --- 🕰️ ZAMAN MAKİNESİ (RESMİ VERİLER) ---
st.subheader("🕰️ Zaman Makinesi: Asgari Ücretin Gerçek Gücü (2000-2025)")
raw_data = {
    "Yıl": ["2000", "2001", "2003", "2005", "2008", "2010", "2013", "2016", "2018", "2020", "2023", "2024", "2025"],
    "Dolar ($)": [126, 92, 150, 261, 385, 395, 420, 430, 333, 330, 430, 520, 485],
    "Altın (Gram)": [24.5, 11.2, 13.1, 18.2, 13.5, 10.5, 9.5, 10.4, 7.2, 5.1, 6.5, 6.8, 4.5]
}
df_nost = pd.DataFrame(raw_data)
g1, g2 = st.columns(2)
with g1: st.plotly_chart(px.bar(df_nost, x="Yıl", y="Altın (Gram)", text_auto='.1f', title="Maaş Kaç Gram Altın?", color="Altın (Gram)", color_continuous_scale='YlOrBr'), use_container_width=True)
with g2: st.plotly_chart(px.bar(df_nost, x="Yıl", y="Dolar ($)", text_auto='.0f', title="Maaş Kaç Dolar?", color="Dolar ($)", color_continuous_scale='Greens'), use_container_width=True)

st.divider()

# --- ⚔️ VARLIK SAVAŞLARI ---
st.subheader("⚔️ Enflasyon vs Varlık Savaşları (2021-2025)")
st.table(pd.DataFrame({"Yıl": ["2021", "2022", "2023", "2024", "2025"], "Enf.": ["%36", "%64", "%65", "%45", "%28"], "Altın": ["+72 ✅", "+40 ❌", "+78 ✅", "+61 ✅", "+35 ✅"], "BIST": ["+26 ❌", "+196 ✅", "+35 ❌", "+48 ✅", "+40 ✅"]}))

if st.button("💾 ANALİZİ KAYDET VE ADİSYONU AL", use_container_width=True):
    save_data(u_name, u_prof, u_city, res_total-Q1_ENF, res_total, tahmini_kur, "Genel", alim_kaybi, 1000/(1+res_total/100))
    st.balloons()
    food_2026 = 980 * (1 + res_total/100)
    st.markdown(f'<div class="receipt-box"><center>🧾 <b>LiraPulse Intelligence ADİSYON</b></center><hr>31.12.2026 | GELECEK FATURASI<br>--------------------------------<br>1x Akşam Yemeği (2 Kişi) : {food_2026:.0f} TL<br>--------------------------------<br><b>TOPLAM (SENİN SENARYON) : {food_2026:.0f} TL</b><br><center><i>Veri kaydedildi. Gelecek yaklaşıyor.</i></center></div>', unsafe_allow_html=True)

if st.sidebar.text_input("🔐 Admin", type="password") == "alper2026":
    if os.path.exists(DB_FILE): st.dataframe(pd.read_csv(DB_FILE))
