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

st.set_page_config(page_title="LiraPulse Pro: Investor Edition", layout="wide")

# --- 🎨 CSS ---
st.markdown("""
    <style>
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border-left: 5px solid #00d4ff; }
    .sefalet-box { background-color: #ff4b4b; color: white; padding: 20px; border-radius: 15px; text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 10px; }
    .advisor-box { background-color: #238636; color: white; padding: 15px; border-radius: 10px; border-left: 10px solid #ffffff; margin-top: 10px; }
    .nabiz-card { background: linear-gradient(90deg, #161b22 0%, #0d1117 100%); padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-top: 5px;}
    .win-box { color: #2ecc71; font-weight: bold; }
    .lose-box { color: #e74c3c; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 OTURUM HAFIZASI ---
for key, val in [('d_val', 15), ('g_val', 25), ('k_val', 35), ('u_val', 20)]:
    if key not in st.session_state: st.session_state[key] = val

st.title("🛰️ LiraPulse Investor Pro v17.1")
st.markdown("🔍 *Kişisel Beklenti Endeksi ve Stratejik Yatırım Rehberi*")

# --- 🌐 TOPLUMSAL NABIZ ---
if os.path.exists(DB_FILE):
    df_history = pd.read_csv(DB_FILE)
    avg_enf = df_history['Yıl_Sonu_Enf'].mean()
    avg_usd = df_history['Dolar_Beklentisi'].mean()
    st.markdown(f'<div class="nabiz-card">🌐 <b>Analist Ortalaması:</b> Enflasyon <b>%{avg_enf:.1f}</b> | Dolar <b>{avg_usd:.2f} TL</b></div>', unsafe_allow_html=True)

st.divider()

col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("🕵️ Analist Girişi")
    u_name = st.text_input("Rumuz:", "Analist_01")
    u_salary = st.number_input("Aylık Net Gelir (TL):", min_value=0, value=45000)
    u_prof = st.selectbox("Harcama Sepeti:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf", "Özel"])
    
    st.write("**🚀 Senaryolar:**")
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
res_total = GERCEKLESEN_3_AYLIK + (d_a*w[0] + g_a*w[1] + k_a*w[2] + u_a*w[3])
alim_kaybi = (1 - (1 / (1 + res_total/100))) * 100
reel_maas = u_salary * (1 / (1 + res_total/100))

# --- 🏁 ANALİZ PANELİ ---
with col_out:
    sefalet_puanı = int((res_total * 0.6) + (alim_kaybi * 0.4))
    st.markdown(f'<div class="sefalet-box">📉 SEFALET PUANIN: {sefalet_puanı}/100</div>', unsafe_allow_html=True)
    
    r1, r2, r3 = st.columns(3)
    r1.metric("📉 Alım Gücü Kaybı", f"%{alim_kaybi:.1f}")
    r2.metric("🍞 Reel Maaş", f"{reel_maas:.0f} TL")
    r3.metric("📈 Kişisel Enflasyon", f"%{res_total:.2f}")

    # --- 🏆 YATIRIM PERFORMANS TABLOSU (YENİ) ---
    st.subheader("🛡️ Enflasyon Savaşçıları (Son 5 Yıl Karşılaştırması)")
    perf_data = {
        "Yatırım Aracı": ["Altın (Gram)", "BIST 100", "Bitcoin", "Dolar/TL", "Mevduat (Faiz)"],
        "Reel Getiri": ["✅ Yüksek", "✅ Orta-Yüksek", "🚀 Volatil/Yüksek", "❌ Düşük/Negatif", "🔴 Negatif Reel Getiri"],
        "Durum": ["WINNER", "WINNER", "RISKY WIN", "LOSER", "BIG LOSER"]
    }
    st.table(pd.DataFrame(perf_data))
    st.caption("Son 5 yılda enflasyonu yenen yatırımlar 'WINNER' olarak işaretlenmiştir.")

st.divider()

# --- 🕰️ NOSTALJİ VE ADVISOR ---
c_g1, c_g2 = st.columns([2, 1])
with c_g1:
    st.subheader("🕰️ Asgari Ücretle Gram Altın (2005-2026)")
    gold_history = {"Yıl": ["2005", "2010", "2015", "2020", "2024", "BUGÜN", "2026 Tahm."],
                    "Gram Altın": [18.5, 12.4, 9.8, 7.2, 5.8, 5.1, 5.1 / (1 + res_total/150)]}
    st.plotly_chart(px.bar(pd.DataFrame(gold_history), x="Yıl", y="Gram Altın", color="Gram Altın", color_continuous_scale='RdYlGn_r').update_layout(showlegend=False), use_container_width=True)

with c_g2:
    advice = "Paranı korumak için reel varlıklara (altın, hisse) odaklanmalısın."
    if res_total > MEVCUT_FAIZ: advice = "⚠️ ALERT: Enflasyon tahminin faizden yüksek! Faizde kalırsan paran eriyecek."
    st.markdown(f'<div class="advisor-box"><b>🛡️ LiraPulse Stratejisi:</b><br>{advice}</div>', unsafe_allow_html=True)
    st.divider()
    st.write(f"📱 **iPhone 17 Pro Max:** ~{85000 * (1 + (d_a*0.7 + res_total*0.3)/100):,.0f} TL")

st.divider()

# --- 💾 BUTONLAR ---
btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    if st.button("💾 ANALİZİ KAYDET VE NABZA KATIL", use_container_width=True):
        save_data(u_name, u_prof, "Genel", res_total-14.4, res_total, GUNCEL_DOLAR*(1+d_a/100), "Genel", alim_kaybi, 1000*(1-alim_kaybi/100))
        st.balloons()

with btn_col2:
    tweet_text = f"LiraPulse Sefalet Puanım: {sefalet_puanı}/100! 🌋 Yatırım stratejim: '{advice[:35]}...'. Senin puanın kaç? Hesapla: https://huspevhztwxasrstrhne7z.streamlit.app"
    encoded_tweet = urllib.parse.quote(tweet_text)
    st.markdown(f'<a href="https://twitter.com/intent/tweet?text={encoded_tweet}" target="_blank"><button style="width:100%; height:45px; background-color:#1DA1F2; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold; font-size:16px;">🐦 PUANINI PAYLAŞ & MEYDAN OKU</button></a>', unsafe_allow_html=True)

# --- 🛡️ ADMIN ---
st.sidebar.markdown("---")
if st.sidebar.text_input("🔐 Admin", type="password") == "alper2026":
    if os.path.exists(DB_FILE): st.dataframe(pd.read_csv(DB_FILE))
