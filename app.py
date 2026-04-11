# --- 🎨 CSS TASARIMI (ESKİ KARİZMAYI GERİ GETİRİYORUZ) ---
st.markdown("""<style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 15px; border-left: 5px solid #00d4ff; color: white; }
    .ozet-panel { background: linear-gradient(145deg, #1e1e26, #252532); padding: 20px; border-radius: 15px; border: 1px solid #30363d; text-align: center; color: white; }
    
    /* ADİSYON KUTUSU DÜZELTME */
    .receipt-box { 
        background-color: #f8f9fa; 
        color: #333 !important; 
        padding: 20px; 
        border-radius: 10px; 
        font-family: 'Courier New', monospace; 
        border: 2px dashed #333; 
        margin: 20px auto;
        max-width: 400px; /* Dev gibi olmasın diye sınırladık */
        line-height: 1.2;
    }
    .receipt-box b, .receipt-box center { color: #333 !important; }
    
    /* Admin Paneli Tablo Yazı Rengi */
    [data-testid="stExpander"] { color: white; }
    </style>""", unsafe_allow_html=True)

# ... (Hesaplama kısımları aynı kalsın) ...

with col_out:
    st.markdown(f"""<div class="ozet-panel"><h3>Yıl Sonu Beklenti Analizi</h3><b style="font-size:36px; color:#ff4b4b;">%{res_total:.1f}</b><br>Tahmini Kur: {tahmini_kur:.2f} TL</div>""", unsafe_allow_html=True)
    
    if st.button("💾 ANALİZİ KAYDET VE FİŞ AL", use_container_width=True):
        tarih = datetime.now().strftime("%d.%m.%Y %H:%M")
        veri = [tarih, u_name, "", u_salary, u_prof, u_city, "0.0.0.0", slider_enf, res_total, tahmini_kur, alim_kaybi, 1000/(1+res_total/100)]
        
        if save_to_sheets(veri):
            st.balloons()
            # ŞIK VE KÜÇÜK ADİSYON TASARIMI
            st.markdown(f"""
            <div class="receipt-box">
                <center>🧾 <b>LiraPulse ADİSYON</b></center>
                <hr style="border: 0.5px solid #333;">
                <b>Analist:</b> {u_name}<br>
                <b>Şehir:</b> {u_city}<br>
                <b>Enflasyon Tahmini:</b> %{res_total:.1f}<br>
                <b>Dolar Kuru:</b> {tahmini_kur:.2f} TL<br>
                <hr style="border: 0.5px dashed #333;">
                <center><i>Veri Buluta Başarıyla İşlendi.</i></center>
            </div>
            """, unsafe_allow_html=True)
