import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# --- 📁 VERİ YÖNETİMİ ---
DB_FILE = 'lirapulse_v15_data.csv'
COL_LIST = ['Tarih', 'Katilimci', 'Cinsiyet', 'Maas', 'Profil', 'Sehir', 'IP', 'Nisan_Aralik_Tahmin', 'Yil_Sonu_Toplam', 'Dolar_Beklentisi', 'Alim_Gucu_Kaybi', 'Reel_Kalan_TL']

def save_data(isim, cinsiyet, maas, profil, sehir, beklenti_9ay, toplam, dolar, alim_kaybi, erime):
    user_ip = "127.0.0.1"
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        if headers: user_ip = headers.get("X-Forwarded-For", "127.0.0.1").split(",")[0]
    except: pass
    data = pd.DataFrame([[datetime.now().strftime("%d.%m.%Y %H:%M"), isim, cinsiyet, maas, profil, sehir, user_ip, beklenti_9ay, toplam, dolar, alim_kaybi, erime]], columns=COL_LIST)
    if not os.path.isfile(DB_FILE):
        data.to_csv(DB_FILE, index=False, encoding='utf-8')
    else:
        data.to_csv(DB_FILE, mode='a', index=False, header=False, encoding='utf-8')

# --- 📊 PİYASA VERİLERİ (6 Nisan 2026) ---
GUNCEL_DOLAR, Q1_ENF, TCMB_FAIZ, TCMB_2026_HEDEF = 44.92, 14.40, 37.0, 22.0
P_PS5_GUNCEL, P_IPHONE_GUNCEL, P_CAR_GUNCEL = 42999, 77999, 1795000

st.set_page_config(page_title="LiraPulse: Gelecek Beklentisi", layout="wide")

