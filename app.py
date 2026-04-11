import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

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

# --- 🛰️ CANLI VERİ SENKRONİZASYONU (Kritik Çözüm) ---
if 'live_data' not in st.session_state:
    try:
        # Uygulama ilk açıldığında Excel'deki geçmişi çek ve temizle
        client = get_gspread_client()
        sheet = client.open("LiraPulse_Veri").sheet1
        existing_data = pd.DataFrame(sheet.get_all_records())
        # Virgül-Nokta temizliği (Gümrük Filtresi)
        for col in ['Maas', 'Yil_Sonu_Toplam', 'Dolar_Beklentisi', 'Alim_Gucu_Kaybi', 'Reel_Kalan_TL']:
            if col in existing_data.columns:
                existing_data[col] = existing_data[col].apply(lambda x: float(str(x).replace(',', '.')) if x != "" else 0.0)
        st.session_state.live_data = existing_data
    except:
        st.session_state.live_data = pd.DataFrame()

# --- 📊 PİYASA VERİLERİ ---
GUNCEL_DOLAR, Q1_ENF, TCMB_FAIZ, TCMB_2026_HEDEF = 44.92, 14.40, 37.0, 21.0
P_PS5, P_IPHONE, P_CLIO = 42999, 77999, 1795000

st.set_page_config(page_title="LiraPulse: Gelecek Beklentisi", layout="wide")

