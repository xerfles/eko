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

# --- 📊 PİYASA VERİLERİ ---
GUNCEL_DOLAR, GERCEKLESEN_3_AYLIK, TCMB_HEDEF = 44.92, 14.40, 22.0

st.set_page_config(page_title="LiraPulse Pro: Viral Edition", layout="wide")

# --- 🎨 CSS (Sertifika ve Kartlar İçin) ---
st.markdown("""
    <style>
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border-left: 5px solid #00d4ff; }
    .cert-card { background: linear-gradient(135deg, #00d4ff 0%, #0055ff 100%); color: white; padding: 30px; border-radius: 15px; text-align: center; border: 4px solid #fff; margin: 20px 0; }
    .receipt-box { background-color: #fff; color: #333; padding: 20px; border-radius: 5px; font-family: 'Courier New'; border: 2px dashed #333; }
    .scenario-btn { margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 OTURUM YÖNETİMİ ---
if 'd_val' not in st.session_state: st.session_state.update({'d_val': 15, 'g_val': 25, 'k_val': 35, 'u_val': 20})

st.title("🛰️ LiraPulse Intelligence v20.0")

# --- 🎭 1. SEÇİM SENİN (HIZLI SENARYOLAR) ---
st.subheader("🎭 Bir Evren Seç")
s_col1, s_col2, s_col3 = st.columns(3)
if s_col1.button("🌸 Pembe Rüya (İyimser)", use_container_width=True):
    st.session_state.d_val, st.session_state.g_val, st.session_state.k_val, st.session_state.u_val = 10, 15, 20, 12
    st.rerun()
if s_col2.button("📊 Gri Gerçek (Realist)", use_container_width=True):
    st.session_state.d_val, st.session_state.g_val, st.session_state.k_val, st.session_state.u_val = 25, 35, 45, 30
    st.rerun()
if s_col3.button("🌋 Kara Delik (Kriz)", use_container_width=True):
    st.session_state.d_val, st.session_state.g_val, st.session_state.k_val, st.session_state.u_val = 60, 85, 100, 75
    st.rerun()

st.divider()

col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("🕵️ Analist Girişi")
    u_name = st.text_input("Rumuz:", "Analist_01")
    u_city = st.selectbox("Şehir:", ["İstanbul", "Ankara", "İzmir", "Kırklareli", "Bursa", "Antalya", "Diğer"])
    u_prof = st.selectbox("Profil:", ["Öğrenci", "Emekli", "Beyaz Yakalı", "Esnaf", "Yeni Evli 💍", "Gamer 🎮", "Araç Sahibi 🚗"])
    u_salary = st.number_input("Mevcut Gelir (TL):", min_value=0, value=45000)
    
    # --- 🕹️ 2. FİYATI SEN BELİRLE (HAYAL ENDEKSİ) ---
    st.write("---")
    st.write("✨ **Hayalini Hesapla**")
    u_item = st.text_input("Ürün Adı:", "PlayStation 5")
    u_item_price = st.number_input(f"{u_item} Bugün Kaç TL?", value=25000)

    d_a = st.slider("💵 Dolar Artışı (%)", 0, 150, key='d_val')
    g_a = st.slider("🛒 Gıda Artışı (%)", 0, 150, key='g_val')
    k_a = st.slider("🏠 Kira Artışı (%)", 0, 150, key='k_val')
    u_a = st.slider("🚗 Ulaşım Artışı (%)", 0, 150, key='u_val')

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.15, 0.25, 0.45, 0.15], "Emekli": [0.05, 0.55, 0.30, 0.10], "Beyaz Yakalı": [0.20, 0.30, 0.30, 0.20], "Esnaf": [0.40, 0.20, 0.20, 0.20], "Yeni Evli 💍": [0.15, 0.20, 0.50, 0.15], "Gamer 🎮": [0.40, 0.20, 0.20, 0.20], "Araç Sahibi 🚗": [0.15, 0.20, 0.25, 0.40]}
w = weights[u_prof]
res_total = GERCEKLESEN_3_AYLIK + (d_a*w[0] + g_a*w[1] + k_a*w[2] + u_a*w[3])
alim_kaybi = (1 - (1 / (1 + res_total/100))) * 100
bin_tl_kalan = 1000 * (1 / (1 + res_total/100))
item_future_price = u_item_price * (1 + res_total/80) # Ürün enflasyonu (Dolar/Gıda/Ulaşım ağırlıklı basitleştirilmiş)

# --- 🏁 ANALİZ PANELİ ---
with col_out:
    r1, r2, r3 = st.columns(3)
    r1.metric("📉 Alım Gücü Kaybı", f"%{alim_kaybi:.1f}")
    r2.metric(f"🚀 2026 {u_item}", f"{item_future_price:.0f} TL")
    r3.metric("📉 1000 TL Ne Oldu?", f"{bin_tl_kalan:.2f} TL")

    # --- 🎓 3. ANALİST SERTİFİKASI ---
    st.markdown(f"""
    <div class="cert-card">
        <h3>📜 LiraPulse Intelligence</h3>
        <p>2026 EKONOMİK ÖNGÖRÜ SERTİFİKASI</p>
        <h2 style="color: #fff; margin: 10px 0;">{u_name.upper()}</h2>
        <p>Bu analist, 2026 yılı için <b>%{res_total:.1f}</b> oranında bir "Sokak Enflasyonu" öngörmüştür.<br>
        Durum: <b>{"KAOS TEORİSYENİ" if res_total > 50 else "REALİST GÖZLEMCİ"}</b></p>
        <small>ID: LP-{datetime.now().strftime("%y%m%d")}-{u_name[:3].upper()}</small>
    </div>
    """, unsafe_allow_html=True)

    # VARLIK SAVAŞLARI TABLOSU (Kaldırılmadı!)
    st.subheader("⚔️ Enflasyon vs Varlık Savaşları")
    war_data = {"Yıl": ["2021", "2022", "2023", "2024", "2025"], "Enf.": ["%36", "%64", "%65", "%45", "%28"], "Altın": ["+72 ✅", "+40 ❌", "+78 ✅", "+61 ✅", "+35 ✅"], "BIST": ["+26 ❌", "+196 ✅", "+35 ❌", "+48 ✅", "+40 ✅"]}
    st.table(pd.DataFrame(war_data))

# --- 🏆 ŞAMPİYON ÜRÜNLER (Expander) ---
with st.expander("🚨 2020-2025: Yıllık Zam Şampiyonları"):
    st.markdown("* **2022:** 📈 Kuru Soğan (%314) | **2023:** 📈 Dana Eti (%145) | **2024:** 📈 Üniversite (%160)")

st.divider()

# --- 🕰️ ZAMAN MAKİNESİ ---
st.plotly_chart(px.bar(pd.DataFrame({"Yıl": ["2020", "2024", "2026 T."], "Maaş ($)": [380, 520, 17002 / (GUNCEL_DOLAR * (1+d_a/100))]}), x="Yıl", y="Maaş ($)", title="Maaşın Dolar Karşılığı"), use_container_width=True)

# --- 💾 BUTONLAR ---
if st.button("💾 ANALİZİ KAYDET VE VERİ TABANINA EKLE", use_container_width=True):
    save_data(u_name, u_prof, u_city, res_total-14.4, res_total, GUNCEL_DOLAR*(1+d_a/100), "Genel", alim_kaybi, bin_tl_kalan)
    st.balloons()

tweet_text = f"LiraPulse Onaylı Analist Oldum! Rumuz: {u_name}. 2026 tahminim: %{res_total:.1f} enflasyon! 2026 model {u_item} fiyatım: {item_future_price:.0f} TL! 🧾 Hesapla: https://huspevhztwxasrstrhne7z.streamlit.app"
st.markdown(f'<a href="https://twitter.com/intent/tweet?text={urllib.parse.quote(tweet_text)}" target="_blank"><button style="width:100%; height:45px; background-color:#1DA1F2; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">🐦 SERTİFİKAMI VE TAHMİNİMİ PAYLAŞ</button></a>', unsafe_allow_html=True)

# --- 🛡️ ADMIN ---
if st.sidebar.text_input("🔐 Admin", type="password") == "alper2026":
    if os.path.exists(DB_FILE): st.dataframe(pd.read_csv(DB_FILE))
