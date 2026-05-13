import pandas as pd
import numpy as np

def load_data(file):
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