import streamlit as st
import pandas as pd
from eda.analyzer import load_data, basic_stats, detect_outliers, correlation_matrix
from eda.visualizer import plot_distributions, plot_correlation_heatmap, plot_missing_values, plot_outliers, plot_categorical
from eda.reporter import generate_report
from export.pdf_exporter import create_pdf_report

st.set_page_config(
    page_title="AutoEDA Pro",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AutoEDA Pro")
st.markdown("**Otomatik Keşifsel Veri Analizi & Rapor Üretici**")
st.markdown("---")

# Sol panel ayarlar
with st.sidebar:
    st.header("⚙️ Ayarlar")
    language = st.selectbox("Rapor Dili", ["Türkçe", "English"])
    st.markdown("---")
    st.markdown("**Nasıl Kullanılır?**")
    st.markdown("1. CSV dosyanı yükle")
    st.markdown("2. Analizi incele")
    st.markdown("3. AI raporu üret")
    st.markdown("4. PDF olarak indir")

# Dosya yükleme
uploaded_file = st.file_uploader(
    "📂 CSV dosyanı yükle",
    type=["csv"],
    help="Maksimum 200MB"
)

if uploaded_file is not None:
    # Veriyi yükle
    with st.spinner("Veri yükleniyor..."):
        df = load_data(uploaded_file)
    
    st.success(f"✅ Dosya yüklendi! {df.shape[0]} satır, {df.shape[1]} sütun")
    
    # Veri önizleme
    with st.expander("🔍 Veri Önizleme (İlk 5 Satır)", expanded=True):
        st.dataframe(df.head(), use_container_width=True)
    
    # Analiz yap
    with st.spinner("Analiz yapılıyor..."):
        stats = basic_stats(df)
        outliers = detect_outliers(df)
        corr = correlation_matrix(df)
    
    # Tab yapısı
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Genel İstatistikler",
        "📊 Dağılımlar",
        "🔥 Korelasyon",
        "⚠️ Outlier & Eksik",
        "🤖 AI Raporu"
    ])
    
    # TAB 1 — Genel İstatistikler
    with tab1:
        st.subheader("Genel Bilgiler")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Satır", stats['shape'][0])
        col2.metric("Sütun", stats['shape'][1])
        col3.metric("Yinelenen Satır", stats['duplicates'])
        col4.metric("Eksik Değerli Sütun", sum(1 for v in stats['missing'].values() if v > 0))
        
        st.markdown("---")
        st.subheader("Tanımlayıcı İstatistikler")
        if stats['describe']:
            st.dataframe(pd.DataFrame(stats['describe']).round(2), use_container_width=True)
        
        st.markdown("---")
        st.subheader("Sütun Bilgileri")
        col_info = pd.DataFrame({
            'Veri Tipi': stats['dtypes'],
            'Eksik Sayısı': stats['missing'],
            'Eksik Yüzdesi (%)': stats['missing_pct']
        })
        st.dataframe(col_info, use_container_width=True)
    
    # TAB 2 — Dağılımlar
    with tab2:
        st.subheader("Sayısal Sütun Dağılımları")
        dist_figs = plot_distributions(df)
        if dist_figs:
            for col_name, fig in dist_figs:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sayısal sütun bulunamadı.")
        
        st.subheader("Kategorik Sütun Dağılımları")
        cat_figs = plot_categorical(df)
        if cat_figs:
            for col_name, fig in cat_figs:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Kategorik sütun bulunamadı.")
    
    # TAB 3 — Korelasyon
    with tab3:
        st.subheader("Korelasyon Matrisi")
        corr_fig = plot_correlation_heatmap(corr)
        if corr_fig:
            st.plotly_chart(corr_fig, use_container_width=True)
            st.markdown("**Yorum:** 1'e yakın = güçlü pozitif ilişki, -1'e yakın = güçlü negatif ilişki, 0'a yakın = ilişki yok")
        else:
            st.info("Korelasyon için en az 2 sayısal sütun gerekli.")
    
    # TAB 4 — Outlier & Eksik
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⚠️ Aykırı Değerler")
            outlier_fig = plot_outliers(outliers)
            if outlier_fig:
                st.plotly_chart(outlier_fig, use_container_width=True)
            else:
                st.info("Aykırı değer tespit edilmedi.")
        
        with col2:
            st.subheader("❓ Eksik Değerler")
            missing_fig = plot_missing_values(df)
            if missing_fig:
                st.plotly_chart(missing_fig, use_container_width=True)
            else:
                st.success("Eksik değer yok! ✅")
    
    # TAB 5 — AI Raporu
    with tab5:
        st.subheader("🤖 AI Destekli Otomatik Rapor")
        st.info("Rapor üretmek için aşağıdaki butona tıkla. Ollama'nın çalışıyor olması gerekiyor.")
        
        if st.button("🚀 Rapor Üret", type="primary"):
            with st.spinner("AI raporu yazıyor... (1-2 dakika sürebilir)"):
                report = generate_report(stats, outliers, corr, language)
            st.markdown(report)
            
            # PDF Export
            st.markdown("---")
            st.subheader("📥 PDF İndir")
            with st.spinner("PDF hazırlanıyor..."):
                pdf_buffer = create_pdf_report(stats, outliers, report)
            
            st.download_button(
                label="📄 PDF Raporu İndir",
                data=pdf_buffer,
                file_name="autoeda_raporu.pdf",
                mime="application/pdf",
                type="primary"
            )

else:
    # Dosya yüklenmemişse hoşgeldin ekranı
    st.markdown("""
    ## 👋 Hoş Geldin!
    
    **AutoEDA Pro** ile CSV dosyanı yükle, saniyeler içinde:
    
    - 📈 **Otomatik istatistikler** — ortalama, medyan, std ve daha fazlası
    - 📊 **İnteraktif grafikler** — dağılım, korelasyon, kategorik analizler  
    - ⚠️ **Outlier & eksik değer tespiti** — IQR yöntemiyle
    - 🤖 **AI destekli yorum** — Türkçe veya İngilizce otomatik rapor
    - 📄 **PDF export** — tek tıkla profesyonel rapor
    
    **Başlamak için sol üstten CSV dosyanı yükle!** ⬆️
    """)
    
    st.markdown("---")
    st.markdown("*Test için örnek CSV dosyası yükleyebilirsin.*")