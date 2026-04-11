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

# --- 📊 PİYASA VERİLERİ ---
GUNCEL_DOLAR, Q1_ENF, TCMB_FAIZ, TCMB_2026_HEDEF = 44.92, 14.40, 37.0, 22.0
P_PS5, P_IPHONE, P_CLIO = 42999, 77999, 1795000

st.set_page_config(page_title="LiraPulse: Gelecek Analizi", layout="wide")

# --- 🎨 CSS: TASARIM KORUMASI ---
st.markdown("""<style>
    .main { background-color: #0d1117; }
    [data-testid="stMetric"] { background-color: #161b22; padding: 15px !important; border-radius: 15px; border-left: 5px solid #00d4ff; }
    .ozet-panel { background: linear-gradient(145deg, #1e1e26, #252532); padding: 25px; border-radius: 15px; border: 1px solid #30363d; text-align: center; }
    .bugun-etiket { color: #ffbd45; font-size: 13px; text-align: center; margin-top: -10px; font-weight: bold; }
    .ekmek-text { color: #ffbd45; font-size: 14px; font-weight: bold; margin-bottom: 20px; }
    .receipt-box { background-color: #fff; color: #333 !important; padding: 30px; border-radius: 10px; font-family: 'Courier New', monospace; border: 3px dashed #333; margin: 20px auto; max-width: 500px; line-height: 1.8; text-align: left; }
    .receipt-box b, .receipt-box center, .receipt-box p, .receipt-box hr { color: #333 !important; border-color: #333 !important; }
    </style>""", unsafe_allow_html=True)

if 'd_val' not in st.session_state: st.session_state.update({'d_val': 35, 'g_val': 55, 'k_val': 65, 'u_val': 45})

# --- 🍞 ÜST BAŞLIK VE EKMEK ÖRNEĞİ ---
st.markdown('<p class="ekmek-text">💡 Enflasyon Nedir?<br>Bugün 100 liraya aldığın 10 ekmeğin, seneye aynı parayla sadece 6 tanesini alabilmendir.</p>', unsafe_allow_html=True)

