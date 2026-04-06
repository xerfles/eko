# --- 🎨 CSS (TAM RESPONSIVE GÜNCELLEME) ---
st.markdown("""
    <style>
    /* Ana Konteyner Ayarları */
    .main { padding: 10px !important; }
    
    /* Metrik Kartları Güzelleştirme */
    [data-testid="stMetric"] {
        background-color: #161b22; 
        padding: 15px !important; 
        border-radius: 15px; 
        border-left: 5px solid #00d4ff;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    /* Özet Panel (Hesaplama Alanı) */
    .ozet-panel { 
        background: linear-gradient(145deg, #1e1e26, #252532); 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #30363d; 
        text-align: center; 
        margin-bottom: 20px;
    }

    /* Bugün Etiketi (Senin istediğin sarı yazılar) */
    .bugun-etiket { 
        color: #ffbd45; 
        font-size: clamp(12px, 2vw, 14px); /* Ekrana göre küçülür/büyür */
        text-align: center; 
        margin-top: -5px; 
        font-weight: bold; 
    }

    /* Enflasyon Tanım Kutusu */
    .inf-box { 
        background-color: #161b22; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #ff4b4b; 
        margin-top: 10px; 
        margin-bottom: 20px; 
        font-size: clamp(14px, 1.5vw, 16px);
    }

    /* Adisyon (Fiş) Görünümü */
    .receipt-box { 
        background-color: #fff; 
        color: #333; 
        padding: clamp(15px, 5vw, 30px); 
        border-radius: 5px; 
        font-family: 'Courier New', monospace; 
        border: 2px dashed #333; 
        margin-top: 20px;
        width: 100%;
        max-width: 500px; /* Mobilde taşmasın diye */
        margin-left: auto;
        margin-right: auto;
    }

    /* Slider ve Giriş Alanlarını Mobilde Sıkıştır */
    .stSlider, .stSelectbox, .stTextInput {
        margin-bottom: 10px !important;
    }

    /* Responsive Kolon Ayarları (Streamlit zaten otomatik yapar ama biz destekliyoruz) */
    @media (max-width: 768px) {
        .ozet-panel b { font-size: 24px !important; }
        h1 { font-size: 28px !important; }
    }
    </style>
    """, unsafe_allow_html=True)
