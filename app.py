import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid

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
def tr_format(number):
    try:
        val = float(number)
        fmt = f"{val:,.2f}"
        s = fmt.replace(',', 'X').replace('.', ',').replace('X', '.')
        if s.endswith(",00"): return s[:-3]
        return s
    except: return "0"

# --- 📊 PİYASA VERİLERİ ---
GUNCEL_DOLAR, Q1_ENF = 44.92, 14.40

st.set_page_config(page_title="LiraPulse: Enflasyon ve Gelecek Beklentisi", layout="wide")

# --- 🎨 CSS ---
st.markdown("""<style>
    .main { background-color: #0d1117; }
    [data-testid="stMetric"] { background-color: #161b22; padding: 15px !important; border-radius: 15px; border-left: 5px solid #00d4ff; }
    .ozet-panel { background: linear-gradient(145deg, #1e1e26, #252532); padding: 25px; border-radius: 15px; border: 1px solid #30363d; text-align: center; }
    .receipt-box { background-color: #fff; color: #333 !important; padding: 20px; border-radius: 5px; border: 2px dashed #333; margin: 20px auto; max-width: 450px; line-height: 1.6; }
    .receipt-box b, .receipt-box center, .receipt-box p { color: #333 !important; }
    </style>""", unsafe_allow_html=True)

if 'd_val' not in st.session_state: st.session_state.update({'d_val': 35, 'g_val': 55, 'k_val': 65, 'u_val': 45})

st.title("🛰️ LiraPulse: Enflasyon ve Gelecek Beklentisi")
st.markdown("Enflasyon, paranın alım gücünün düşmesi ve yaşam maliyetlerinin artmasıdır. Bu panel üzerinden kendi beklentilerini oluşturabilirsin.")

col_in, col_out = st.columns([1.2, 2])

with col_in:
    st.subheader("🕵️ Analist Girişi")
    u_name = st.text_input("Rumuz:", "Analist_01")
    u_salary = st.number_input("Aylık Maaş (TL):", value=22102)
    u_prof = st.selectbox("Harcama Sepeti:", ["Öğrenci", "Mavi Yaka", "Beyaz Yaka", "Emekli", "Kamu Personeli"])
    u_city = st.selectbox("Şehir:", ["Kırklareli", "İstanbul", "Ankara", "İzmir", "Diğer"])
    u_gender = st.selectbox("Cinsiyet:", ["Erkek", "Kadın", "Belirtmek İstemiyorum"])
    
    st.write("🔮 **Senaryo Seç**")
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
s_enf = round((d_a*w[0] + g_a*w[1] + k_a*w[2] + u_a*w[3]), 2)
res_total = round(Q1_ENF + s_enf, 2)
tahmini_kur = round(GUNCEL_DOLAR * (1 + d_a/100), 2)
alim_kaybi = round((1 - (1 / (1 + res_total/100))) * 100, 2)

with col_out:
    st.markdown(f"""<div class="ozet-panel"><h3>Yıl Sonu Beklenti Analizi</h3><b style="font-size:36px; color:#ff4b4b;">%{tr_format(res_total)}</b><br><p>Tahmini Kur: <b>{tr_format(tahmini_kur)} TL</b></p></div>""", unsafe_allow_html=True)
    st.divider()
    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=alim_kaybi, title={'text': "Alım Gücü Kaybı (%)"}, gauge={'bar': {'color': "#ff4b4b"}})).update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}), use_container_width=True)

# --- 💾 EXCEL'E KAYIT ---
if st.button("💾 ANALİZİ KAYDET", use_container_width=True):
    def f_tr(val):
        s = f"{val:.2f}".replace(".", ",")
        return f"'{s[:-3]}" if s.endswith(",00") else f"'{s}"
    kayit_id = str(uuid.uuid4().hex[:8]).upper()
    v = [datetime.now().strftime("%d.%m.%Y %H:%M"), u_name, u_gender, f_tr(u_salary), u_prof, u_city, kayit_id, f_tr(s_enf), f_tr(res_total), f_tr(tahmini_kur), f_tr(alim_kaybi), f_tr(round(1000/(1+res_total/100), 2))]
    if save_to_sheets(v):
        st.balloons()
        st.markdown(f"""<div class="receipt-box"><center>🧾 <b>LiraPulse ADİSYON</b></center><hr><p><b>Analist:</b> {u_name}</p><p><b>Enflasyon:</b> %{tr_format(res_total)}</p><p><b>Dolar:</b> {tr_format(tahmini_kur)} TL</p></div>""", unsafe_allow_html=True)

