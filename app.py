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

# --- 🇹🇷 TÜRKÇE SAYI FORMATLAYICI (Gereksiz Sıfırlar Yok) ---
def tr_format(number):
    try:
        val = float(number)
        fmt = f"{val:,.2f}"
        s = fmt.replace(',', 'X').replace('.', ',').replace('X', '.')
        if s.endswith(",00"):
            return s[:-3]
        return s
    except:
        return "0"

# --- 📊 PİYASA VERİLERİ ---
GUNCEL_DOLAR, Q1_ENF, TCMB_FAIZ, TCMB_2026_HEDEF = 44.92, 14.40, 37.0, 21.0
P_PS5, P_IPHONE, P_CLIO = 42999, 77999, 1795000

st.set_page_config(page_title="LiraPulse: Gelecek Analizi", layout="wide")

# --- 🎨 CSS ---
st.markdown("""<style>
    .main { background-color: #0d1117; }
    [data-testid="stMetric"] { background-color: #161b22; padding: 15px !important; border-radius: 15px; border-left: 5px solid #00d4ff; }
    .ozet-panel { background: linear-gradient(145deg, #1e1e26, #252532); padding: 25px; border-radius: 15px; border: 1px solid #30363d; text-align: center; }
    .bugun-etiket { color: #ffbd45; font-size: 13px; text-align: center; margin-top: -10px; font-weight: bold; }
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
    u_prof = st.selectbox("Harcama Sepeti:", ["Öğrenci", "Mavi Yaka", "Beyaz Yaka", "Emekli", "Kamu Personeli"])
    u_city = st.selectbox("Şehir:", ["Kırklareli", "İstanbul", "Ankara", "İzmir", "Diğer"])
    
    st.write("🔮 **Senaryo Seç**")
    s1, s2, s3, s4, s5, s6 = st.columns(6)
    if s1.button("🏦 TCMB"): st.session_state.update({'d_val': 5, 'g_val': 8, 'k_val': 7, 'u_val': 6}); st.rerun()
    if s2.button("📉 TÜİK"): st.session_state.update({'d_val': 12, 'g_val': 22, 'k_val': 20, 'u_val': 16}); st.rerun()
    if s3.button("📊 Realist"): st.session_state.update({'d_val': 35, 'g_val': 48, 'k_val': 50, 'u_val': 42}); st.rerun()
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
    st.markdown(f"""<div class="ozet-panel"><h3>Yıl Sonu Beklenti Analizi</h3><div style="display:flex; justify-content: space-around; align-items:center;"><div><small>Q1 Gerçekleşen</small><br><b style="font-size:24px; color:#00d4ff;">%{tr_format(Q1_ENF)}</b></div><div style="font-size:30px; color:#555;">+</div><div><small>Tahminin</small><br><b style="font-size:24px; color:#ffbd45;">%{tr_format(s_enf)}</b></div><div style="font-size:30px; color:#555;">=</div><div><small><b>Yıl Sonu Toplamı</b></small><br><b style="font-size:36px; color:#ff4b4b;">%{tr_format(res_total)}</b></div></div><hr style="border:0.5px solid #333;"><p>Tahmini Kur: <b>{tr_format(tahmini_kur)} TL</b></p></div>""", unsafe_allow_html=True)
    h1, h2, h3 = st.columns(3)
    with h1: st.metric("🎮 PS5 (2026)", f"{tr_format(P_PS5*(1+res_total/85))} TL")
    with h2: st.metric("📱 iPhone (2026)", f"{tr_format(P_IPHONE*(1+res_total/95))} TL")
    with h3: st.metric("🚗 Clio (2026)", f"{tr_format(P_CLIO*(1+res_total/100))} TL")
    st.divider()
    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=alim_kaybi, title={'text': "Alım Gücü Kaybı (%)"}, gauge={'bar': {'color': "#ff4b4b"}})).update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}), use_container_width=True)

# --- 💾 EXCEL'E KAYIT ---
if st.button("💾 ANALİZİ KAYDET VE GELECEK ADİSYONUNU AL", use_container_width=True):
    def f_tr(val):
        s = f"{val:.2f}".replace(".", ",")
        if s.endswith(",00"): s = s[:-3]
        return f"'{s}"
    
    kayit_id = str(uuid.uuid4().hex[:8]).upper()
    reel_kalan = round(1000/(1+res_total/100), 2)
    zaman_damgasi = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    v = [zaman_damgasi, u_name, u_gender, f_tr(u_salary), u_prof, u_city, kayit_id, f_tr(s_enf), f_tr(res_total), f_tr(tahmini_kur), f_tr(alim_kaybi), f_tr(reel_kalan)]
    
    if save_to_sheets(v):
        st.balloons()
        st.markdown(f"""<div class="receipt-box"><center>🧾 <b>LiraPulse ADİSYON</b></center><hr><p><b>Analist:</b> {u_name}</p><p><b>ID:</b> {kayit_id}</p><p><b>Yıl Sonu Enflasyon:</b> %{tr_format(res_total)}</p><p><b>Dolar Beklentisi:</b> {tr_format(tahmini_kur)} TL</p><hr><center><i>Veri Google Sheets'e Mermi Gibi İşlendi.</i></center></div>""", unsafe_allow_html=True)

# --- 🔐 ADMIN PANELİ ---
if 'admin_data' not in st.session_state: st.session_state['admin_data'] = []

with st.expander("🔐 Admin Control Center"):
    if st.text_input("Şifre:", type="password", key="adm_pw") == "alper2026":
        
        if st.button("🔄 Verileri Excel'den Tazele"):
            try:
                client = get_gspread_client()
                sheet = client.open("LiraPulse_Veri").sheet1
                records = sheet.get_all_records()
                
                if records:
                    def clean_num(val):
                        try:
                            s = str(val).replace("'", "").strip()
                            if s == "": return 0.0
                            if '.' in s and ',' in s: s = s.replace('.', '').replace(',', '.')
                            elif ',' in s: s = s.replace(',', '.')
                            return float(s)
                        except: return 0.0

                    clean_data = []
                    for i, row in enumerate(records):
                        t_col = 'Yil_Sonu_Toplam' if 'Yil_Sonu_Toplam' in row else ('Yil_Sonu_Toplar' if 'Yil_Sonu_Toplar' in row else None)
                        clean_data.append({
                            "Tarih": str(row.get("Tarih", row.get("Zaman Damgası", ""))), 
                            "Katilimci": str(row.get("Katilimci", row.get("Rumuz", ""))), 
                            "Maas": clean_num(row.get("Maas", 0)),
                            "Kayit_ID": str(row.get("IP", row.get("IP Adresi", row.get("Kimlik No (ID)", "")))).strip(), 
                            "Enflasyon": clean_num(row.get(t_col, 0)),
                            "Dolar": clean_num(row.get("Dolar_Beklentisi", 0)), # Dolar kolonunu buradan çekiyoruz
                            "Excel_Row": i + 2
                        })
                    st.session_state['admin_data'] = clean_data
                    st.success("Veriler çekildi!")
                else: st.info("Excel'de veri yok.")
            except Exception as e: st.error(f"Hata: {e}")

        if len(st.session_state['admin_data']) > 0:
            df_admin = pd.DataFrame(st.session_state['admin_data'])
            
            st.write("### 📈 Sokağın Röntgenti")
            s1, s2, s3, s4 = st.columns(4) # 4 sütun yaptık
            s1.metric("Toplam Katılım", f"{len(df_admin)} Kişi")
            s2.metric("Ort. Maaş", f"{tr_format(df_admin['Maas'].mean())} TL")
            s3.metric("Ort. Enflasyon", f"%{tr_format(df_admin['Enflasyon'].mean())}")
            s4.metric("Ort. Dolar Beklentisi", f"{tr_format(df_admin['Dolar'].mean())} TL") # YENİ METRİK BURADA
            
            st.divider()
            df_edit = df_admin.copy(); df_edit.insert(0, "Seç", False)
            edited_df = st.data_editor(df_edit, column_config={"Seç": st.column_config.CheckboxColumn("Sil?", default=False), "Maas": st.column_config.NumberColumn("Maaş", format="%.0f"), "Enflasyon": st.column_config.NumberColumn("Enf", format="%.2f"), "Dolar": st.column_config.NumberColumn("Dolar", format="%.2f"), "Excel_Row": None}, use_container_width=True, hide_index=True)
            
            if st.button("🗑️ SEÇİLENLERİ EXCEL'DEN KAZI"):
                try:
                    secilen_idler = edited_df[edited_df["Seç"] == True]["Kayit_ID"].dropna().tolist()
                    if secilen_idler:
                        client = get_gspread_client(); sheet = client.open("LiraPulse_Veri").sheet1; all_vals = sheet.get_all_values()
                        rows_to_del = []
                        for i, row_data in enumerate(all_vals):
                            if i == 0: continue
                            if len(row_data) > 6 and str(row_data[6]).strip() in secilen_idler: rows_to_del.append(i + 1)
                        rows_to_del.sort(reverse=True)
                        for r_num in rows_to_del: sheet.delete_rows(int(r_num))
                        st.success(f"{len(rows_to_del)} veri silindi!"); st.session_state['admin_data'] = []; st.rerun()
                except Exception as e: st.error(f"Hata: {e}")