# --- 🎨 CSS ---
st.markdown("""<style>
    .main { background-color: #0d1117; }
    [data-testid="stMetric"] { background-color: #161b22; padding: 15px !important; border-radius: 15px; border-left: 5px solid #00d4ff; }
    .ozet-panel { background: linear-gradient(145deg, #1e1e26, #252532); padding: 25px; border-radius: 15px; border: 1px solid #30363d; text-align: center; }
    .receipt-box { background-color: #fff; color: #333 !important; padding: 20px; border-radius: 5px; font-family: 'Courier New', monospace; border: 2px dashed #333; margin: 20px auto; max-width: 450px; line-height: 1.6; }
    .receipt-box b, .receipt-box center, .receipt-box p { color: #333 !important; }
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
    
    st.write("🔮 **Senaryo Seç**")
    s_cols = st.columns(6)
    if s_cols[0].button("🏦 TCMB"): st.session_state.update({'d_val': 5, 'g_val': 8, 'k_val': 7, 'u_val': 6}); st.rerun()
    if s_cols[1].button("📉 TÜİK"): st.session_state.update({'d_val': 12, 'g_val': 22, 'k_val': 20, 'u_val': 16}); st.rerun()
    if s_cols[2].button("🌸 İyimser"): st.session_state.update({'d_val': 20, 'g_val': 32, 'k_val': 30, 'u_val': 28}); st.rerun()
    if s_cols[3].button("📊 Realist"): st.session_state.update({'d_val': 35, 'g_val': 48, 'k_val': 50, 'u_val': 42}); st.rerun()
    if s_cols[4].button("🔥 ENAG"): st.session_state.update({'d_val': 55, 'g_val': 70, 'k_val': 75, 'u_val': 60}); st.rerun()
    if s_cols[5].button("🌋 Kriz"): st.session_state.update({'d_val': 100, 'g_val': 120, 'k_val': 130, 'u_val': 110}); st.rerun()
    
    d_a = st.slider("💵 Dolar Artışı (%)", 0, 150, key='d_val')
    g_a = st.slider("🛒 Gıda Artışı (%)", 0, 150, key='g_val')
    k_a = st.slider("🏠 Kira Artışı (%)", 0, 150, key='k_val')
    u_a = st.slider("🚗 Ulaşım Artışı (%)", 0, 150, key='u_val')

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.25, 0.20, 0.40, 0.15], "Mavi Yaka": [0.10, 0.45, 0.30, 0.15], "Beyaz Yaka": [0.20, 0.25, 0.35, 0.20], "Emekli": [0.05, 0.55, 0.30, 0.10], "Kamu Personeli": [0.15, 0.30, 0.35, 0.20]}
w = weights[u_prof]
s_enf = round((d_a*w[0] + g_a*w[1] + k_a*w[2] + u_a*w[3]), 2)
res_total = round(Q1_ENF + s_enf, 2)
tahmini_kur = round(GUNCEL_DOLAR * (1 + d_a/100), 2)
alim_kaybi = round((1 - (1 / (1 + res_total/100))) * 100, 2)

with col_out:
    st.markdown(f"""<div class="ozet-panel"><h3>Yıl Sonu Beklenti Analizi</h3><div style="display:flex; justify-content: space-around; align-items:center;"><div><small>Q1</small><br><b style="font-size:24px; color:#00d4ff;">%{Q1_ENF}</b></div><div style="font-size:30px; color:#555;">+</div><div><small>Tahmin</small><br><b style="font-size:24px; color:#ffbd45;">%{s_enf:.2f}</b></div><div style="font-size:30px; color:#555;">=</div><div><small><b>TOPLAM</b></small><br><b style="font-size:36px; color:#ff4b4b;">%{res_total:.2f}</b></div></div></div>""", unsafe_allow_html=True)
    st.metric("💵 Tahmini Kur", f"{tahmini_kur:.2f} TL")
    h1, h2, h3 = st.columns(3)
    with h1: st.metric("🎮 PS5", f"{P_PS5*(1+res_total/85):,.0f} TL")
    with h2: st.metric("📱 iPhone", f"{P_IPHONE*(1+res_total/95):,.0f} TL")
    with h3: st.metric("🚗 Clio", f"{P_CLIO*(1+res_total/100):,.0f} TL")
    st.divider()
    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=alim_kaybi, title={'text': "Alım Gücü Kayabı (%)"}, gauge={'bar': {'color': "#ff4b4b"}})).update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}), use_container_width=True)

# --- 💾 KAYIT VE ADİSYON ---
if st.button("💾 ANALİZİ KAYDET VE GELECEK ADİSYONUNU AL", use_container_width=True):
    # Excel formatı (%24,44)
    v_excel = [datetime.now().strftime("%d.%m.%Y %H:%M"), u_name, u_gender, str(u_salary).replace(".",","), u_prof, u_city, "0.0.0.0", str(s_enf).replace(".",","), str(res_total).replace(".",","), str(tahmini_kur).replace(".",","), str(alim_kaybi).replace(".",","), str(round(1000/(1+res_total/100), 2)).replace(".",",")]
    
    # Canlı sistem formatı (Saf sayı)
    new_entry = pd.DataFrame([{
        "Tarih": v_excel[0], "Analist": u_name, "Cinsiyet": u_gender, "Maas": u_salary, "Profil": u_prof, "Sehir": u_city, "IP": "0.0.0.0", "Kalan_Enf": s_enf, "Yil_Sonu_Toplam": res_total, "Dolar_Beklentisi": tahmini_kur, "Alim_Gucu_Kaybi": alim_kaybi, "Reel_Kalan_TL": round(1000/(1+res_total/100), 2)
    }])
    
    if save_to_sheets(v_excel):
        st.session_state.live_data = pd.concat([st.session_state.live_data, new_entry], ignore_index=True)
        st.balloons()
        st.markdown(f"""<div class="receipt-box"><center>🧾 <b>LiraPulse ADİSYON</b></center><hr><p><b>Analist:</b> {u_name}</p><p><b>Profil:</b> {u_prof}</p><p><b>Yıl Sonu Toplam:</b> %{res_total:.2f}</p><p><b>1.000 TL Reel Değeri:</b> {round(1000/(1+res_total/100), 2):.2f} TL</p><hr><center><i>Veri Kaydedildi.</i></center></div>""", unsafe_allow_html=True)

# --- 🔐 ADMIN (CANLI VERİDEN ÇALIŞIR) ---
with st.expander("🔐 Admin Control Center"):
    if st.text_input("Şifre:", type="password", key="adm_pw") == "alper2026":
        df = st.session_state.live_data
        if not df.empty:
            st.write("### 📈 Sokağın Röntgenti (Canlı Hafıza)")
            s1, s2, s3 = st.columns(3)
            s1.metric("Katılım", f"{len(df)} Kişi")
            s2.metric("Ort. Maaş", f"{df['Maas'].mean():,.2f} TL")
            # Excel'den değil, canlı hafızadan okuduğu için artık %24.44 mermi gibi çıkar
            s3.metric("Ort. Enflasyon", f"%{df['Yil_Sonu_Toplam'].mean():.2f}")
            
            gr1, gr2, gr3 = st.columns(3)
            with gr1: st.plotly_chart(px.pie(df, names='Cinsiyet', title="Cinsiyet", hole=0.4), use_container_width=True)
            with gr2: st.plotly_chart(px.pie(df, names='Sehir', title="Şehir", hole=0.4), use_container_width=True)
            with gr3: st.plotly_chart(px.pie(df, names='Profil', title="Sepet", hole=0.4), use_container_width=True)
            
            st.divider()
            st.write("### 🧹 Veri Yönetimi")
            df_display = df.copy()
            df_display.insert(0, "Seç", False)
            edited_df = st.data_editor(df_display, column_config={"Seç": st.column_config.CheckboxColumn("Sil?", default=False)}, use_container_width=True, hide_index=True)
            
            if st.button("🗑️ SEÇİLENLERİ SİL"):
                rows_to_keep = edited_df[edited_df["Seç"] == False].drop(columns=["Seç"])
                st.session_state.live_data = rows_to_keep
                # Excel'i de güncelle
                client = get_gspread_client()
                sheet = client.open("LiraPulse_Veri").sheet1
                sheet.clear()
                # Excel'e geri yazarken virgüllü yaz
                df_to_excel = rows_to_keep.copy()
                for col in ['Maas', 'Kalan_Enf', 'Yil_Sonu_Toplam', 'Dolar_Beklentisi', 'Alim_Gucu_Kaybi', 'Reel_Kalan_TL']:
                    df_to_excel[col] = df_to_excel[col].apply(lambda x: str(round(x, 2)).replace(".", ","))
                sheet.update([df_to_excel.columns.values.tolist()] + df_to_excel.values.tolist())
                st.success("Temizlendi!")
                st.rerun()
