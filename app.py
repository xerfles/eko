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

# --- 🛰️ CANLI HAFIZA SİSTEMİ (SESSION STATE) ---
if 'live_data' not in st.session_state:
    st.session_state['live_data'] = []

# --- 🇹🇷 TÜRKÇE SAYI FORMATLAYICI ---
def tr_format(number, decimals=2):
    try:
        val = float(number)
        fmt = f"{{:,.{decimals}f}}".format(val)
        s = fmt.replace(',', 'X').replace('.', ',').replace('X', '.')
        if decimals == 0 or s.endswith(",00"):
            return s[:-3] if not (decimals == 0 and s.endswith(",00")) else s
        return s
    except: return "0"

# --- 📊 PİYASA VERİLERİ (GÜNCEL) ---
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
    .receipt-box b, .receipt-box center, .receipt-box p, .receipt-box hr { color: #333 !important; border-color: #333 !important; }
    </style>""", unsafe_allow_html=True)

if 'd_val' not in st.session_state: st.session_state.update({'d_val': 35, 'g_val': 55, 'k_val': 65, 'u_val': 45})

# --- 🛰️ ÜST BAŞLIK VE AÇIKLAMA (RESİM 9'DAN DÜZELTİLDİ) ---
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
    
    st.write("🔮 **Senaryo Seç (RESİM 4'DEN İYİMSER VE ENAG GERİ GELDİ)**")
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
reel_deger = round(1000/(1+res_total/100), 2)

with col_out:
    # --- 1. FOTOĞRAF ESKİ DÜZENİ VE 5. FOTOĞRAF EKMEK ÖRNEĞİ (RESİM 1 VE RESİM 5'DEN) ---
    st.markdown(f"""<div class="ozet-panel"><h3>Yıl Sonu Beklenti Analizi</h3><div style="display:flex; justify-content: space-around; align-items:center;"><div><small>Q1 Gerçekleşen</small><br><b style="font-size:24px; color:#00d4ff;">%{tr_format(Q1_ENF)}</b></div><div style="font-size:30px; color:#555;">+</div><div><small>Senin Tahminin</small><br><b style="font-size:24px; color:#ffbd45;">%{tr_format(s_enf)}</b></div><div style="font-size:30px; color:#555;">=</div><div><small><b>Yıl Sonu Toplamı</b></small><br><b style="font-size:36px; color:#ff4b4b;">%{tr_format(res_total)}</b></div></div><hr style="border:0.5px solid #333;"><p>Tahmini Kur: <b>{tr_format(tahmini_kur)} TL</b></p><p style="font-size:14px; color:#aaa; margin-top:10px;">Yani basitçe anlatmak gerekirse, yıl başında 100 TL'ye aldığın bir ekmek sepeti, yıl sonunda tam olarak {100*(1+res_total/100):,.0f} TL olacak.</p></div>""", unsafe_allow_html=True)
    
    # --- 2. FOTOĞRAF 1000 TL REEL DEĞERİ (RESİM 2'DEN) ---
    h1, h2, h3 = st.columns(3)
    with h1: st.metric("🎮 PS5 (2026)", f"{tr_format(P_PS5*(1+res_total/85), 0)} TL"); st.markdown(f'<p class="bugun-etiket">Bugün: {tr_format(P_PS5, 0)} TL</p>', unsafe_allow_html=True)
    with h2: st.metric("📱 iPhone (2026)", f"{tr_format(P_IPHONE*(1+res_total/95), 0)} TL"); st.markdown(f'<p class="bugun-etiket">Bugün: {tr_format(P_IPHONE, 0)} TL</p>', unsafe_allow_html=True)
    with h3: st.metric("🚗 Clio (2026)", f"{tr_format(P_CLIO*(1+res_total/100), 0)} TL"); st.markdown(f'<p class="bugun-etiket">Bugün: 1.795.000 TL</p>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: st.metric("🏠 Kira (Tahmini)", f"{u_salary*0.35*(1+k_a/100):,.0f} TL"); st.markdown('<p class="bugun-etiket">Kira Sepetin</p>', unsafe_allow_html=True)
    with c2: st.metric("💰 1.000 TL Reel Değeri (2026 Sonunda)", f"{reel_deger:,.0f} TL"); st.markdown(f'<p class="bugun-etiket">Bugün 1.000 TL</p>', unsafe_allow_html=True)
    
    st.divider()
    # --- ALIM GÜCÜ KADRANI (RESİM 6'DAN) ---
    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=alim_kaybi, title={'text': "Alım Gücü Kaybı (%)"}, gauge={'bar': {'color': "#ff4b4b"}})).update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}), use_container_width=True)