# --- 📈 4'LÜ TEPE METRİKLERİ ---
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
    with c_col1: u_gender = st.selectbox("Cinsiyet:", ["Erkek", "Kadın", "Belirtmek İstemiyorum"])
    with c_col2: u_salary = st.number_input("Aylık Maaş (TL):", value=22102)
    
    u_city = st.selectbox("Şehir:", ["Kırklareli", "İstanbul", "Ankara", "İzmir", "Diğer"])
    u_prof = st.selectbox("Harcama Sepeti:", ["Öğrenci", "Mavi Yaka", "Beyaz Yaka", "Emekli", "Kamu Personeli"])
    
    st.write("🔮 **Hızlı Senaryo Seçimi**")
    s1, s2, s3, s4, s5, s6 = st.columns(6)
    if s1.button("🏦 TCMB"): st.session_state.update({'d_val': 5, 'g_val': 8, 'k_val': 7, 'u_val': 6}); st.rerun()
    if s2.button("🌸 İyimser"): st.session_state.update({'d_val': 20, 'g_val': 32, 'k_val': 30, 'u_val': 28}); st.rerun()
    if s3.button("📉 TÜİK"): st.session_state.update({'d_val': 12, 'g_val': 22, 'k_val': 20, 'u_val': 16}); st.rerun()
    if s4.button("📊 Realist"): st.session_state.update({'d_val': 35, 'g_val': 48, 'k_val': 50, 'u_val': 42}); st.rerun()
    if s5.button("🔥 ENAG"): st.session_state.update({'d_val': 55, 'g_val': 70, 'k_val': 75, 'u_val': 60}); st.rerun()
    if s6.button("🌋 Kriz"): st.session_state.update({'d_val': 100, 'g_val': 120, 'k_val': 130, 'u_val': 110}); st.rerun()
    
    st.divider()
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
    # --- YIL SONU ANALİZİ ---
    st.markdown(f"""<div class="ozet-panel">
        <h3 style="color:#aaa; margin-bottom: 20px;">Yıl Sonu Beklenti Analizi</h3>
        <div style="display:flex; justify-content: space-around; align-items:center; margin-bottom: 15px;">
            <div><small style="color:#ccc;">Q1 Gerçekleşen</small><br><b style="font-size:24px; color:#00d4ff;">%{tr_format(Q1_ENF)}</b></div>
            <div style="font-size:30px; color:#555;">+</div>
            <div><small style="color:#ccc;">Senin Tahminin</small><br><b style="font-size:24px; color:#ffbd45;">%{tr_format(s_enf)}</b></div>
            <div style="font-size:30px; color:#555;">=</div>
            <div><small style="color:#ccc;"><b>Yıl Sonu Toplamı</b></small><br><b style="font-size:36px; color:#ff4b4b;">%{tr_format(res_total)}</b></div>
        </div>
        <hr style="border:0.5px solid #333;">
        <p style="font-size:16px; color:#ccc; margin-top:10px;">Tahmini Kur: <b>{tr_format(tahmini_kur)} TL</b></p>
    </div>""", unsafe_allow_html=True)
    
    st.write("") 
    
    h1, h2, h3 = st.columns(3)
    with h1: st.metric("🎮 PS5 (2026)", f"{tr_format(P_PS5*(1+res_total/85), 0)} TL"); st.markdown(f'<p class="bugun-etiket">Bugün: {tr_format(P_PS5, 0)} TL</p>', unsafe_allow_html=True)
    with h2: st.metric("📱 iPhone (2026)", f"{tr_format(P_IPHONE*(1+res_total/95), 0)} TL"); st.markdown(f'<p class="bugun-etiket">Bugün: {tr_format(P_IPHONE, 0)} TL</p>', unsafe_allow_html=True)
    with h3: st.metric("🚗 Clio (2026)", f"{tr_format(P_CLIO*(1+res_total/100), 0)} TL"); st.markdown(f'<p class="bugun-etiket">Bugün: 1.795.000 TL</p>', unsafe_allow_html=True)
    
    st.divider()
    
    c_g, c_e = st.columns(2)
    with c_g: 
        st.plotly_chart(go.Figure(go.Indicator(
            mode="gauge+number", 
            value=alim_kaybi, 
            title={'text': "Alım Gücü Kaybı (%)", 'font': {'size': 16}}, 
            gauge={'bar': {'color': "#ff4b4b"}}
        )).update_layout(height=250, margin=dict(l=30, r=30, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}), use_container_width=True)
    
    with c_e: 
        yuzde_kalan = max(0, min(100, (reel_deger / 1000) * 100))
        st.markdown(f"""
        <div style="background-color: #161b22; padding: 30px 25px; border-radius: 10px; border: 1px solid #30363d; margin-top: 10px;">
            <p style="color: #aaa; font-size: 14px; margin-bottom: 5px; font-weight: bold;">📉 1.000 TL Akıbeti</p>
            <h2 style="color: #fff; margin-top: 0; margin-bottom: 20px; font-size: 36px;">{tr_format(reel_deger)} TL</h2>
            <div style="height: 10px; background-color: #252532; border-radius: 5px; width: 100%;">
                <div style="height: 100%; background-color: #ff4b4b; border-radius: 5px; width: {yuzde_kalan}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# --- ⚔️ YENİ BÖLÜM: YIL YIL ENFLASYON VS YATIRIM TABLOSU ---
st.subheader("⚔️ 2020-2025: Enflasyonu Yenenler ve Yenilenler")
st.markdown("<small style='color:#aaa;'>Grafikler yerine net rakamlar. Yeşil yananlar enflasyonu tokatladı, kırmızı yananlar enflasyona ezildi.</small>", unsafe_allow_html=True)

df_yatirim = pd.DataFrame({
    "Yıl": ["2020", "2021", "2022", "2023", "2024", "2025 (Tahmin)"],
    "Enflasyon (%)": [14.6, 36.0, 64.2, 64.7, 45.0, 25.0],
    "TL Mevduat (%)": [12.0, 17.0, 16.0, 35.0, 50.0, 40.0],
    "Dolar (%)": [24.0, 78.0, 40.0, 57.0, 25.0, 15.0],
    "Gram Altın (%)": [56.0, 70.0, 43.0, 78.0, 40.0, 20.0],
    "BIST 100 (%)": [29.0, 25.0, 196.0, 35.0, 45.0, 30.0]
})

# Renklendirme Motoru: Enflasyondan büyükse yeşil, küçükse kırmızı
def color_cells(row):
    enf = row["Enflasyon (%)"]
    colors = [''] * len(row)
    for i, col in enumerate(row.index):
        if col not in ["Yıl", "Enflasyon (%)"]:
            if row[col] > enf:
                colors[i] = 'color: #28a745; font-weight: bold;' # Yeşil
            elif row[col] < enf:
                colors[i] = 'color: #ff4b4b; font-weight: bold;' # Kırmızı
            else:
                colors[i] = 'color: white;'
        elif col == "Enflasyon (%)":
            colors[i] = 'color: white; font-weight: bold; background-color: rgba(255,255,255,0.05);'
        else:
            colors[i] = 'font-weight: bold;'
    return colors

# Tabloyu Formatla ve Ekrana Bas
styled_df = df_yatirim.style.apply(color_cells, axis=1).format({
    "Enflasyon (%)": "{:.1f}%",
    "TL Mevduat (%)": "{:.1f}%",
    "Dolar (%)": "{:.1f}%",
    "Gram Altın (%)": "{:.1f}%",
    "BIST 100 (%)": "{:.1f}%"
})

st.dataframe(styled_df, use_container_width=True, hide_index=True)

st.divider()

# --- 🕰️ ZAMAN MAKİNESİ ---
st.subheader("🕰️ Zaman Makinesi: Asgari Ücretin Erimesi (2000-2025)")
yillar_nost = [str(y) for y in range(2000, 2026)]; altin_nost = [24.5, 11.2, 12.5, 13.1, 17.8, 18.2, 15.1, 14.8, 14.1, 11.8, 10.5, 8.5, 8.0, 9.5, 10.5, 10.1, 10.4, 9.6, 7.5, 7.8, 5.1, 5.6, 5.3, 6.5, 6.8, 4.5]
dolar_nost = [126, 92, 115, 150, 222, 261, 265, 315, 385, 352, 395, 393, 410, 420, 406, 365, 430, 385, 330, 355, 330, 315, 330, 430, 520, 485]
df_nost = pd.DataFrame({"Yıl": yillar_nost, "Gram Altın": altin_nost, "Dolar ($)": dolar_nost})
g1, g2 = st.columns(2)
with g1: st.plotly_chart(px.bar(df_nost, x="Yıl", y="Gram Altın", title="Maaş Kaç Gram Altın?", color="Gram Altın", color_continuous_scale="Blues"), use_container_width=True)
with g2: st.plotly_chart(px.bar(df_nost, x="Yıl", y="Dolar ($)", title="Maaş Kaç Dolar?", color="Dolar ($)", color_continuous_scale="Greens"), use_container_width=True)

if st.button("💾 ANALİZİ KAYDET VE ADİSYONU AL", use_container_width=True):
    def f_tr(val):
        s = f"{val:.2f}".replace(".", ",")
        return f"'{s[:-3]}" if s.endswith(",00") else f"'{s}"
    
    kayit_id = str(uuid.uuid4().hex[:8]).upper()
    v = [datetime.now().strftime("%d.%m.%Y %H:%M"), u_name, u_gender, f_tr(u_salary), u_prof, u_city, kayit_id, f_tr(s_enf), f_tr(res_total), f_tr(tahmini_kur), f_tr(alim_kaybi), f_tr(reel_deger)]
    
    if save_to_sheets(v):
        st.balloons()
        
        t_kahvalti = 400 
        t_aksam = 600    
        
        y_kahvalti = t_kahvalti * (1 + res_total/100)
        y_aksam = t_aksam * (1 + res_total/100)
        y_toplam = y_kahvalti + y_aksam

        st.markdown(f"""
        <div style="background-color: #fff; color: #000; padding: 30px; font-family: 'Courier New', Courier, monospace; width: 100%; max-width: 480px; margin: 30px auto; border: 1px solid #ddd; box-shadow: 2px 2px 15px rgba(0,0,0,0.5);">
            <center><b>🧾 LiraPulse Intelligence ADİSYON</b></center><br>
            <p style="margin:4px 0;">TARİH: 31.12.2026</p>
            <p style="margin:4px 0;">MASA: 2026 SONU</p>
            <p style="margin:4px 0;">ANALİST: {u_name}</p>
            <p style="margin:15px 0;">-----------------------------------------</p>
            <div style="display:flex; justify-content:space-between;"><p style="margin:4px 0;">2x Serpme Kahvaltı</p><p style="margin:4px 0;">: {tr_format(y_kahvalti, 0)} TL</p></div>
            <div style="display:flex; justify-content:space-between;"><p style="margin:4px 0;">1x Akşam Yemeği (2 Kişi)</p><p style="margin:4px 0;">: {tr_format(y_aksam, 0)} TL</p></div>
            <p style="margin:15px 0;">-----------------------------------------</p>
            <div style="display:flex; justify-content:space-between;"><b style="margin:4px 0; font-size:16px;">TOPLAM (Yıl Başı: 1.000 TL)</b><b style="margin:4px 0; font-size:16px;">: {tr_format(y_toplam, 0)} TL</b></div>
            <p style="margin:15px 0;">-----------------------------------------</p><br>
            <center><i>Geleceği Görmek Cesaret İster.</i></center>
        </div>
        """, unsafe_allow_html=True)

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
                    
                    new_data = []
                    for i in range(1, len(vals)):
                        row = vals[i]
                        new_data.append({
                            "Tarih": row[0] if len(row) > 0 else "", "Analist": row[1] if len(row) > 1 else "",
                            "Cinsiyet": row[2] if len(row) > 2 else "", "Maas": clean_num(row[3]) if len(row) > 3 else 0.0,
                            "Profil": row[4] if len(row) > 4 else "", "Sehir": row[5] if len(row) > 5 else "",
                            "Kayit_ID": str(row[6]).strip() if len(row) > 6 else "", "Enflasyon": clean_num(row[8]) if len(row) > 8 else 0.0,
                            "Dolar": clean_num(row[9]) if len(row) > 9 else 0.0, "Reel": clean_num(row[11]) if len(row) > 11 else 0.0
                        })
                    st.session_state['admin_data'] = new_data
                    st.success("Veriler Excel'den çekildi!")
                else: st.info("Excel boş.")
            except Exception as e: st.error(f"Hata: {e}")

        if len(st.session_state['admin_data']) > 0:
            df = pd.DataFrame(st.session_state['admin_data'])
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Toplam Katılım", f"{len(df)} Kişi")
            s2.metric("Ort. Maaş", f"{tr_format(df['Maas'].mean())} TL")
            s3.metric("Ort. Enflasyon", f"%{tr_format(df['Enflasyon'].mean())}")
            s4.metric("Ort. Dolar", f"{tr_format(df['Dolar'].mean())} TL")
            
            if not df.empty and len(df) > 0:
                g1, g2, g3 = st.columns(3)
                with g1: st.plotly_chart(px.pie(df, names='Cinsiyet', title="Cinsiyet Dağılımı", hole=0.4), use_container_width=True)
                with g2: st.plotly_chart(px.pie(df, names='Sehir', title="Şehir Dağılımı", hole=0.4), use_container_width=True)
                with g3: st.plotly_chart(px.pie(df, names='Profil', title="Harcama Sepeti", hole=0.4), use_container_width=True)
            
            st.divider()
            df_edit = df.copy(); df_edit.insert(0, "Seç", False)
            edited_df = st.data_editor(df_edit, column_config={"Seç": st.column_config.CheckboxColumn("Sil?", default=False), "Maas": st.column_config.NumberColumn("Maaş", format="%.0f")}, use_container_width=True, hide_index=True)
            
            if st.button("🗑️ SEÇİLENLERİ SİL"):
                sec_idler = edited_df[edited_df["Seç"] == True]["Kayit_ID"].tolist()
                if sec_idler:
                    client = get_gspread_client(); sheet = client.open("LiraPulse_Veri").sheet1; all_vals = sheet.get_all_values()
                    rows_to_del = [i+1 for i, r in enumerate(all_vals) if len(r) > 6 and str(r[6]).strip() in sec_idler]
                    for r_num in sorted(rows_to_del, reverse=True): sheet.delete_rows(r_num)
                    st.success("Silindi!"); st.session_state['admin_data'] = []; st.rerun()
