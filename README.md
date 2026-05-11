# 📊 AutoEDA Pro — Otomatik Keşifsel Veri Analizi

CSV dosyası yükle, saniyeler içinde profesyonel veri analizi raporu al!

## 🚀 Özellikler
- 📈 Otomatik istatistikler (ortalama, medyan, std, eksik değerler)
- 📊 İnteraktif grafikler (dağılım, korelasyon, kategorik analiz)
- ⚠️ Outlier tespiti (IQR yöntemi)
- 🤖 AI destekli otomatik Türkçe/İngilizce rapor (Llama 3.1)
- 📄 PDF export

## 🛠️ Kurulum

### Gereksinimler
- Python 3.8+
- [Ollama](https://ollama.com) (AI rapor için)

### Adımlar
```bash
# Repoyu klonla
git clone https://github.com/KULLANICIADIN/autoeda-pro.git
cd autoeda-pro

# Sanal ortam oluştur
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Kütüphaneleri kur
pip install -r requirements.txt

# Ollama modeli indir
ollama pull llama3.1

# Uygulamayı başlat
streamlit run app.py
```

## 🧰 Teknolojiler
- Streamlit
- Pandas & NumPy
- Plotly
- Llama 3.1 (Ollama)
- ReportLab