st.divider()

# --- 🕰️ ZAMAN MAKİNESİ VE ASGARİ ÜCRET GRAFİKLERİ GERİ GELDİ (DEDİKLERİNDEN) ---
st.subheader("🕰️ Zaman Makinesi: Asgari Ücretin Erimesi")
yillar = [str(y) for y in range(2000, 2026)]; altin = [24.5, 11.2, 12.5, 13.1, 17.8, 18.2, 15.1, 14.8, 14.1, 11.8, 10.5, 8.5, 8.0, 9.5, 10.5, 10.1, 10.4, 9.6, 7.5, 7.8, 5.1, 5.6, 5.3, 6.5, 6.8, 4.5]
dolar = [126, 92, 115, 150, 222, 261, 265, 315, 385, 352, 395, 393, 410, 420, 406, 365, 430, 385, 330, 355, 330, 315, 330, 430, 520, 485]
df_nost = pd.DataFrame({"Yıl": yillar, "Gram Altın": altin, "Dolar ($)": dolar})
g1, g2 = st.columns(2)
with g1: st.plotly_chart(px.bar(df_nost, x="Yıl", y="Gram Altın", title="Maaş Kaç Gram Altın?", color="Gram Altın", color_continuous_scale="YlOrBr"), use_container_width=True)
with g2: st.plotly_chart(px.bar(df_nost, x="Yıl", y="Dolar ($)", title="Maaş Kaç Dolar?", color="Dolar ($)", color_continuous_scale="Greens"), use_container_width=True)

# --- 💾 KAYIT ---
if st.button("💾 ANALİZİ KAYDET VE GELECEK ADİSYONUNU AL", use_container_width=True):
    def f_tr(val): return f"'{val:.2f}".replace(".", ",")
    
    kayit_id = str(uuid.uuid4().hex[:8]).upper()
    zaman_damgasi = datetime.now().strftime("%d.%m.%Y %H:%M")
    v = [zaman_damgasi, u_name, u_gender, f_tr(u_salary), u_prof, u_city, kayit_id, f_tr(s_enf), f_tr(res_total), f_tr(tahmini_kur), f_tr(alim_kaybi), f_tr(reel_deger)]
    
    if save_to_sheets(v):
        st.balloons()
        # --- 4. FOTOĞRAF ADİSYON ESKİ DÜZENİ VE REEL DEĞER (RESİM 8 VE RESİM 2'DEN) ---
        st.markdown(f"""<div class="receipt-box"><center>🧾 <b>LiraPulse ADİSYON</b></center><hr><p><b>Analist:</b> {u_name}</p><p><b>ID:</b> {kayit_id}</p><p><b>Yıl Sonu Enflasyon:</b> %{tr_format(res_total)}</p><p><b>Dolar Beklentisi:</b> {tr_format(tahmini_kur)} TL</p><p><b>1.000 TL Reel Değer:</b> {tr_format(reel_deger)} TL</p><hr><center><i>Veri Google Sheets'e Mermi Gibi İşlendi.</i></center></div>""", unsafe_allow_html=True)

# --- 🔐 ADMIN PANELİ VE 3. FOTOĞRAF PASTA GRAFİKLERİ (RESİM 7 VE RESİM 3'DEN) ---
if 'admin_data' not in st.session_state: st.session_state['admin_data'] = []

