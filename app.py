import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid
import requests

# --- 🔐 GOOGLE SHEETS MOTORU ---
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["gcp_service_account"].to_dict()
    if "private_key" in creds_info:
        creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)

def save_to_sheets(veri):
    try:
        client = get_gspread_client()
        sheet = client.open("LiraPulse_Veri").sheet1 
        sheet.append_row(veri)
        return True
    except Exception as e:
        st.error(f"Kayıt Hatası: {e}")
        return False

# --- 🇹🇷 TÜRKÇE SAYI FORMATLAYICI ---
def tr_format(number, decimals=2):
    try:
        val = float(number)
        if decimals == 0:
            fmt = f"{val:,.0f}"
            return fmt.replace(',', '.')
        else:
            fmt = f"{val:,.2f}"
            s = fmt.replace(',', 'X').replace('.', ',').replace('X', '.')
            if s.endswith(",00"): return s[:-3]
            return s
    except: return "0"

# --- 🌐 CANLI DOLAR ÇEKİCİ ---
@st.cache_data(ttl=3600)
def get_live_usd():
    try:
        res = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=2)
        return round(res.json()['rates']['TRY'], 2)
    except:
        return 44.59

# --- 📊 PİYASA VERİLERİ ---
GUNCEL_DOLAR = get_live_usd()
Q1_ENF, TCMB_FAIZ, TCMB_2026_HEDEF = 14.40, 37.0, 22.0
P_PS5, P_IPHONE, P_CLIO = 42999, 77999, 1795000

st.set_page_config(page_title="LiraPulse: Geleceğin Faturası", layout="wide")

# --- 🎨 CSS: BİLGİSAYAR TASARIMI + YENİ NESİL MOBİL ZIRHI ---
st.markdown("""<style>
    /* --- BİLGİSAYAR TASARIMI (ASLA DOKUNULMADI) --- */
    .main { background-color: #0d1117; }
    [data-testid="stMetric"] { background-color: #161b22; padding: 15px !important; border-radius: 15px; border-left: 5px solid #00d4ff; }
    .ozet-panel { background: linear-gradient(145deg, #1e1e26, #252532); padding: 25px; border-radius: 15px; border: 1px solid #30363d; text-align: center; }
    .bugun-etiket { color: #ffbd45; font-size: 13px; text-align: center; margin-top: -10px; font-weight: bold; }
    .ekmek-text { color: #ffbd45; font-size: 16px; margin-bottom: 25px; line-height: 1.5; }
    .receipt-box { background-color: #fff; color: #333 !important; padding: 30px; border-radius: 10px; font-family: 'Courier New', monospace; border: 3px dashed #333; margin: 20px auto; max-width: 500px; line-height: 1.8; text-align: left; }
    
    .mobile-live-preview { display: none; }
    
    /* --- 📱 SADECE MOBİL İÇİN DÜZELTMELER --- */
    @media (max-width: 768px) {
        .main .block-container { padding: 0.5rem !important; max-width: 100% !important; overflow-x: hidden !important; }
        
        /* Özet paneli mobilde gizli kalsın (Yandaki kutu yetiyor) */
        .ozet-panel { display: none !important; }
        
        /* 1. Tepe Metrikleri: 2x2 ufak kutular */
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) {
            flex-direction: row !important; flex-wrap: wrap !important; gap: 5px 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div[data-testid="column"] {
            width: 48% !important; flex: 0 0 48% !important; min-width: 48% !important;
        }

        /* 2. PS5, iPhone, Clio: İsteğin üzerine ALT ALTA ve NET */
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(3):last-child):has([data-testid="stMetric"]) {
            flex-direction: column !important; gap: 10px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(3):last-child):has([data-testid="stMetric"]) > div[data-testid="column"] {
            width: 100% !important; min-width: 100% !important;
        }

        /* 3. Slider ve Yanındaki Analiz Kutusu */
        div[data-testid="column"]:nth-child(1) { position: relative !important; }
        div[data-testid="stSlider"] { width: 55% !important; margin-left: 0 !important; }
        
        .mobile-live-preview {
            display: flex !important; flex-direction: column; justify-content: center;
            position: absolute !important; right: 0; bottom: 10px; width: 42%; height: 275px; 
            background: linear-gradient(145deg, #161b22, #1e1e26); border: 1px solid #ff4b4b;
            border-radius: 10px; padding: 5px; text-align: center; z-index: 99;
        }

        /* 4. Tablolar: Yatayda genişlesin ve tüm değerler gözüksün (Scroll eklendi) */
        [data-testid="stExpander"] [data-testid="stDataFrame"] {
            width: 100% !important;
            overflow-x: auto !important; /* Sağa kaydırmayı açar */
            display: block !important;
        }
        [data-testid="stExpander"] [data-testid="stDataFrame"] div[data-testid="stTable"] {
            min-width: 600px !important; /* Tablonun daralmasını engeller */
        }
        
        .stButton button { font-size: 11px !important; }
    }
    </style>""", unsafe_allow_html=True)

