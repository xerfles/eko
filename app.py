import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

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

# --- 📊 PİYASA VERİLERİ (GÜNCEL) ---
GUNCEL_DOLAR, Q1_ENF, TCMB_FAIZ, TCMB_2026_HEDEF = 44.92, 14.40, 37.0, 21.0
P_PS5, P_IPHONE, P_CLIO = 42999, 77999, 1795000

st.set_page_config(page_title="LiraPulse: Gelecek Beklentisi", layout="wide")

# --- 🎨 CSS ---
st.markdown("""<style>
    .main { background-color: #0d1117; }
    [data-testid="stMetric"] { background-color: #161b22; padding: 15px !important; border-radius: 15px; border-left: 5px solid #00d4ff; }
    .ozet-panel { background: linear-gradient(145deg, #1e1e26, #252532); padding: 25px; border-radius: 15px; border: 1px solid #30363d; text-align: center; }
    </style>""", unsafe_allow_html=True)

if 'd_val' not in st.session_state: st.session_state.update({'d_val': 35, 'g_val': 55, 'k_val': 65, 'u_val': 45})

st.title("🛰️ LiraPulse: Enflasyon ve Gelecek Beklentisi")

col_in, col_out = st.columns([1.2, 2])

with col_in:
    st.subheader("🕵️ Analist Girişi")
    u_name = st.text_input("Rumuz:", "Analist_01")
    u_gender = st.selectbox("Cinsiyet:", ["Erkek", "Kadın", "Belirtmek İstemiyorum"])
    u_salary = st.number_input("Aylık Maaş (TL):", value=22102)
    u_prof = st.selectbox("Harcama Sepeti (Profil):", ["Öğrenci", "Mavi Yaka", "Beyaz Yaka", "Emekli", "Kamu Personeli"])
    u_city = st.selectbox("Şehir:", ["Kırklareli", "İstanbul", "Ankara", "İzmir", "Diğer"])
    
    st.write("🔮 **Gelecek Senaryosunu Seç**")
    s1, s2, s3, s4, s5, s6 = st.columns(6)
    if s1.button("🏦 TCMB"): st.session_state.update({'d_val': 5, 'g_val': 8, 'k_val': 7, 'u_val': 6}); st.rerun()
    if s2.button("📉 TÜİK"): st.session_state.update({'d_val': 12, 'g_val': 22, 'k_val': 20, 'u_val': 16}); st.rerun()
    if s3.button("🌸 İyimser"): st.session_state.update({'d_val': 20, 'g_val': 32, 'k_val': 30, 'u_val': 28}); st.rerun()
    if s4.button("📊 Realist"): st.session_state.update({'d_val': 35, 'g_val': 48, 'k_val': 50, 'u_val': 42}); st.rerun()
    if s5.button("🔥 ENAG"): st.session_state.update({'d_val': 55, 'g_val': 70, 'k_val': 75, 'u_val': 60}); st.rerun()
    if s6.button("🌋 Kriz"): st.session_state.update({'d_val': 100, 'g_val': 120, 'k_val': 130, 'u_val': 110}); st.rerun()
    
    d_a = st.slider("💵 Dolar Artışı (%)", 0, 150, key='d_val')
    g_a = st.slider("🛒 Gıda Artışı (%)", 0, 150, key='g_val')
    k_a = st.slider("🏠 Kira Artışı (%)", 0, 150, key='k_val')
    u_a = st.slider("🚗 Ulaşım Artışı (%)", 0, 150, key='u_val')

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.25, 0.20, 0.40, 0.15], "Mavi Yaka": [0.10, 0.45, 0.30, 0.15], "Beyaz Yaka": [0.20, 0.25, 0.35, 0.20], "Emekli": [0.05, 0.55, 0.30, 0.10], "Kamu Personeli": [0.15, 0.30, 0.35, 0.20]}
w = weights[u_prof]
s_enf = (d_a*w[0] + g_a*w[1] + k_a*w[2] + u_a*w[3])
res_total = Q1_ENF + s_enf
tahmini_kur = GUNCEL_DOLAR * (1 + d_a/100)
alim_kaybi = (1 - (1 / (1 + res_total/100))) * 100

