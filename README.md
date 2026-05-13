# 📊 AutoEDA Pro — Automated Exploratory Data Analysis

> Upload a CSV file and get a professional data analysis report in seconds — with AI-powered insights in Turkish or English.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red?style=flat-square&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-green?style=flat-square&logo=plotly)
![Ollama](https://img.shields.io/badge/Ollama-Llama3.1-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 🚀 Features

- 📈 **Automatic Statistics** — mean, median, std, missing values, duplicates
- 📊 **Interactive Charts** — distribution plots, correlation heatmap, categorical analysis
- ⚠️ **Outlier Detection** — IQR method with visual highlights
- ❓ **Missing Value Analysis** — visual breakdown by column
- 🤖 **AI-Powered Report** — automatic narrative in Turkish or English (Llama 3.1 via Ollama)
- 📄 **PDF Export** — download a professional report with one click

---

## 🖥️ Screenshots

![Statistics](Screenshot1.png)
![Charts](Screenshot2.png)
![AI Report](Screenshot3.png)

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Streamlit | Web interface |
| Pandas & NumPy | Data analysis |
| Plotly | Interactive visualizations |
| Llama 3.1 (Ollama) | AI report generation |
| ReportLab | PDF export |

---

## ⚙️ Installation

### Requirements
- Python 3.8+
- [Ollama](https://ollama.com) (for AI report feature)

### Steps

```bash
# Clone the repo
git clone https://github.com/iremnurefe/autoeda-pro.git
cd autoeda-pro

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download AI model
ollama pull llama3.1

# Run the app
streamlit run app.py
```

---

## 📂 Project Structure
autoeda-pro/
├── app.py                 # Main Streamlit application
├── requirements.txt
├── README.md
├── eda/
│   ├── analyzer.py        # Statistical analysis
│   ├── visualizer.py      # Plotly visualizations
│   └── reporter.py        # AI report generation (Ollama)
├── export/
│   └── pdf_exporter.py    # PDF report creation
└── sample_data/
└── ornek_veri.csv     # Sample dataset

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)

---

⭐ If you found this useful, please give it a star!