if 'd_val' not in st.session_state: st.session_state.update({'d_val': 35, 'g_val': 55, 'k_val': 65, 'u_val': 45})

# --- 🔐 ADMIN PANELİ ---
if 'admin_data' not in st.session_state: st.session_state['admin_data'] = []
with st.sidebar.expander("🔐 Admin Control Center"):
    if st.text_input("Şifre:", type="password", key="adm_pw") == st.secrets["ADMIN_PASSWORD"]:
        if st.button("🔄 Verileri Excel'den Tazele", use_container_width=True):
            try:
                client = get_gspread_client(); sheet = client.open("LiraPulse_Veri").sheet1; vals = sheet.get_all_values()
                if len(vals) > 1:
                    new_data = []
                    for i in range(1, len(vals)):
                        row = vals[i]
                        new_data.append({"Tarih": row[0], "Analist": row[1], "Cinsiyet": row[2], "Maas": row[3], "Profil": row[4], "Sehir": row[5], "Kayit_ID": str(row[6]), "Enflasyon": row[8], "Dolar": row[9], "Reel": row[11]})
                    st.session_state['admin_data'] = new_data; st.success("Çekildi!")
            except Exception as e: st.error(f"Hata: {e}")

# --- 🍞 ÜST BAŞLIK ---
st.title("🛰️ LiraPulse: Geleceğin Faturası")
st.markdown('<p class="ekmek-text">💡 <b>Enflasyon Nedir?</b><br>Bugün 100 liraya aldığın 10 ekmeğin, seneye aynı parayla sadece 6 tanesini alabilmendir.</p>', unsafe_allow_html=True)

# --- 📈 TEPE METRİKLERİ ---
tm1, tm2, tm3, tm4 = st.columns(4)
tm1.metric("💵 Güncel Dolar", f"{GUNCEL_DOLAR} TL")
tm2.metric("📉 Q1 Enflasyon", f"%{Q1_ENF}")
tm3.metric("🏦 TCMB Faiz", f"%{TCMB_FAIZ}")
tm4.metric("🎯 TCMB Hedef", f"%{TCMB_2026_HEDEF}")
st.divider()

col_in, col_out = st.columns([1.2, 2])

