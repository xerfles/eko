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

# --- 📊 PİYASA VERİLERİ (6 Nisan 2026) ---
GUNCEL_DOLAR, GERCEKLESEN_3_AYLIK, TCMB_HEDEF, MEVCUT_FAIZ = 44.92, 14.40, 22.0, 37.0 

st.set_page_config(page_title="LiraPulse Pro: History Champions", layout="wide")

# --- 🎨 CSS ---
st.markdown("""
    <style>
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border-left: 5px solid #00d4ff; }
    .mektup-box { background-color: #1e1e26; border-left: 5px solid #ffbd45; padding: 20px; border-radius: 10px; font-style: italic; color: #f0f0f0; margin: 15px 0; }
    .sehir-stats { background-color: #0d1117; padding: 10px; border-radius: 5px; border: 1px solid #30363d; font-size: 13px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 OTURUM ---
for key, val in [('d_val', 15), ('g_val', 25), ('k_val', 35), ('u_val', 20)]:
    if key not in st.session_state: st.session_state[key] = val

st.title("🛰️ LiraPulse Intelligence v18.3")

# --- 🌐 ŞEHİRLERİN NABZI ---
if os.path.exists(DB_FILE):
    df_h = pd.read_csv(DB_FILE)
    top_cities = df_h.groupby('Şehir')['Yıl_Sonu_Enf'].mean().sort_values(ascending=False).head(3)
    st.markdown(f'<div class="sehir-stats">🔥 <b>En Karamsar Şehirler:</b> ' + 
                " | ".join([f"{c}: %{v:.1f}" for c, v in top_cities.items()]) + '</div>', unsafe_allow_html=True)

st.divider()

col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("🕵️ Analist Girişi")
    u_name = st.text_input("Rumuz:", "Analist_01")
    u_city = st.selectbox("Şehir:", ["İstanbul", "Ankara", "İzmir", "Kırklareli", "Bursa", "Antalya", "Diğer"])
    u_salary = st.number_input("Gelir (TL):", min_value=0, value=45000)
    u_prof = st.selectbox("Profil:", ["Öğrenci", "Emekli", "Beyaz Yakalı", "Esnaf", "Yeni Evli 💍", "Gamer 🎮", "Araç Sahibi 🚗"])
    
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
weights = {"Öğrenci": [0.15, 0.25, 0.45, 0.15], "Emekli": [0.05, 0.55, 0.30, 0.10], "Beyaz Yakalı": [0.20, 0.30, 0.30, 0.20], "Esnaf": [0.40, 0.20, 0.20, 0.20], "Yeni Evli 💍": [0.15, 0.20, 0.50, 0.15], "Gamer 🎮": [0.40, 0.20, 0.20, 0.20], "Araç Sahibi 🚗": [0.15, 0.20, 0.25, 0.40]}
w = weights[u_prof]
res_total = GERCEKLESEN_3_AYLIK + (d_a*w[0] + g_a*w[1] + k_a*w[2] + u_a*w[3])
alim_kaybi = (1 - (1 / (1 + res_total/100))) * 100
reel_maas = u_salary * (1 / (1 + res_total/100))
tahmini_dolar = GUNCEL_DOLAR * (1 + d_a/100)
bin_tl_kalan = 1000 * (1 / (1 + res_total/100))

# --- 🏁 ANALİZ PANELİ ---
with col_out:
    r1, r2, r3 = st.columns(3)
    r1.metric("📉 Alım Gücü Kaybı", f"%{alim_kaybi:.1f}")
    r2.metric("🍞 Reel Maaş", f"{reel_maas:.0f} TL")
    r3.metric("📉 Tahmini Kur", f"{tahmini_dolar:.2f} TL")

    st.divider()
    
    c_gauge, c_erime = st.columns(2)
    with c_gauge:
        gauge = go.Figure(go.Indicator(mode = "gauge+number", value = alim_kaybi, title = {'text': "Paranın Değer Kaybı (%)"}, gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#ff4b4b"}, 'steps': [{'range': [0, 30], 'color': "green"}, {'range': [30, 60], 'color': "orange"}, {'range': [60, 100], 'color': "red"}]}))
        gauge.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(gauge, use_container_width=True)

    with c_erime:
        st.write("### 📉 1.000 TL'nin Akıbeti")
        st.title(f"{bin_tl_kalan:.2f} TL")
        bar_color = "green" if res_total < 30 else ("orange" if res_total < 55 else "red")
        st.markdown(f'<div style="background-color: lightgrey; border-radius: 5px;"><div style="background-color: {bar_color}; width: {min(res_total, 100)}%; height: 25px; border-radius: 5px;"></div></div>', unsafe_allow_html=True)
        st.caption(f"Yıl sonunda 1.000 TL'nin alım gücü karşılığı.")

    # --- ⚔️ VARLIK SAVAŞI VE YENİ: TARİHSEL ŞAMPİYONLAR ---
    st.subheader("⚔️ Enflasyon Savaşları & Şampiyonlar")
    war_data = {
        "Yıl": ["2021", "2022", "2023", "2024", "2025"],
        "TÜİK Enf.": ["%36", "%64", "%65", "%45", "%28"],
        "Altın (%)": ["+72 ✅", "+40 ❌", "+78 ✅", "+61 ✅", "+35 ✅"],
        "BIST 100": ["+26 ❌", "+196 ✅", "+35 ❌", "+48 ✅", "+40 ✅"],
        "Konut (%)": ["+60 ✅", "+189 ✅", "+84 ✅", "+30 ❌", "+25 ❌"]
    }
    st.table(pd.DataFrame(war_data))

    # 🏆 YENİ: YILLIK EN ÇOK ARTAN/DÜŞEN LİSTESİ
    with st.expander("🚨 2020-2025: Yılın En Çok Artan ve Düşenleri"):
        st.markdown("""
        * **2020:** 📈 **En Çok:** Elektronik & Altın | 📉 **En Az:** Ulaşım (Pandemi)
        * **2021:** 📈 **En Çok:** Dolar & İthal Ürünler | 📉 **En Az:** Haberleşme
        * **2022:** 📈 **En Çok:** Konut & Gıda | 📉 **En Az:** Giyim
        * **2023:** 📈 **En Çok:** Lokanta & Otel | 📉 **En Az:** Konut (Yavaşlama)
        * **2024:** 📈 **En Çok:** Eğitim & Sağlık | 📉 **En Az:** Ulaştırma
        * **2025:** 📈 **En Çok:** Hizmet Sektörü | 📉 **En Az:** Dayanıklı Tüketim Malları
        """)

    st.markdown(f"""<div class="mektup-box">📬 <b>LiraPulse Intelligence:</b> Bugün 1.000 TL'ye aldığın sepet, 2026 sonunda <b>{(1000*(1+res_total/100)):.0f} TL</b> olacak.</div>""", unsafe_allow_html=True)

st.divider()

# --- 🕰️ ZAMAN MAKİNESİ ---
g1, g2 = st.columns(2)
nost_data = {"Yıl": ["2010", "2015", "2020", "2024", "BUGÜN", "2026 Tahm."], "Gram Altın": [12.4, 9.8, 7.2, 5.8, 5.1, 5.1 / (1 + res_total/150)], "Dolar ($)": [385, 410, 380, 520, 378, 17002 / tahmini_dolar]}
df_n = pd.DataFrame(nost_data)
with g1: st.plotly_chart(px.bar(df_n, x="Yıl", y="Gram Altın", text_auto='.1f', title="Maaş Kaç Gram Altın?").update_layout(height=300), use_container_width=True)
with g2: st.plotly_chart(px.bar(df_n, x="Yıl", y="Dolar ($)", text_auto='.0f', title="Maaş Kaç Dolar?").update_layout(height=300), use_container_width=True)

st.divider()

# --- 💾 BUTONLAR ---
btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    if st.button("💾 ANALİZİ KAYDET VE NABZA KATIL", use_container_width=True):
        save_data(u_name, u_prof, u_city, res_total-14.4, res_total, tahmini_dolar, "Genel", alim_kaybi, bin_tl_kalan)
        st.balloons()
with btn_col2:
    tweet_text = f"LiraPulse Intelligence: 2026'da 1000 TL'm sadece {bin_tl_kalan:.0f} TL kalıyor! 🌋 Senin alım gücün ne kadar eridi? Hesapla: https://huspevhztwxasrstrhne7z.streamlit.app"
    encoded_tweet = urllib.parse.quote(tweet_text)
    st.markdown(f'<a href="https://twitter.com/intent/tweet?text={encoded_tweet}" target="_blank"><button style="width:100%; height:45px; background-color:#1DA1F2; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">🐦 SONUCU PAYLAŞ</button></a>', unsafe_allow_html=True)

# --- 🛡️ ADMIN ---
st.sidebar.markdown("---")
if st.sidebar.text_input("🔐 Admin", type="password") == "alper2026":
    if os.path.exists(DB_FILE): st.dataframe(pd.read_csv(DB_FILE))
