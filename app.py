# ... (Üstteki tüm kodlar aynı kalıyor, sadece buton kısmını bul ve değiştir)

with btn_col2:
    # Yüzde işareti için URL uyumlu '%25' kodunu kullanıyoruz
    tweet_text = f"LiraPulse ile 2026 sonu enflasyon beklentimi %{res_total:.2f} olarak hesapladım! 📈 Maaşım ne kadar eriyor? Hemen gör: https://huspevhztwxasrstrhne7z.streamlit.app"
    
    # URL içindeki % işaretini %25 olarak değiştiriyoruz ki Twitter doğru algılasın
    import urllib.parse
    encoded_tweet = urllib.parse.quote(tweet_text)
    
    twitter_url = f"https://twitter.com/intent/tweet?text={encoded_tweet}"
    st.markdown(f'<a href="{twitter_url}" target="_blank"><button style="width:100%; height:40px; background-color:#1DA1F2; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">🐦 SONUCU TWITTER\'DA PAYLAŞ</button></a>', unsafe_allow_html=True)