with col_in:
    st.subheader("🕵️ Analist Girişi")
    u_name = st.text_input("Rumuz:", "Analist_01")
    c_col1, c_col2 = st.columns(2)
    with c_col1: u_gender = st.selectbox("Cinsiyet:", ["Erkek", "Kadın", "Diger"])
    with c_col2: u_salary = st.number_input("Aylık Maaş (TL):", value=22102)
    u_prof = st.selectbox("Harcama Sepeti:", ["Öğrenci", "Mavi Yaka", "Beyaz Yaka", "Emekli", "Kamu Personeli"])
    u_city = st.selectbox("Şehir:", ["Kırklareli", "İstanbul", "Ankara", "İzmir", "Diğer"])
    
    st.write("🔮 **Hızlı Senaryo Seçimi**")
    s1, s2, s3, s4, s5, s6 = st.columns(6)
    if s1.button("🏦 TCMB", use_container_width=True): st.session_state.update({'d_val': 5, 'g_val': 8, 'k_val': 7, 'u_val': 6}); st.rerun()
    if s2.button("🌸 İyimser", use_container_width=True): st.session_state.update({'d_val': 20, 'g_val': 32, 'k_val': 30, 'u_val': 28}); st.rerun()
    if s3.button("📉 TÜİK", use_container_width=True): st.session_state.update({'d_val': 12, 'g_val': 22, 'k_val': 20, 'u_val': 16}); st.rerun()
    if s4.button("📊 Realist", use_container_width=True): st.session_state.update({'d_val': 35, 'g_val': 48, 'k_val': 50, 'u_val': 42}); st.rerun()
    if s5.button("🔥 ENAG", use_container_width=True): st.session_state.update({'d_val': 55, 'g_val': 70, 'k_val': 75, 'u_val': 60}); st.rerun()
    if s6.button("🌋 Kriz", use_container_width=True): st.session_state.update({'d_val': 100, 'g_val': 120, 'k_val': 130, 'u_val': 110}); st.rerun()
    
    st.divider()
    d_a = st.slider("💵 Dolar Artışı (%)", 0, 150, key='d_val')
    g_a = st.slider("🛒 Gıda Artışı (%)", 0, 150, key='g_val')
    k_a = st.slider("🏠 Kira Artışı (%)", 0, 150, key='k_val')
    u_a = st.slider("🚗 Ulaşım Artışı (%)", 0, 150, key='u_val')

    weights = {"Öğrenci": [0.25, 0.20, 0.40, 0.15], "Mavi Yaka": [0.10, 0.45, 0.30, 0.15], "Beyaz Yaka": [0.20, 0.25, 0.35, 0.20], "Emekli": [0.05, 0.55, 0.30, 0.10], "Kamu Personeli": [0.15, 0.30, 0.35, 0.20]}
    w = weights[u_prof]
    s_enf_live = round((d_a*w[0] + g_a*w[1] + k_a*w[2] + u_a*w[3]), 2)
    res_total_live = round(Q1_ENF + s_enf_live, 2)
    tahmini_kur_live = round(GUNCEL_DOLAR * (1 + d_a/100), 2)
    
    st.markdown(f"""<div class="mobile-live-preview">
        <div style="color:#ccc; font-size:10px;">Q1 Gerçekleşen</div>
        <div style="color:#00d4ff; font-size:16px; font-weight:bold;">%{tr_format(Q1_ENF)}</div>
        <div style="color:#ccc; font-size:10px; margin-top:5px;">Senin Tahminin</div>
        <div style="color:#ffbd45; font-size:16px; font-weight:bold;">%{tr_format(s_enf_live)}</div>
        <div style="color:#ccc; font-size:11px; font-weight:bold; border-top:1px solid #333; margin-top:5px;">Yıl Sonu Toplamı</div>
        <div style="color:#ff4b4b; font-size:22px; font-weight:bold;">%{tr_format(res_total_live)}</div>
        <div style="color:#aaa; font-size:10px; margin-top:5px;">Kur: <b style="color:#fff;">{tr_format(tahmini_kur_live)} TL</b></div>
    </div>""", unsafe_allow_html=True)

s_enf = s_enf_live
res_total = res_total_live
tahmini_kur = tahmini_kur_live
alim_kaybi = round((1 - (1 / (1 + res_total/100))) * 100, 2)
reel_deger = round(1000/(1+res_total/100), 2)