# --- 🔐 ADMIN PANELİ ---
if 'admin_data' not in st.session_state: st.session_state['admin_data'] = []

with st.expander("🔐 Admin Control Center"):
    if st.text_input("Şifre:", type="password", key="adm_pw") == "alper2026":
        if st.button("🔄 Verileri Excel'den Tazele"):
            try:
                client = get_gspread_client()
                sheet = client.open("LiraPulse_Veri").sheet1
                vals = sheet.get_all_values()
                if len(vals) > 1:
                    def clean_num(val):
                        try:
                            s = str(val).replace("'", "").strip()
                            if not s: return 0.0
                            if '.' in s and ',' in s: s = s.replace('.', '').replace(',', '.')
                            elif ',' in s: s = s.replace(',', '.')
                            return float(s)
                        except: return 0.0
                    clean_data = []
                    for i in range(1, len(vals)):
                        row = vals[i]
                        clean_data.append({
                            "Tarih": row[0] if len(row) > 0 else "", "Analist": row[1] if len(row) > 1 else "", "Cinsiyet": row[2] if len(row) > 2 else "",
                            "Maas": clean_num(row[3]) if len(row) > 3 else 0.0, "Profil": row[4] if len(row) > 4 else "", "Sehir": row[5] if len(row) > 5 else "",
                            "Kayit_ID": str(row[6]).strip() if len(row) > 6 else "", "Enflasyon": clean_num(row[8]) if len(row) > 8 else 0.0, "Dolar": clean_num(row[9]) if len(row) > 9 else 0.0
                        })
                    st.session_state['admin_data'] = clean_data
                    st.success("Excel'den veriler çekildi!")
                else: 
                    st.session_state['admin_data'] = []
                    st.info("Excel boş.")
            except Exception as e: st.error(f"Hata: {e}")

        if st.session_state['admin_data']:
            df = pd.DataFrame(st.session_state['admin_data'])
            
            # --- ÖZET KUTULARI ---
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Toplam Katılım", f"{len(df)} Kişi")
            s2.metric("Ort. Maaş", f"{tr_format(df['Maas'].mean())} TL")
            s3.metric("Ort. Enflasyon", f"%{tr_format(df['Enflasyon'].mean())}")
            s4.metric("Ort. Dolar", f"{tr_format(df['Dolar'].mean())} TL")
            
            # --- 🛡️ GRAFİK KORUMASI ---
            if not df.empty:
                g_col1, g_col2, g_col3 = st.columns(3)
                with g_col1:
                    if 'Cinsiyet' in df.columns and not df['Cinsiyet'].isnull().all():
                        st.plotly_chart(px.pie(df, names='Cinsiyet', title="Cinsiyet Dağılımı", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu), use_container_width=True)
                with g_col2:
                    if 'Sehir' in df.columns and not df['Sehir'].isnull().all():
                        st.plotly_chart(px.pie(df, names='Sehir', title="Şehir Dağılımı", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues), use_container_width=True)
                with g_col3:
                    if 'Profil' in df.columns and not df['Profil'].isnull().all():
                        st.plotly_chart(px.pie(df, names='Profil', title="Harcama Sepeti", hole=0.4, color_discrete_sequence=px.colors.sequential.Greens), use_container_width=True)
            
            st.divider()
            df_edit = df.copy(); df_edit.insert(0, "Seç", False)
            edited_df = st.data_editor(df_edit, column_config={"Seç": st.column_config.CheckboxColumn("Sil?", default=False), "Maas": st.column_config.NumberColumn("Maaş", format="%.0f")}, use_container_width=True, hide_index=True)
            
            if st.button("🗑️ SEÇİLENLERİ SİL"):
                sec_idler = edited_df[edited_df["Seç"] == True]["Kayit_ID"].tolist()
                if sec_idler:
                    client = get_gspread_client(); sheet = client.open("LiraPulse_Veri").sheet1; all_vals = sheet.get_all_values()
                    rows_to_del = [i+1 for i, r in enumerate(all_vals) if len(r) > 6 and str(r[6]).strip() in sec_idler]
                    for r_num in sorted(rows_to_del, reverse=True): sheet.delete_rows(r_num)
                    st.success(f"{len(rows_to_del)} veri silindi!"); st.session_state['admin_data'] = []; st.rerun()
