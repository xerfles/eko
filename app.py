import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# --- 📁 VERİ YÖNETİMİ (LiraPulse Veri Bankası) ---
DB_FILE = 'lirapulse_v15_data.csv'

def save_data(isim, profil, sehir, beklenti_9ay, toplam, dolar, risk, alim_kaybi, erime):
    user_ip = "127.0.0.1"
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        if headers:
            user_ip = headers.get("X-Forwarded-For", "127.0.0.1").split(",")[0]
    except: pass

    cols = ['Tarih', 'Katılımcı', 'Profil', 'Şehir', 'IP', 'Yıl_Sonu_Enf', 'Dolar_Beklentisi', 'Alım_Gücü_Kaybı', 'Reel_Kalan_TL']
    data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), isim, profil, sehir, user_ip, toplam, dolar, alim_kaybi, erime]], columns=cols)
    if not os.path.isfile(DB_FILE): data.to_csv(DB_FILE, index=False)
    else: data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 6 NİSAN 2026 GÜNCEL PİYASA ---
GUNCEL_DOLAR = 44.92
TCMB_HEDEF = 22.0

st.set_page_config(page_title="LiraPulse: Ekonomik Beklenti Simülatörü", layout="wide")

# --- 🧠 OTURUM HAFIZASI ---
for key, val in [('d_val', 15), ('g_val', 25), ('k_val', 35), ('u_val', 20)]:
    if key not in st.session_state: st.session_state[key] = val

# --- 🔭 MARKA PANELİ ---
st.title("🛰️ LiraPulse: Türkiye'nin İnteraktif Beklenti Endeksi")
st.caption("Veri odaklı gelecek vizyonu. Toplumsal nabzı simüle edin.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 Dolar/TL", f"{GUNCEL_DOLAR}")
m2.metric("🎯 TCMB Hedefi", f"%{TCMB_HEDEF}")
m3.metric("📊 Q1 Gerçekleşen", "%14.40")
m4.metric("🏦 Politika Faizi", "%37.0")

st.divider()

# --- (Buradan sonrası v15.2 ile aynı hesaplama ve grafik yapısıdır) ---
# ...