with st.expander("🔐 Admin Control Center"):
    if st.text_input("Şifre:", type="password", key="adm_pw") == "alper2026":
        if st.button("🔄 Verileri Excel'den Tazele (Geçmişi Çek)"):
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
                            "Tarih": row[0] if len(row) > 0 else "", "Analist": row[1] if len(row) > 1 else "",
                            "Cinsiyet": row[2] if len(row) > 2 else "", "Maas": clean_num(row[3]) if len(row) > 3 else 0.0,
                            "Profil": row[4] if len(row) > 4 else "", "Sehir": row[5] if len(row) > 5 else "",
                            "Kayit_ID": str(row[6]).strip() if len(row) > 6 else "", "Enflasyon": clean_num(row[8]) if len(row) > 8 else 0.0,
                            "Dolar": clean_num(row[9]) if len(row) > 9 else 0.0, "Reel_Kalan_TL": clean_num(row[11]) if len(row) > 11 else 0.0
                        })
                    st.session_state['admin_data'] = clean_data
                    st.success("Excel mermi gibi çekildi!")
                else: st.info("Excel boş.")
            except Exception as e: st.error(f"Hata: {e}")

        if len(st.session_state['admin_data']) > 0:
            df_admin = pd.DataFrame(st.session_state['admin_data'])
            st.write("### 📈 Sokağın Röntgenti (Admin Panel Özet)")
            
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Toplam Katılım", f"{len(df_admin)} Kişi")
            s2.metric("Ort. Maaş", f"{tr_format(df_admin['Maas'].mean())} TL")
            s3.metric("Ort. Enflasyon", f"%{tr_format(df_admin['Enflasyon'].mean())}")
            s4.metric("Ort. Dolar", f"{tr_format(df_admin['Dolar'].mean())} TL")
            
            # --- 3. FOTOĞRAF PASTA GRAFİKLERİ GERİ GELDİ (RESİM 3'DEN) ---
            g_col1, g_col2, g_col3 = st.columns(3)
            with g_col1: st.plotly_chart(px.pie(df_admin, names='Cinsiyet', title="Cinsiyet Dağılımı", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu), use_container_width=True)
            with g_col2: st.plotly_chart(px.pie(df_admin, names='Sehir', title="Şehir Dağılımı", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues), use_container_width=True)
            with g_col3: st.plotly_chart(px.pie(df_admin, names='Profil', title="Harcama Sepeti (Profil)", hole=0.4, color_discrete_sequence=px.colors.sequential.Greens), use_container_width=True)
            
            st.divider()
            df_edit = df_admin.copy(); df_edit.insert(0, "Seç", False)
            edited_df = st.data_editor(df_edit, column_config={"Seç": st.column_config.CheckboxColumn("Sil?", default=False), "Maas": st.column_config.NumberColumn("Maaş", format="%.0f"), "Reel_Kalan_TL": st.column_config.NumberColumn("1000TL Reel", format="%.2f")}, use_container_width=True, hide_index=True)
            
            if st.button("🗑️ SEÇİLENLERİ EXCEL'DEN SİL"):
                try:
                    secilen_idler = edited_df[edited_df["Seç"] == True]["Kayit_ID"].dropna().tolist()
                    if secilen_idler:
                        client = get_gspread_client(); sheet = client.open("LiraPulse_Veri").sheet1; all_vals = sheet.get_all_values()
                        rows_to_del = [i+1 for i, r in enumerate(all_vals) if len(r) > 6 and str(r[6]).strip() in secilen_idler]
                        for r_num in sorted(rows_to_del, reverse=True): sheet.delete_rows(r_num)
                        st.success(f"{len(rows_to_del)} veri silindi!"); st.session_state['admin_data'] = []; st.rerun()
                except Exception as e: st.error(f"Hata: {e}")
