import pandas as pd
import numpy as np

def load_data(file):
    filename = file.name.lower()
    
    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        return pd.read_excel(file)
    else:
        try:
            return pd.read_csv(file, encoding='utf-8')
        except UnicodeDecodeError:
            return pd.read_csv(file, encoding='latin-1')

def basic_stats(df):
    stats = {}
    stats['shape'] = df.shape
    stats['dtypes'] = df.dtypes.astype(str).to_dict()
    stats['missing'] = df.isnull().sum().to_dict()
    stats['missing_pct'] = (df.isnull().sum() / len(df) * 100).round(2).to_dict()
    stats['duplicates'] = int(df.duplicated().sum())
    
    numeric_df = df.select_dtypes(include=np.number)
    if not numeric_df.empty:
        stats['describe'] = numeric_df.describe().round(2).to_dict()
    else:
        stats['describe'] = {}
    
    return stats

def detect_outliers(df):
    outliers = {}
    numeric_cols = df.select_dtypes(include=np.number).columns
    
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outlier_count = int(((df[col] < lower) | (df[col] > upper)).sum())
        outlier_pct = round(outlier_count / len(df) * 100, 2)
        outliers[col] = {
            'count': outlier_count,
            'percentage': outlier_pct,
            'lower_bound': round(lower, 2),
            'upper_bound': round(upper, 2)
        }
    
    return outliers

def correlation_matrix(df):
    numeric_df = df.select_dtypes(include=np.number)
    if numeric_df.shape[1] < 2:
        return None
    return numeric_df.corr().round(2)

def clean_data(df, fill_method, columns_to_drop):
    cleaned = df.copy()
    
    # Sütun sil
    if columns_to_drop:
        cleaned = cleaned.drop(columns=columns_to_drop, errors='ignore')
    
    # Eksik değerleri doldur
    numeric_cols = cleaned.select_dtypes(include=np.number).columns
    cat_cols = cleaned.select_dtypes(include=['object', 'category']).columns
    
    if fill_method == "Mean (Ortalama)":
        cleaned[numeric_cols] = cleaned[numeric_cols].fillna(cleaned[numeric_cols].mean())
    elif fill_method == "Median (Medyan)":
        cleaned[numeric_cols] = cleaned[numeric_cols].fillna(cleaned[numeric_cols].median())
    elif fill_method == "Mode (Mod)":
        cleaned[numeric_cols] = cleaned[numeric_cols].fillna(cleaned[numeric_cols].mode().iloc[0])
    elif fill_method == "Sıfır (0)":
        cleaned[numeric_cols] = cleaned[numeric_cols].fillna(0)
    elif fill_method == "Sil (Drop Rows)":
        cleaned = cleaned.dropna()
    
    # Kategorik sütunlardaki eksikleri mod ile doldur
    for col in cat_cols:
        if cleaned[col].isnull().any():
            cleaned[col] = cleaned[col].fillna(cleaned[col].mode().iloc[0] if not cleaned[col].mode().empty else "Unknown")
    
    return cleaned

def fix_dtypes(df):
    fixed = df.copy()
    for col in fixed.columns:
        # Tarih tespiti
        if fixed[col].dtype == 'object':
            try:
                fixed[col] = pd.to_datetime(fixed[col])
                continue
            except:
                pass
            # Sayı tespiti
            try:
                fixed[col] = pd.to_numeric(fixed[col])
            except:
                pass
    return fixed

def feature_importance(df, target_col):
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    
    data = df.copy()
    
    # Hedef sütunu ayır
    y = data[target_col]
    X = data.drop(columns=[target_col])
    
    # Sadece sayısal sütunları al
    X = X.select_dtypes(include=np.number)
    
    if X.empty or len(X.columns) < 1:
        return None, "Yeterli sayısal sütun yok."
    
    # Eksik değerleri doldur
    X = X.fillna(X.mean())
    
    # Hedef sütun sayısal mı kategorik mi?
    if y.dtype == 'object' or y.nunique() < 10:
        le = LabelEncoder()
        y = le.fit_transform(y.astype(str))
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        task = "classification"
    else:
        y = y.fillna(y.mean())
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        task = "regression"
    
    model.fit(X, y)
    
    importance_df = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    return importance_df, task

def data_quality_score(df):
    score = 100
    details = []
    
    # 1. Eksik değer kontrolü
    missing_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100
    if missing_pct > 0:
        penalty = min(missing_pct * 2, 30)
        score -= penalty
        details.append(f"❌ Eksik değerler: %{missing_pct:.1f} → -{penalty:.0f} puan")
    else:
        details.append("✅ Eksik değer yok → +0 puan")
    
    # 2. Yinelenen satır kontrolü
    dup_pct = df.duplicated().sum() / len(df) * 100
    if dup_pct > 0:
        penalty = min(dup_pct * 2, 20)
        score -= penalty
        details.append(f"❌ Yinelenen satırlar: %{dup_pct:.1f} → -{penalty:.0f} puan")
    else:
        details.append("✅ Yinelenen satır yok → +0 puan")
    
    # 3. Outlier kontrolü
    numeric_cols = df.select_dtypes(include=np.number).columns
    total_outliers = 0
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)).sum()
        total_outliers += outliers
    
    outlier_pct = total_outliers / (len(df) * len(numeric_cols)) * 100 if len(numeric_cols) > 0 else 0
    if outlier_pct > 0:
        penalty = min(outlier_pct * 1.5, 20)
        score -= penalty
        details.append(f"❌ Aykırı değerler: %{outlier_pct:.1f} → -{penalty:.0f} puan")
    else:
        details.append("✅ Aykırı değer yok → +0 puan")
    
    # 4. Veri tipi tutarlılığı
    mixed_cols = []
    for col in df.select_dtypes(include='object').columns:
        try:
            pd.to_numeric(df[col])
            mixed_cols.append(col)
        except:
            pass
    
    if mixed_cols:
        penalty = len(mixed_cols) * 5
        score -= penalty
        details.append(f"❌ Sayı olması gereken metin sütunlar: {mixed_cols} → -{penalty} puan")
    else:
        details.append("✅ Veri tipleri tutarlı → +0 puan")
    
    score = max(0, round(score))
    
    if score >= 80:
        grade = "A"
        color = "green"
        comment = "Veri kalitesi yüksek, analize hazır!"
    elif score >= 60:
        grade = "B"
        color = "orange"
        comment = "Veri kalitesi orta, bazı iyileştirmeler önerilir."
    elif score >= 40:
        grade = "C"
        color = "red"
        comment = "Veri kalitesi düşük, temizleme gerekli."
    else:
        grade = "F"
        color = "red"
        comment = "Veri kalitesi çok düşük, kapsamlı temizlik şart!"
    
    return {
        'score': score,
        'grade': grade,
        'color': color,
        'comment': comment,
        'details': details
    }
def detect_time_series(df):
    date_cols = []
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]':
            date_cols.append(col)
        elif df[col].dtype == 'object':
            try:
                pd.to_datetime(df[col])
                date_cols.append(col)
            except:
                pass
    return date_cols