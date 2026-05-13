import os
from groq import Groq

def generate_report(stats, outliers, corr_matrix, language="Türkçe"):
    
    rows, cols = stats['shape']
    missing_cols = {k: v for k, v in stats['missing'].items() if v > 0}
    duplicates = stats['duplicates']
    
    outlier_summary = []
    for col, info in outliers.items():
        if info['count'] > 0:
            outlier_summary.append(f"{col}: {info['count']} aykiri deger (%{info['percentage']})")
    
    corr_summary = []
    if corr_matrix is not None:
        cols_list = corr_matrix.columns.tolist()
        for i in range(len(cols_list)):
            for j in range(i+1, len(cols_list)):
                val = corr_matrix.iloc[i, j]
                if abs(val) > 0.5:
                    corr_summary.append(f"{cols_list[i]} & {cols_list[j]}: {val}")

    if language == "English":
        prompt = f"""You are a data analyst assistant. Analyze the following dataset statistics and write a professional report in ENGLISH ONLY.

DATASET INFO:
- Rows: {rows}
- Columns: {cols}
- Column names: {list(stats['dtypes'].keys())}
- Missing values: {missing_cols if missing_cols else 'None'}
- Duplicate rows: {duplicates}
- Outliers: {outlier_summary if outlier_summary else 'None detected'}
- Strong correlations: {corr_summary if corr_summary else 'None detected'}

Write a report with these sections:
1. Dataset Overview
2. Data Quality Assessment
3. Key Findings
4. Recommendations

IMPORTANT: Write ONLY in English. Use Markdown format."""
    else:
        prompt = f"""Sen bir veri analisti asistanisin. Asagidaki veri seti istatistiklerini analiz et ve Turkce dilinde profesyonel bir rapor yaz.

VERI SETI BILGILERI:
- Satir sayisi: {rows}
- Sutun sayisi: {cols}
- Sutunlar: {list(stats['dtypes'].keys())}
- Eksik deger olan sutunlar: {missing_cols if missing_cols else 'Yok'}
- Yinelenen satir sayisi: {duplicates}
- Aykiri degerler: {outlier_summary if outlier_summary else 'Tespit edilmedi'}
- Guclu korelasyonlar: {corr_summary if corr_summary else 'Tespit edilmedi'}

Lutfen sunlari iceren bir rapor yaz:
1. Veri setine genel bakis
2. Veri kalitesi degerlendirmesi
3. One cikan bulgular
4. Oneriler

Rapor profesyonel Turkce olsun. Markdown formatinda yaz."""

    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return "⚠️ GROQ_API_KEY bulunamadı! .env dosyasını kontrol et."
        
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"⚠️ Hata: {str(e)}"