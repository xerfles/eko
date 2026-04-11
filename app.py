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

# --- 📊 PİYASA VERİLERİ ---
GUNCEL_DOLAR, Q1_ENF, TCMB_FAIZ, TCMB_2026_HEDEF = 44.92, 14.40, 37.0, 21.0
P_PS5, P_IPHONE, P_CLIO = 42999, 77999, 1795000

st.set_page_config(page_title="LiraPulse: Gelecek Analizi", layout="wide")

# --- 🎨 CSS: TASARIM VE ADİSYON KORUMASI ---
st.markdown("""<style>
    .main { background-color: #0d1117; }
    [data-testid="stMetric"] { background-color: #161b22; padding: 15px !important; border-radius: 15px; border-left: 5px solid #00d4ff; }
    .ozet-panel { background: linear-gradient(145deg, #1e1e26, #252532); padding: 25px; border-radius: 15px; border: 1px solid #30363d; text-align: center; }
    .bugun-etiket { color: #ffbd45; font-size: 13px; text-align: center; margin-top: -10px; font-weight: bold; }
    .receipt-box { background-color: #fff; color: #333 !important; padding: 20px; border-radius: 5px; font-family: 'Courier New', monospace; border: 2px dashed #333; margin: 20px auto; max-width: 450px; line-height: 1.6; }
    .receipt-box b, .receipt-box center, .receipt-box p, .receipt-box hr { color: #333 !important; border-color: #333 !important; }
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
    st.markdown(f"""<div class="ozet-panel"><h3>Yıl Sonu Beklenti Analizi</h3><div style="display:flex; justify-content: space-around; align-items:center;"><div><small>Q1 Gerçekleşen</small><br><b style="font-size:24px; color:#00d4ff;">%{Q1_ENF}</b></div><div style="font-size:30px; color:#555;">+</div><div><small>Tahminin</small><br><b style="font-size:24px; color:#ffbd45;">%{s_enf:.2f}</b></div><div style="font-size:30px; color:#555;">=</div><div><small><b>Yıl Sonu Toplamı</b></small><br><b style="font-size:36px; color:#ff4b4b;">%{res_total:.2f}</b></div></div><hr style="border:0.5px solid #333;"><p>Tahmini Kur: <b>{tahmini_kur:.2f} TL</b></p></div>""", unsafe_allow_html=True)
    h1, h2, h3 = st.columns(3)
    with h1: st.metric("🎮 PS5 (2026)", f"{P_PS5*(1+res_total/85):,.0f} TL"); st.markdown(f'<p class="bugun-etiket">Bugün: {P_PS5:,.0f} TL</p>', unsafe_allow_html=True)
    with h2: st.metric("📱 iPhone (2026)", f"{P_IPHONE*(1+res_total/95):,.0f} TL"); st.markdown(f'<p class="bugun-etiket">Bugün: {P_IPHONE:,.0f} TL</p>', unsafe_allow_html=True)
    with h3: st.metric("🚗 Clio (2026)", f"{P_CLIO*(1+res_total/100):,.0f} TL"); st.markdown(f'<p class="bugun-etiket">Bugün: 1.795.000 TL</p>', unsafe_allow_html=True)
    st.divider()
    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=alim_kaybi, title={'text': "Alım Gücü Kaybı (%)"}, gauge={'bar': {'color': "#ff4b4b"}})).update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}), use_container_width=True)

st.divider()

# --- 🕰️ ZAMAN MAKİNESİ ---
st.subheader("🕰️ Zaman Makinesi: Asgari Ücretin Erimesi")
yillar = [str(y) for y in range(2000, 2026)]; altin = [24.5, 11.2, 12.5, 13.1, 17.8, 18.2, 15.1, 14.8, 14.1, 11.8, 10.5, 8.5, 8.0, 9.5, 10.5, 10.1, 10.4, 9.6, 7.5, 7.8, 5.1, 5.6, 5.3, 6.5, 6.8, 4.5]
dolar = [126, 92, 115, 150, 222, 261, 265, 315, 385, 352, 395, 393, 410, 420, 406, 365, 430, 385, 330, 355, 330, 315, 330, 430, 520, 485]
df_nost = pd.DataFrame({"Yıl": yillar, "Gram Altın": altin, "Dolar ($)": dolar})
g1, g2 = st.columns(2)
with g1: st.plotly_chart(px.bar(df_nost, x="Yıl", y="Gram Altın", title="Maaş Kaç Gram Altın?", color="Gram Altın", color_continuous_scale="YlOrBr"), use_container_width=True)
with g2: st.plotly_chart(px.bar(df_nost, x="Yıl", y="Dolar ($)", title="Maaş Kaç Dolar?", color="Dolar ($)", color_continuous_scale="Greens"), use_container_width=True)

# --- 💾 EXCEL'E KAYIT (VİRGÜLLÜ) ---
if st.button("💾 ANALİZİ KAYDET VE GELECEK ADİSYONUNU AL", use_container_width=True):
    def f_tr(val): return "{:.2f}".format(val).replace(".", ",")
    reel_kalan = round(1000/(1+res_total/100), 2)
    zaman_damgasi = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    v = [zaman_damgasi, u_name, u_gender, f_tr(u_salary), u_prof, u_city, "0.0.0.0", f_tr(s_enf), f_tr(res_total), f_tr(tahmini_kur), f_tr(alim_kaybi), f_tr(reel_kalan)]
    if save_to_sheets(v):
        st.balloons()
        st.markdown(f"""<div class="receipt-box"><center>🧾 <b>LiraPulse ADİSYON</b></center><hr><p><b>Analist:</b> {u_name}</p><p><b>Yıl Sonu Tahmini:</b> %{res_total:.2f}</p><p><b>1.000 TL Reel Değer:</b> {reel_kalan:.2f} TL</p><hr><center><i>Veri Google Sheets'e Mermi Gibi İşlendi.</i></center></div>""", unsafe_allow_html=True)

# --- 🔐 ADMIN: DİREKT EXCEL BAĞLANTISI (OTOMATİK ÇEKİM) ---
with st.expander("🔐 Admin Control Center"):
    if st.text_input("Şifre:", type="password", key="adm_pw") == "alper2026":
        try:
            client = get_gspread_client()
            sheet = client.open("LiraPulse_Veri").sheet1
            records = sheet.get_all_records()
            
            if records:
                # KRİTİK TEMİZLİK: Excel'den ne gelirse gelsin noktaya çevir, sayı yap.
                def clean_num(val):
                    try: return float(str(val).replace(',', '.').strip())
                    except: return 0.0

                clean_data = []
                for i, row in enumerate(records):
                    # Bazen sütun adları değişebiliyor, garantiye alalım
                    t_col = 'Yil_Sonu_Toplam' if 'Yil_Sonu_Toplam' in row else ('Yil_Sonu_Toplar' if 'Yil_Sonu_Toplar' in row else None)
                    enf_val = clean_num(row.get(t_col, 0)) if t_col else 0.0
                    
                    clean_data.append({
                        "Zaman": row.get("Zaman Damgası", ""), "Rumuz": row.get("Rumuz", ""), 
                        "Cinsiyet": row.get("Cinsiyet", ""), "Maas": clean_num(row.get("Maas", 0)),
                        "Profil": row.get("Profil", ""), "Sehir": row.get("Sehir", ""), 
                        "IP": row.get("IP", "0.0.0.0"), "Yil_Sonu_Toplam": enf_val,
                        "Excel_Row": i + 2  # Excel'de 1. satır başlıktır
                    })
                
                df_admin = pd.DataFrame(clean_data)
                
                st.write("### 📈 Sokağın Röntgenti")
                s1, s2, s3 = st.columns(3)
                s1.metric("Toplam Katılım", f"{len(df_admin)} Kişi")
                s2.metric("Ort. Maaş", f"{df_admin['Maas'].mean():,.2f} TL")
                s3.metric("Ort. Enflasyon", f"%{df_admin['Yil_Sonu_Toplam'].mean():.2f}")
                
                gr1, gr2, gr3 = st.columns(3)
                with gr1: st.plotly_chart(px.pie(df_admin, names='Cinsiyet', title="Cinsiyet", hole=0.4), use_container_width=True)
                with gr2: st.plotly_chart(px.pie(df_admin, names='Sehir', title="Şehir", hole=0.4), use_container_width=True)
                with gr3: st.plotly_chart(px.pie(df_admin, names='Profil', title="Profil", hole=0.4), use_container_width=True)
                
                st.divider()
                df_edit = df_admin.copy()
                df_edit.insert(0, "Seç", False)
                # Excel_Row sütununu gizleyerek göster
                edited_df = st.data_editor(df_edit, column_config={
                    "Seç": st.column_config.CheckboxColumn("Sil?", default=False), 
                    "Maas": st.column_config.NumberColumn("Maaş", format="%.2f"),
                    "Excel_Row": None 
                }, use_container_width=True, hide_index=True)
                
                if st.button("🗑️ SEÇİLENLERİ SİL"):
                    try:
                        rows_to_del = sorted(edited_df[edited_df["Seç"] == True]["Excel_Row"].dropna().tolist(), reverse=True)
                        if rows_to_del:
                            for r_num in rows_to_del: 
                                sheet.delete_rows(int(r_num))
                            st.success(f"{len(rows_to_del)} veri Excel'den kazındı!")
                            st.rerun() # Sayfayı yenile ki yeni Excel durumu gelsin
                        else:
                            st.warning("Silinecek veri seçmedin.")
                    except Exception as e: st.error(f"Silme Hatası: {e}")
            else:
                st.info("Excel dosyasında henüz veri yok.")
                
        except Exception as e: st.error(f"Excel Bağlantı Hatası: {e}")
