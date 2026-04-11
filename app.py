import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 🔐 GOOGLE SHEETS BAĞLANTISI ---
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Secrets'tan bilgileri al
    creds_info = st.secrets["gcp_service_account"].to_dict()
    # PEM hatasını önlemek için \n işaretlerini gerçek alt satıra çevir
    if "private_key" in creds_info:
        creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)

def save_to_sheets(veri_listesi):
    try:
        client = get_gspread_client()
        sheet = client.open("LiraPulse_Veri").sheet1 
        sheet.append_row(veri_listesi)
        return True
    except Exception as e:
        st.error(f"Veri kaydedilemedi: {e}")
        return False

# --- 📊 PİYASA VERİLERİ ---
GUNCEL_DOLAR, Q1_ENF, TCMB_FAIZ, TCMB_2026_HEDEF = 44.92, 14.40, 37.0, 22.0
P_PS5_GUNCEL, P_IPHONE_GUNCEL, P_CAR_GUNCEL = 42999, 77999, 1795000

st.set_page_config(page_title="LiraPulse v2.0", layout="wide")

# --- 🎨 CSS TASARIMI (GÜNCELLENDİ) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 15px; border-left: 5px solid #00d4ff; color: white; }
    .ozet-panel { background: linear-gradient(145deg, #1e1e26, #252532); padding: 20px; border-radius: 15px; border: 1px solid #30363d; text-align: center; color: white; }
    .receipt-box { 
        background-color: #f8f9fa; 
        color: #333 !important; 
        padding: 20px; 
        border-radius: 10px; 
        font-family: 'Courier New', monospace; 
        border: 2px dashed #333; 
        margin: 20px auto;
        max-width: 400px;
        line-height: 1.4;
    }
    .receipt-box b, .receipt-box center { color: #333 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ LiraPulse: Gelecek Beklentisi v2.0")

if 'd_val' not in st.session_state: st.session_state.update({'d_val': 35, 'g_val': 55, 'k_val': 65, 'u_val': 45})

col_in, col_out = st.columns([1.2, 2])

with col_in:
    st.subheader("🕵️ Analist Girişi")
    u_name = st.text_input("Rumuz:", "Analist_01")
    u_salary = st.number_input("Mevcut Maaş (TL):", value=22102)
    u_prof = st.selectbox("Sepet Türü:", ["Öğrenci", "Beyaz Yakalı", "Gamer 🎮", "Araç Sahibi 🚗"])
    u_city = st.selectbox("Şehir:", ["Kırklareli", "İstanbul", "Ankara", "İzmir", "Diğer"])
    
    d_a = st.slider("💵 Dolar Artışı (%)", 0, 150, key='d_val')
    g_a = st.slider("🛒 Gıda Artışı (%)", 0, 150, key='g_val')
    k_a = st.slider("🏠 Kira Artışı (%)", 0, 150, key='k_val')
    u_a = st.slider("🚗 Ulaşım Artışı (%)", 0, 150, key='u_val')

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.15, 0.25, 0.45, 0.15], "Beyaz Yakalı": [0.20, 0.30, 0.30, 0.20], "Gamer 🎮": [0.40, 0.20, 0.20, 0.20], "Araç Sahibi 🚗": [0.15, 0.20, 0.25, 0.40]}
w = weights[u_prof]
slider_enf = (d_a*w[0] + g_a*w[1] + k_a*w[2] + u_a*w[3])
res_total = Q1_ENF + slider_enf
alim_kaybi = (1 - (1 / (1 + res_total/100))) * 100
tahmini_kur = GUNCEL_DOLAR * (1 + d_a/100)

with col_out:
    st.markdown(f"""<div class="ozet-panel"><h3>Yıl Sonu Beklenti Analizi</h3><b style="font-size:36px; color:#ff4b4b;">%{res_total:.1f}</b><br>Tahmini Kur: {tahmini_kur:.2f} TL</div>""", unsafe_allow_html=True)
    
    if st.button("💾 ANALİZİ KAYDET VE FİŞ AL", use_container_width=True):
        tarih = datetime.now().strftime("%d.%m.%Y %H:%M")
        veri = [tarih, u_name, "", u_salary, u_prof, u_city, "0.0.0.0", slider_enf, res_total, tahmini_kur, alim_kaybi, 1000/(1+res_total/100)]
        
        if save_to_sheets(veri):
            st.balloons()
            st.markdown(f"""
            <div class="receipt-box">
                <center>🧾 <b>LiraPulse ADİSYON</b></center>
                <hr style="border: 0.5px solid #333;">
                <b>Analist:</b> {u_name}<br>
                <b>Şehir:</b> {u_city}<br>
                <b>Yıl Sonu Tahmini:</b> %{res_total:.1f}<br>
                <b>Tahmini Kur:</b> {tahmini_kur:.2f} TL<br>
                <hr style="border: 0.5px dashed #333;">
                <center><i>Veri Google Sheets'e Kaydedildi.</i></center>
            </div>
            """, unsafe_allow_html=True)

# --- 🔐 ADMIN ---
with st.expander("🔐 Admin Paneli"):
    if st.text_input("Şifre:", type="password") == "alper2026":
        try:
            client = get_gspread_client()
            sheet = client.open("LiraPulse_Veri").sheet1
            df_cloud = pd.DataFrame(sheet.get_all_records())
            st.dataframe(df_cloud)
        except Exception as e:
            st.write(f"Veri çekilemedi: {e}")