# --- 🎨 CSS (RESPONSIVE & FIXED) ---
st.markdown("""
    <style>
    .main { padding: 10px !important; }
    [data-testid="stMetric"] {
        background-color: #161b22; 
        padding: 15px !important; 
        border-radius: 15px; 
        border-left: 5px solid #00d4ff;
    }
    .ozet-panel { 
        background: linear-gradient(145deg, #1e1e26, #252532); 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #30363d; 
        text-align: center; 
        margin-bottom: 20px;
    }
    .bugun-etiket { 
        color: #ffbd45; 
        font-size: clamp(12px, 2vw, 14px); 
        text-align: center; 
        margin-top: -5px; 
        font-weight: bold; 
    }
    .inf-box { 
        background-color: #161b22; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #ff4b4b; 
        margin-top: 10px; 
        margin-bottom: 20px; 
    }
    .receipt-box { 
        background-color: #fff; 
        color: #333; 
        padding: 20px; 
        border-radius: 5px; 
        font-family: 'Courier New', monospace; 
        border: 2px dashed #333; 
        margin-top: 20px;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
    }
    @media (max-width: 768px) {
        .ozet-panel b { font-size: 24px !important; }
        h1 { font-size: 28px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

if 'd_val' not in st.session_state: st.session_state.update({'d_val': 35, 'g_val': 55, 'k_val': 65, 'u_val': 45})

st.title("🛰️ LiraPulse: Enflasyon ve Gelecek Beklentisi")
st.markdown("""<div class="inf-box"><b>💡 Enflasyon Nedir?</b><br>Bugün 100 liraya aldığın 10 ekmeğin, seneye aynı parayla sadece 6 tanesini alabilmendir.</div>""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("💵 Güncel Dolar", f"{GUNCEL_DOLAR} TL"); m2.metric("📊 Q1 Enflasyon", f"%{Q1_ENF}"); m3.metric("🏦 TCMB Faiz", f"%{TCMB_FAIZ}"); m4.metric("🎯 TCMB Hedef", f"%{TCMB_2026_HEDEF}")
st.divider()

col_in, col_out = st.columns([1.2, 2])
with col_in:
    st.subheader("🕵️ Analist Girişi")
    u_name = st.text_input("Rumuz:", "Analist_01", key="u_n")
    c1, c2 = st.columns(2)
    u_gender = c1.selectbox("Cinsiyet:", ["Erkek", "Kadın", "Diğer"], key="u_g")
    u_salary = c2.number_input("Aylık Maaş (TL):", value=22102, key="u_s")
    u_city = st.selectbox("Şehir:", ["İstanbul", "Ankara", "İzmir", "Kırklareli", "Bursa", "Antalya", "Diğer"], key="u_c")
    u_prof = st.selectbox("Harcama Sepeti:", ["Öğrenci", "Emekli", "Beyaz Yakalı", "Esnaf", "Yeni Evli 💍", "Gamer 🎮", "Araç Sahibi 🚗"], key="u_p")
    
    st.write("🔮 **Hızlı Senaryo Seçimi**")
    s1, s2, s3, s4 = st.columns(4)
    if s1.button("🏦 TCMB", key="b_1"): st.session_state.update({'d_val': 15, 'g_val': 22, 'k_val': 22, 'u_val': 20}); st.rerun()
    if s2.button("🌸 İyimser", key="b_2"): st.session_state.update({'d_val': 12, 'g_val': 30, 'k_val': 35, 'u_val': 25}); st.rerun()
    if s3.button("📊 Realist", key="b_3"): st.session_state.update({'d_val': 35, 'g_val': 55, 'k_val': 65, 'u_val': 45}); st.rerun()
    if s4.button("🌋 Kriz", key="b_4"): st.session_state.update({'d_val': 85, 'g_val': 110, 'k_val': 125, 'u_val': 95}); st.rerun()
    
    d_a = st.slider("💵 Dolar Artışı (%)", 0, 150, key='d_val')
    g_a = st.slider("🛒 Gıda Artışı (%)", 0, 150, key='g_val')
    k_a = st.slider("🏠 Kira Artışı (%)", 0, 150, key='k_val')
    u_a = st.slider("🚗 Ulaşım Artışı (%)", 0, 150, key='u_val')

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.15, 0.25, 0.45, 0.15], "Emekli": [0.05, 0.55, 0.30, 0.10], "Beyaz Yakalı": [0.20, 0.30, 0.30, 0.20], "Esnaf": [0.40, 0.20, 0.20, 0.20], "Yeni Evli 💍": [0.15, 0.20, 0.50, 0.15], "Gamer 🎮": [0.40, 0.20, 0.20, 0.20], "Araç Sahibi 🚗": [0.15, 0.20, 0.25, 0.40]}
w = weights[u_prof]; slider_enf = (d_a*w[0] + g_a*w[1] + k_a*w[2] + u_a*w[3]); res_total = Q1_ENF + slider_enf 
alim_kaybi, tahmini_kur = (1 - (1 / (1 + res_total/100))) * 100, GUNCEL_DOLAR * (1 + d_a/100)
f_ps5, f_iphone, f_car = P_PS5_GUNCEL*(1+res_total/85), P_IPHONE_GUNCEL*(1+(d_a*0.85+res_total*0.15)/100), P_CAR_GUNCEL*(1+(d_a*0.7+res_total*0.3)/100)

