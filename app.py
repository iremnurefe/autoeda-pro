from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import pandas as pd
import numpy as np
from eda.analyzer import load_data, basic_stats, detect_outliers, correlation_matrix, clean_data, fix_dtypes, feature_importance, data_quality_score, detect_time_series
from eda.visualizer import plot_distributions, plot_correlation_heatmap, plot_missing_values, plot_outliers, plot_categorical, plot_scatter, plot_pie, plot_feature_importance
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
    st.markdown("**Nasıl Kullanılır?**")
    st.markdown("1. CSV dosyanı yükle")
    st.markdown("2. Analizi incele")
    st.markdown("3. AI raporu üret")
    st.markdown("4. PDF olarak indir")

# Dosya yükleme
uploaded_file = st.file_uploader(
    "📂 CSV veya Excel dosyanı yükle",
    type=["csv", "xlsx", "xls"],
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📈 Genel İstatistikler",
    "📊 Dağılımlar",
    "🔥 Korelasyon",
    "⚠️ Outlier & Eksik",
    "🤖 AI Raporu",
    "🧹 Veri Temizleme",
    "🎯 Feature Importance",
    "🏆 Kalite Skoru",
    "📅 Zaman Serisi"
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
        st.markdown("---")
        st.subheader("🔵 Scatter Plot")
        numeric_cols_list = df.select_dtypes(include=np.number).columns.tolist()
        cat_cols_list = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(numeric_cols_list) >= 2:
            col1, col2, col3 = st.columns(3)
            with col1:
                scatter_x = st.selectbox("X ekseni", numeric_cols_list, key="scatter_x")
            with col2:
                scatter_y = st.selectbox("Y ekseni", numeric_cols_list, index=1, key="scatter_y")
            with col3:
                scatter_color = st.selectbox("Renk (opsiyonel)", ["Yok"] + cat_cols_list, key="scatter_color")
            
            scatter_fig = plot_scatter(df, scatter_x, scatter_y, scatter_color)
            st.plotly_chart(scatter_fig, use_container_width=True)
        else:
            st.info("Scatter plot için en az 2 sayısal sütun gerekli.")
        
        st.markdown("---")
        st.subheader("🥧 Pasta Grafik")
        if cat_cols_list:
            pie_col = st.selectbox("Sütun seç", cat_cols_list, key="pie_col")
            pie_fig = plot_pie(df, pie_col)
            st.plotly_chart(pie_fig, use_container_width=True)
        else:
            st.info("Pasta grafik için kategorik sütun gerekli.")    
    
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
        
        report_lang = st.selectbox("Rapor dilini seç", ["English", "Türkçe"], key="report_lang")
        if st.button("🚀 Rapor Üret", type="primary"):
            with st.spinner("AI raporu yazıyor... (1-2 dakika sürebilir)"):
                report = generate_report(stats, outliers, corr, report_lang)
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

# TAB 6 — Veri Temizleme
    with tab6:
        st.subheader("🧹 Veri Temizleme & Düzenleme")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Eksik Değer Doldurma Yöntemi**")
            fill_method = st.selectbox(
                "Yöntem seç",
                ["Mean (Ortalama)", "Median (Medyan)", "Mode (Mod)", "Sıfır (0)", "Sil (Drop Rows)"]
            )
        
        with col2:
            st.markdown("**Silinecek Sütunlar**")
            columns_to_drop = st.multiselect(
                "Sütun seç (boş bırakabilirsin)",
                options=df.columns.tolist()
            )
        
        st.markdown("---")
        
        fix_types = st.checkbox("🔧 Veri tiplerini otomatik düzelt (tarih, sayı tespiti)")
        
        if st.button("🧹 Temizle & Uygula", type="primary"):
            with st.spinner("Temizleniyor..."):
                cleaned_df = clean_data(df, fill_method, columns_to_drop)
                if fix_types:
                    cleaned_df = fix_dtypes(cleaned_df)
            
            st.success(f"✅ Temizlendi! {df.shape[0] - cleaned_df.shape[0]} satır, {df.shape[1] - cleaned_df.shape[1]} sütun kaldırıldı.")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Öncesi**")
                st.dataframe(df.head(), use_container_width=True)
            with col2:
                st.markdown("**Sonrası**")
                st.dataframe(cleaned_df.head(), use_container_width=True)
            
            # CSV olarak indir
            st.markdown("---")
            csv = cleaned_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Temizlenmiş Veriyi İndir (CSV)",
                data=csv,
                file_name="cleaned_data.csv",
                mime="text/csv",
                type="primary"
            )

