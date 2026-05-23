import os
from groq import Groq

TEMPLATES = {
    "Genel": {
        "tr": "",
        "en": ""
    },
    "Finans": {
        "tr": "Bu bir finansal veri setidir. Gelir, gider, kar/zarar, risk faktörleri ve finansal trendlere özellikle dikkat et.",
        "en": "This is a financial dataset. Focus on revenue, expenses, profit/loss, risk factors and financial trends."
    },
    "Müşteri": {
        "tr": "Bu bir müşteri verisi setidir. Müşteri segmentasyonu, davranış kalıpları, churn riski ve müşteri memnuniyetine odaklan.",
        "en": "This is a customer dataset. Focus on segmentation, behavior patterns, churn risk and satisfaction."
    },
    "Sağlık": {
        "tr": "Bu bir sağlık/medikal veri setidir. Hasta demografisi, hastalık örüntüleri ve klinik öneme sahip bulgulara dikkat et.",
        "en": "This is a health/medical dataset. Focus on patient demographics, disease patterns and clinical findings."
    },
    "E-Ticaret": {
        "tr": "Bu bir e-ticaret verisidir. Satış trendleri, ürün performansı, müşteri satın alma davranışları ve gelir optimizasyonuna odaklan.",
        "en": "This is an e-commerce dataset. Focus on sales trends, product performance and revenue optimization."
    },
    "İK": {
        "tr": "Bu bir insan kaynakları verisidir. Çalışan performansı, işten ayrılma oranları, maaş dağılımı ve departman analizine odaklan.",
        "en": "This is an HR dataset. Focus on employee performance, turnover rates, salary distribution and department analysis."
    }
}

def get_templates():
    return list(TEMPLATES.keys())

def generate_report(stats, outliers, corr_matrix, language="Türkçe", template="Genel"):
    
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

    template_context = TEMPLATES.get(template, TEMPLATES["Genel"])
    
    if language == "English":
        ctx = template_context["en"]
        prompt = f"""You are a data analyst assistant. {ctx} Analyze the following dataset statistics and write a professional report in ENGLISH ONLY. Do not use any Turkish words.

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
        ctx = template_context["tr"]
        prompt = f"""Sen bir veri analisti asistanisin. {ctx} Asagidaki veri seti istatistiklerini analiz et ve Turkce dilinde profesyonel bir rapor yaz.

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
            return "GROQ_API_KEY bulunamadi! .env dosyasini kontrol et."
        
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
        return f"Hata: {str(e)}"