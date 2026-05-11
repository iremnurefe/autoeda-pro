import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"

def generate_report(stats, outliers, corr_matrix, language="Türkçe"):
    
    # Ollama'ya göndereceğimiz özet veriyi hazırla
    rows, cols = stats['shape']
    missing_cols = {k: v for k, v in stats['missing'].items() if v > 0}
    duplicates = stats['duplicates']
    
    outlier_summary = []
    for col, info in outliers.items():
        if info['count'] > 0:
            outlier_summary.append(f"{col}: {info['count']} aykırı değer (%{info['percentage']})")
    
    corr_summary = []
    if corr_matrix is not None:
        corr_pairs = []
        cols_list = corr_matrix.columns.tolist()
        for i in range(len(cols_list)):
            for j in range(i+1, len(cols_list)):
                val = corr_matrix.iloc[i, j]
                if abs(val) > 0.5:
                    corr_pairs.append(f"{cols_list[i]} & {cols_list[j]}: {val}")
        corr_summary = corr_pairs

    prompt = f"""
Sen bir veri analisti asistanısın. Aşağıdaki veri seti istatistiklerini analiz et ve {language} dilinde profesyonel bir rapor yaz.

VERİ SETİ BİLGİLERİ:
- Satır sayısı: {rows}
- Sütun sayısı: {cols}
- Sütunlar: {list(stats['dtypes'].keys())}
- Eksik değer olan sütunlar: {missing_cols if missing_cols else 'Yok'}
- Yinelenen satır sayısı: {duplicates}
- Aykırı değerler: {outlier_summary if outlier_summary else 'Tespit edilmedi'}
- Güçlü korelasyonlar (|r| > 0.5): {corr_summary if corr_summary else 'Tespit edilmedi'}

Lütfen şunları içeren bir rapor yaz:
1. Veri setine genel bakış
2. Veri kalitesi değerlendirmesi
3. Öne çıkan bulgular
4. Öneriler

Rapor profesyonel, net ve {language} dilinde olsun. Markdown formatında yaz.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "Rapor üretilemedi.")
        else:
            return f"Hata: Ollama'ya bağlanılamadı. Status: {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return "⚠️ Ollama çalışmıyor! Terminalde 'ollama serve' komutunu çalıştır."
    except requests.exceptions.Timeout:
        return "⚠️ Zaman aşımı! Ollama yanıt vermedi, tekrar dene."
    except Exception as e:
        return f"⚠️ Beklenmeyen hata: {str(e)}"