# TAB 7 — Feature Importance
    with tab7:
        st.subheader("🎯 Feature Importance — Hangi Sütun Daha Etkili?")
        st.info("Bir hedef sütun seç, diğer sütunların ona etkisini görelim.")
        
        target = st.selectbox(
            "Hedef sütun seç",
            options=df.columns.tolist(),
            key="target_col"
        )
        
        if st.button("🎯 Analiz Et", type="primary"):
            with st.spinner("Model eğitiliyor..."):
                importance_df, task = feature_importance(df, target)
            
            if importance_df is not None:
                st.success(f"✅ Görev tipi: **{'Sınıflandırma' if task == 'classification' else 'Regresyon'}**")
                fig = plot_feature_importance(importance_df)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("**Önem Skorları Tablosu**")
                st.dataframe(importance_df, use_container_width=True)
            else:
                st.error(task)

# TAB 8 — Veri Kalite Skoru
    with tab8:
        st.subheader("🏆 Veri Kalite Skoru")
        
        with st.spinner("Kalite skoru hesaplanıyor..."):
            quality = data_quality_score(df)
        
        # Büyük skor göstergesi
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style='text-align: center; padding: 30px; border-radius: 15px; 
                        background: linear-gradient(135deg, #1e1e2e, #2e2e4e);
                        border: 3px solid {'#00ff88' if quality['score'] >= 80 else '#ff8800' if quality['score'] >= 60 else '#ff4444'}'>
                <h1 style='font-size: 80px; margin: 0; color: {'#00ff88' if quality['score'] >= 80 else '#ff8800' if quality['score'] >= 60 else '#ff4444'}'>{quality['score']}</h1>
                <h2 style='color: white; margin: 0'>/ 100</h2>
                <h1 style='font-size: 60px; margin: 10px 0; color: {'#00ff88' if quality['score'] >= 80 else '#ff8800' if quality['score'] >= 60 else '#ff4444'}'>Not: {quality['grade']}</h1>
                <p style='color: #aaa; font-size: 18px'>{quality['comment']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📋 Puan Detayları")
        for detail in quality['details']:
            st.markdown(detail)
        
        st.markdown("---")
        st.info("💡 Puanını artırmak için **Veri Temizleme** sekmesini kullan!")  

    # TAB 9 — Zaman Serisi
    with tab9:
        st.subheader("📅 Zaman Serisi Analizi")
        
        date_cols = detect_time_series(df)
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        
        if date_cols:
            col1, col2 = st.columns(2)
            with col1:
                date_col = st.selectbox("Tarih sütunu seç", date_cols, key="date_col")
            with col2:
                value_col = st.selectbox("Değer sütunu seç", numeric_cols, key="value_col")
            
            fig = plot_time_series(df, date_col, value_col)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📅 Veri setinde tarih sütunu tespit edilemedi. Tarih içeren bir CSV yükle!")
            st.markdown("""
            **Desteklenen tarih formatları:**
            - `2024-01-15`
            - `15/01/2024`
            - `January 15, 2024`
            """)              
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
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📊 7 Analiz Sekmesi")
        st.markdown("İstatistik, dağılım, korelasyon, outlier, AI raporu, veri temizleme, feature importance")
    with col2:
        st.markdown("### 🤖 AI Destekli")
        st.markdown("Groq API ile Llama 3.1 — saniyeler içinde Türkçe veya İngilizce profesyonel rapor")
    with col3:
        st.markdown("### 📄 PDF Export")
        st.markdown("Tüm analizi tek tıkla profesyonel PDF raporu olarak indir")