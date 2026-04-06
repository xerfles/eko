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

st.set_page_config(page_title="LiraPulse Pro: Financial Intelligence", layout="wide")

# --- 🎨 CUSTOM CSS ---
st.markdown("""
    <style>
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border-left: 5px solid #00d4ff; }
    .stSlider > div [data-baseweb="slider"] { color: #00d4ff; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 OTURUM HAFIZASI ---
for key, val in [('d_val', 15), ('g_val', 25), ('k_val', 35), ('u_val', 20)]:
    if key not in st.session_state: st.session_state[key] = val

# --- 🔭 HEADER ---
st.title("🛰️ LiraPulse Pro")
st.markdown("### *Türkiye'nin Gerçek Zamanlı Beklenti Endeksi*")

top_col1, top_col2, top_col3, top_col4 = st.columns(4)
top_col1.metric("💵 Dolar/TL", f"{GUNCEL_DOLAR}")
top_col2.metric("🎯 Hedef", f"%{TCMB_HEDEF}")
top_col3.metric("📊 Q1 Gerçekleşen", f"%{GERCEKLESEN_3_AYLIK}")
top_col4.metric("🏦 Politika Faizi", f"%{MEVCUT_FAIZ}")

st.divider()

# --- ⚙️ GİRİŞ ---
col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("🕵️ Analist Girişi")
    u_name = st.text_input("Rumuz:", "Analist_01")
    u_salary = st.number_input("Aylık Maaş (TL):", min_value=17002, value=45000, step=1000)
    u_prof = st.selectbox("Harcama Sepeti:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf", "Özel"])
    
    st.write("**🚀 Hızlı Senaryolar:**")
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
bin_tl_kalan = 1000 * (1 / (1 + res_total/100))
reel_maas = u_salary * (1 / (1 + res_total/100))

# --- 🏁 ANALİZ PANELİ ---
with col_out:
    res_color = "🟢" if res_total < 30 else ("🟡" if res_total < 55 else "🔴")
    st.subheader(f"{res_color} Senaryo Analiz Raporu")
    
    r1, r2, r3 = st.columns(3)
    r1.metric("📉 Alım Gücü Kaybı", f"%{alim_kaybi:.1f}")
    r2.metric("🍞 Reel Maaş", f"{reel_maas:.0f} TL")
    r3.metric("📈 Toplam Enflasyon", f"%{res_total:.2f}")

    # 🚀 YENİ: ZAM DEDEKTÖRÜ (ŞOK ETKİSİ)
    zam_gereksinimi = res_total * 1.1 # Refah payı eklenmiş hali
    st.warning(f"🚨 **LiraPulse Uyarısı:** Alım gücünü koruman ve %10 refah payı için alman gereken minimum zam: **%{zam_gereksinimi:.1f}**")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        gauge = go.Figure(go.Indicator(mode = "gauge+number", value = alim_kaybi, gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#00d4ff"}, 'steps': [{'range': [0, 30], 'color': "green"}, {'range': [30, 60], 'color': "orange"}, {'range': [60, 100], 'color': "red"}]}))
        gauge.update_layout(height=230, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(gauge, use_container_width=True)
    with c2:
        radar = go.Figure(go.Scatterpolar(r=[d_a, g_a, k_a, u_a], theta=['Dolar','Gıda','Kira','Ulaşım'], fill='toself', line_color='#00d4ff'))
        radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=230, margin=dict(l=40, r=40, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(radar, use_container_width=True)

st.divider()

# --- 🕰️ ZAMAN TÜNELİ & PEYNİR ENDEKSİ ---
col_graph, col_stats = st.columns([2, 1])

with col_graph:
    st.subheader("📊 Fiyat Merdiveni: 2020-2026 Sepet Tırmanışı")
    history_data = {"Yıl": ["2020", "2021", "2022", "2023", "2024", "2025", "BUGÜN", "2026 SONU"],
                    "Sepet (TL)": [75, 95, 185, 350, 680, 890, 1000, 1000 * (1 + res_total/100)]}
    fig_line = px.line(pd.DataFrame(history_data), x="Yıl", y="Sepet (TL)", text="Sepet (TL)", markers=True, color_discrete_sequence=["#00d4ff"])
    st.plotly_chart(fig_line, use_container_width=True)

with col_stats:
    st.subheader("🧀 Peynir Endeksi")
    # 2020 peynir kg fiyatı ~30 TL, 2026 tahmini
    kg_2020 = 1000 / 40
    kg_bugun = 1000 / 350
    kg_2026 = kg_bugun / (1 + res_total/100)
    
    st.write(f"1.000 TL ile kaç kg Peynir?")
    st.write(f"**2020:** {kg_2020:.1f} kg 🧀")
    st.write(f"**BUGÜN:** {kg_bugun:.1f} kg 🧀")
    st.write(f"**2026 SONU:** {kg_2026:.1f} kg 🔴")
    st.caption("Fiyatlar ortalama market verilerinden simüle edilmiştir.")

st.divider()

# --- 💾 BUTONLAR ---
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if st.button("💾 ANALİZİ VERİ BANKASINA KAYDET", use_container_width=True):
        save_data(u_name, u_prof, "İstanbul", res_9ay, res_total, GUNCEL_DOLAR*(1+d_a/100), "Genel", alim_kaybi, bin_tl_kalan)
        st.balloons()
        st.success("LiraPulse veritabanına kaydedildi!")

with btn_col2:
    tweet_text = f"LiraPulse ile 2026 enflasyon beklentimi %{res_total:.2f} olarak hesapladım! 📈 Maaşım {reel_maas:.0f} TL'ye düşüyor. Sen de hesapla: https://huspevhztwxasrstrhne7z.streamlit.app"
    encoded_tweet = urllib.parse.quote(tweet_text)
    twitter_url = f"https://twitter.com/intent/tweet?text={encoded_tweet}"
    st.markdown(f'<a href="{twitter_url}" target="_blank"><button style="width:100%; height:40px; background-color:#1DA1F2; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">🐦 SONUCU TWITTER\'DA PAYLAŞ</button></a>', unsafe_allow_html=True)

# --- 🛡️ ADMIN ---
st.sidebar.markdown("---")
if st.sidebar.text_input("🔐 Admin", type="password") == "alper2026":
    if os.path.exists(DB_FILE): st.dataframe(pd.read_csv(DB_FILE))
