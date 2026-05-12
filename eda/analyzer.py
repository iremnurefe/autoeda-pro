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