with col_out:
    st.markdown(f"""<div class="ozet-panel"><h3 style="color:#888; margin-bottom:5px;">Yıl Sonu Beklenti Analizi</h3><div style="display:flex; justify-content: space-around; align-items:center;"><div><small>Q1 Gerçekleşen</small><br><b style="font-size:24px; color:#00d4ff;">%{Q1_ENF}</b></div><div style="font-size:30px; color:#555;">+</div><div><small>Senin Tahminin</small><br><b style="font-size:24px; color:#ffbd45;">%{s_enf:.1f}</b></div><div style="font-size:30px; color:#555;">=</div><div><small><b>Yıl Sonu Toplamı</b></small><br><b style="font-size:36px; color:#ff4b4b;">%{res_total:.1f}</b></div></div><hr style="border:0.5px solid #333;"><p style="margin:0; font-size:18px;">Tahmini Kur: <span style="color:#00d4ff; font-weight:bold;">{tahmini_kur:.2f} TL</span></p></div>""", unsafe_allow_html=True)
    h1, h2, h3 = st.columns(3)
    with h1: st.metric("🎮 PS5 (2026)", f"{P_PS5*(1+res_total/85):,.0f} TL")
    with h2: st.metric("📱 iPhone (2026)", f"{P_IPHONE*(1+res_total/95):,.0f} TL")
    with h3: st.metric("🚗 Clio (2026)", f"{P_CLIO*(1+res_total/100):,.0f} TL")
    st.divider()
    st.write("### 📉 1.000 TL Akıbeti")
    st.title(f"{1000/(1+res_total/100):.2f} TL")

if st.button("💾 ANALİZİ KAYDET VE GELECEK ADİSYONUNU AL", use_container_width=True):
    v = [datetime.now().strftime("%d.%m.%Y %H:%M"), u_name, u_gender, str(u_salary).replace(".",","), u_prof, u_city, "0.0.0.0", str(s_enf).replace(".",","), str(res_total).replace(".",","), str(tahmini_kur).replace(".",","), str(alim_kaybi).replace(".",","), str(1000/(1+res_total/100)).replace(".",",")]
    if save_to_sheets(v):
        st.balloons()
        st.success("Veriler Google Sheets'e mermi gibi işlendi!")

# --- 🔐 ADMIN ---
with st.expander("🔐 Admin Control Center"):
    if st.text_input("Şifre:", type="password", key="adm_pw") == "alper2026":
        try:
            client = get_gspread_client()
            sheet = client.open("LiraPulse_Veri").sheet1
            df_cloud = pd.DataFrame(sheet.get_all_records())
            
            if not df_cloud.empty:
                # --- 📉 KRİTİK VERİ TEMİZLEME MOTORU ---
                def parse_tr_float(val):
                    try: return float(str(val).replace(',', '.'))
                    except: return 0.0

                df_cloud['Maas'] = df_cloud['Maas'].apply(parse_tr_float)
                # Sütun adı düzeltildi
                target_col = 'Yil_Sonu_Toplam' if 'Yil_Sonu_Toplam' in df_cloud.columns else 'Yil_Sonu_Toplar'
                df_cloud['Clean_Enf'] = df_cloud[target_col].apply(parse_tr_float)
                df_cloud['Dolar_Beklentisi'] = df_cloud['Dolar_Beklentisi'].apply(parse_tr_float)

                st.write("### 📈 Sokağın Röntgenti")
                s1, s2, s3 = st.columns(3)
                s1.metric("Toplam Katılım", f"{len(df_cloud)} Kişi")
                s2.metric("Ort. Maaş", f"{df_cloud['Maas'].mean():,.2f} TL")
                # Artık tertemiz bir ortalama çıkacak
                s3.metric("Ort. Enflasyon", f"%{df_cloud['Clean_Enf'].mean():.2f}")
                
                # Pasta Grafikleri
                gr1, gr2, gr3 = st.columns(3)
                with gr1: st.plotly_chart(px.pie(df_cloud, names='Cinsiyet', title="Cinsiyet"), use_container_width=True)
                with gr2: st.plotly_chart(px.pie(df_cloud, names='Sehir', title="Şehir"), use_container_width=True)
                with gr3: st.plotly_chart(px.pie(df_cloud, names='Profil', title="Profil"), use_container_width=True)
                
                st.divider()
                st.write("### 🧹 Veri Temizliği (Gerçek IP'ler Gösteriliyor)")
                st.data_editor(df_cloud.drop(columns=['Clean_Enf']), column_config={
                    "Maas": st.column_config.NumberColumn("Maaş", format="%.2f"),
                    target_col: st.column_config.NumberColumn("Enflasyon", format="%.2f"),
                    "Dolar_Beklentisi": st.column_config.NumberColumn("Kur Tahmini", format="%.2f"),
                    "IP": st.column_config.TextColumn("IP Adresi")
                }, use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Hata: {e}")