with col_out:
    st.markdown(f"""<div class="ozet-panel"><h3 style="color:#888; margin-bottom:5px;">Yıl Sonu Beklenti Analizi</h3><div style="display:flex; justify-content: space-around; align-items:center;"><div><small>Q1 Gerçekleşen</small><br><b style="font-size:24px; color:#00d4ff;">%{Q1_ENF}</b></div><div style="font-size:30px; color:#555;">+</div><div><small>Senin Nisan-Aralık Tahminin</small><br><b style="font-size:24px; color:#ffbd45;">%{slider_enf:.1f}</b></div><div style="font-size:30px; color:#555;">=</div><div><small><b>Yıl Sonu Toplamı</b></small><br><b style="font-size:36px; color:#ff4b4b;">%{res_total:.1f}</b></div></div><hr style="border:0.5px solid #333;"><p style="margin:0; font-size:18px;">Tahmini Kur: <span style="color:#00d4ff; font-weight:bold;">{tahmini_kur:.2f} TL</span></p></div>""", unsafe_allow_html=True)
    h1, h2, h3 = st.columns(3)
    with h1: 
        st.metric("🎮 2026 Sonu PS5", f"{f_ps5:,.0f} TL")
        st.markdown(f'<p class="bugun-etiket">Bugün PS5 Slim: 42.999 TL</p>', unsafe_allow_html=True)
    with h2: 
        st.metric("📱 2026 Sonu iPhone", f"{f_iphone:,.0f} TL")
        st.markdown(f'<p class="bugun-etiket">Bugün iPhone 17: 77.999 TL</p>', unsafe_allow_html=True)
    with h3: 
        st.metric("🚗 2026 Sonu Clio", f"{f_car:,.0f} TL")
        st.markdown(f'<p class="bugun-etiket">Bugün Clio: 1.795.000 TL</p>', unsafe_allow_html=True)
    st.divider()
    c_g, c_e = st.columns(2)
    with c_g: st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=alim_kaybi, title={'text': "Alım Gücü Kaybı (%)"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#ff4b4b"}})).update_layout(height=230, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}), use_container_width=True)
    with c_e: st.write("### 📉 1.000 TL Akıbeti"); st.title(f"{1000/(1+res_total/100):.2f} TL"); st.markdown(f'<div style="background-color: #333; border-radius: 5px; height:20px;"><div style="background-color: #ff4b4b; width: {max(0, 100-alim_kaybi)}%; height: 20px; border-radius: 5px;"></div></div>', unsafe_allow_html=True)

st.divider()

# --- 🕰️ ZAMAN MAKİNESİ ---
st.subheader("🕰️ Zaman Makinesi: Asgari Ücretin Erimesi (2000-2025)")
yillar = [str(y) for y in range(2000, 2026)]; altin = [24.5, 11.2, 12.5, 13.1, 17.8, 18.2, 15.1, 14.8, 14.1, 11.8, 10.5, 8.5, 8.0, 9.5, 10.5, 10.1, 10.4, 9.6, 7.5, 7.8, 5.1, 5.6, 5.3, 6.5, 6.8, 4.5]
dolar = [126, 92, 115, 150, 222, 261, 265, 315, 385, 352, 395, 393, 410, 420, 406, 365, 430, 385, 330, 355, 330, 315, 330, 430, 520, 485]
df_nost = pd.DataFrame({"Yıl": yillar, "Gram Altın": altin, "Dolar ($)": dolar})
g1, g2 = st.columns(2)
with g1: st.plotly_chart(px.bar(df_nost, x="Yıl", y="Gram Altın", text_auto='.1f', title="Maaş Kaç Gram Altın?", color="Gram Altın", color_continuous_scale='YlOrBr'), use_container_width=True)
with g2: st.plotly_chart(px.bar(df_nost, x="Yıl", y="Dolar ($)", text_auto='.0f', title="Maaş Kaç Dolar?", color="Dolar ($)", color_continuous_scale='Greens'), use_container_width=True)

if st.button("💾 ANALİZİ KAYDET VE GELECEK ADİSYONUNU AL", use_container_width=True, key="save_final"):
    save_data(u_name, u_gender, u_salary, u_prof, u_city, slider_enf, res_total, tahmini_kur, alim_kaybi, 1000/(1+res_total/100))
    st.balloons()
    b_y, g_y = 1000, 1000 * (1 + res_total/100)
    st.markdown(f"""<div class="receipt-box"><center>🧾 <b>LiraPulse ADİSYON</b></center><hr>31.12.2026 | GELECEK FATURASI<br>--------------------------------<br>Müşteri: {u_name}<br>--------------------------------<br>1x Akşam Yemeği (2 Kişi)<br>(Bugün: 1000 TL) : {g_y:,.0f} TL<br>--------------------------------<br><b>TOPLAM (SENİN SENARYON) : {g_y:,.0f} TL</b><br>Fazladan Ödeyeceğin: +{g_y-b_y:,.0f} TL<br>--------------------------------<br><center><i>Veri kaydedildi.</i></center></div>""", unsafe_allow_html=True)

# --- 🔐 YÖNETİCİ PANELİ ---
with st.expander("🔐 LiraPulse Intelligence Admin Control Center"):
    admin_pass = st.text_input("Yönetici Şifresi:", type="password", key="adm_auth")
    if admin_pass == "alper2026":
        if os.path.exists(DB_FILE):
            try: # --- 📈 YÖNETİCİ İSTATİSTİKLERİ VE GRAFİKLER (GERİ GELDİ) ---
                st.markdown('<div style="background-color: #0d1117; padding: 20px; border-radius: 15px; border: 1px solid #00d4ff;">', unsafe_allow_html=True)
                st.write("### 📊 Sokağın Nabzı & Analitik")
                
                # Üst Metrikler (Sayısal Özeti)
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("Toplam Katılım", f"{len(df)} Kişi")
                stat_col2.metric("Ort. Maaş", f"{pd.to_numeric(df['Maas'], errors='coerce').mean():,.0f} TL")
                stat_col3.metric("Ort. Enflasyon", f"%{pd.to_numeric(df['Yil_Sonu_Toplam'], errors='coerce').mean():.1f}")
                
                st.write("---")
                # Pasta Grafikleri (Cinsiyet ve Sepet)
                gr_col1, gr_col2 = st.columns(2)
                with gr_col1:
                    st.write("**👤 Cinsiyet Dağılımı**")
                    st.plotly_chart(px.pie(df, names='Cinsiyet', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
                
                with gr_col2:
                    st.write("**🛒 En Çok Analiz Yapan Sepetler**")
                    st.plotly_chart(px.pie(df, names='Profil', hole=0.4, color_discrete_sequence=px.colors.sequential.Reds_r), use_container_width=True)
                
                # Şehir ve Trend Grafikleri
                st.write("**📍 Şehirlere Göre Katılım Yoğunluğu**")
                st.plotly_chart(px.bar(df['Sehir'].value_counts().reset_index(), x='Sehir', y='count', color='count', color_continuous_scale='Viridis'), use_container_width=True)
                
                st.write("**💰 Maaş vs Beklenen Enflasyon (Trend)**")
                st.plotly_chart(px.scatter(df, x='Maas', y='Yil_Sonu_Toplam', color='Profil', hover_name='Katilimci', size_max=60), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()
                
                # --- ALT KISIMDA TROL TEMİZLEME TABLOSU DEVAM EDER ---
                df = pd.read_csv(DB_FILE, on_bad_lines='skip')
                if len(df.columns) == len(COL_LIST):
                    df.columns = COL_LIST
                    st.write("### 📊 Sokağın Nabzı")
                    s1, s2, s3 = st.columns(3)
                    s1.metric("Toplam Kişi", f"{len(df)}")
                    s2.metric("Ort. Enflasyon", f"%{pd.to_numeric(df['Yil_Sonu_Toplam'], errors='coerce').mean():.1f}")
                    s3.metric("Ort. Maaş", f"{pd.to_numeric(df['Maas'], errors='coerce').mean():,.0f} TL")
                    st.divider()
                    st.write("### 🧹 Trol Temizliği")
                    df_c = df.reset_index(drop=True)
                    df_c.index = range(len(df_c))
                    df_c.insert(0, "Seç", False)
                    edited = st.data_editor(df_c, column_config={"Seç": st.column_config.CheckboxColumn("Sil?", default=False)}, disabled=COL_LIST, use_container_width=True, key="adm_clean_final")
                    if st.button("🗑️ SEÇİLENLERİ SİL", key="btn_del_final"):
                        df_f = edited[edited["Seç"] == False].drop(columns=["Seç"])
                        df_f.to_csv(DB_FILE, index=False); st.rerun()
                else: st.error("Dosya yapısı uyumsuz! Veritabanını sıfırla.")
            except Exception as e: st.error(f"Hata: {e}")
            if st.button("🔴 VERİTABANINI SIFIRLA", key="btn_rst_final"): os.remove(DB_FILE); st.rerun()