with col_out:
    st.markdown(f"""<div class="ozet-panel">
        <h3 style="color:#aaa;">Yıl Sonu Beklenti Analizi</h3>
        <b style="font-size:36px; color:#ff4b4b;">%{tr_format(res_total)}</b><br>
        <p style="color:#ccc;">Tahmini Kur: {tr_format(tahmini_kur)} TL</p>
    </div>""", unsafe_allow_html=True)
    
    st.write("") 
    h1, h2, h3 = st.columns(3)
    with h1: st.metric("🎮 PS5 (2026)", f"{tr_format(P_PS5*(1+res_total/85), 0)} TL"); st.markdown(f'<p class="bugun-etiket">Bugün: {tr_format(P_PS5, 0)} TL</p>', unsafe_allow_html=True)
    with h2: st.metric("📱 iPhone (2026)", f"{tr_format(P_IPHONE*(1+res_total/95), 0)} TL"); st.markdown(f'<p class="bugun-etiket">Bugün: {tr_format(P_IPHONE, 0)} TL</p>', unsafe_allow_html=True)
    with h3: st.metric("🚗 Clio (2026)", f"{tr_format(P_CLIO*(1+res_total/100), 0)} TL"); st.markdown(f'<p class="bugun-etiket">Bugün: 1,79M TL</p>', unsafe_allow_html=True)
    
    st.divider()
    c_g, c_e = st.columns(2)
    with c_g: st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=alim_kaybi, title={'text': "Alım Gücü Kaybı (%)"}, gauge={'bar': {'color': "#ff4b4b"}})).update_layout(height=220, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}), use_container_width=True)
    with c_e: st.markdown(f"""<div style="background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d;">
            <p style="color: #aaa; font-size: 14px;">📉 1.000 TL Akıbeti</p>
            <h2 style="color: #fff;">{tr_format(reel_deger)} TL</h2>
        </div>""", unsafe_allow_html=True)

st.divider()

with st.expander("⚔️ 2020-2025: Enflasyonu Yenenler ve Yenilenler Tablosunu Gör", expanded=False):
    df_yatirim = pd.DataFrame({
        "Yıl": ["2020", "2021", "2022", "2023", "2024", "2025"],
        "Enflasyon (%)": [14.6, 36.1, 64.3, 64.8, 44.8, 25.0],
        "TL Mevduat (%)": [12.0, 17.5, 16.0, 36.0, 51.0, 42.0],
        "Dolar (%)": [24.8, 78.5, 40.2, 57.3, 25.1, 18.0],
        "Gram Altın (%)": [55.9, 71.2, 42.8, 78.4, 40.5, 22.0],
        "BIST 100 (%)": [29.1, 25.8, 196.6, 35.1, 46.2, 32.0]
    })
    st.dataframe(df_yatirim, use_container_width=True, hide_index=True)

with st.expander("🛒 Sokağın Enflasyonu: Pazarın Şampiyonları Tablosunu Gör", expanded=False):
    df_sokak = pd.DataFrame({
        "Yıl": ["2020", "2021", "2022", "2023", "2024", "2025"],
        "🔥 En Çok Artan": ["2. El Oto", "Yağ", "Soğan", "Zeytinyağı", "Okul", "Et"],
        "Artış (%)": [85, 130, 315, 180, 120, 95],
        "❄️ En Az Artan": ["Uçak", "Elektirik", "İnternet", "Doğalgaz", "Oto", "Soğan"]
    })
    st.dataframe(df_sokak, use_container_width=True, hide_index=True)

if st.button("💾 ANALİZİ KAYDET VE ADİSYONU AL", use_container_width=True):
    if save_to_sheets([datetime.now().strftime("%d.%m.%Y"), u_name, u_gender, u_salary, u_prof, u_city, uuid.uuid4().hex[:8], "-", f"'{tr_format(res_total)}", f"'{tr_format(tahmini_kur)}", "-", f"'{tr_format(reel_deger)}"]):
        st.balloons()
        st.markdown(f"""<div class="receipt-box"><center><b>🧾 LiraPulse ADİSYON</b></center><br>
            <p>TARİH: 31.12.2026</p><p>ANALİST: {u_name}</p><hr>
            <p>Toplam (Yıl Başı: 1.000 TL): <b>{tr_format(1000*(1+res_total/100), 0)} TL</b></p><hr>
            <center><i>Geleceği Görmek Cesaret İster.</i></center></div>""", unsafe_allow_html=True)
