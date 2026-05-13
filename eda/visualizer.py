import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def plot_distributions(df):
    figures = []
    numeric_cols = df.select_dtypes(include=np.number).columns
    
    for col in numeric_cols:
        fig = px.histogram(
            df, x=col, marginal="box",
            title=f"{col} — Dağılım & Boxplot",
            color_discrete_sequence=["#636EFA"]
        )
        fig.update_layout(bargap=0.1)
        figures.append((col, fig))
    
    return figures

def plot_correlation_heatmap(corr_matrix):
    if corr_matrix is None:
        return None
    
    fig = px.imshow(
        corr_matrix,
        title="Korelasyon Matrisi",
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        text_auto=True
    )
    fig.update_layout(width=700, height=600)
    return fig

def plot_missing_values(df):
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    
    if missing.empty:
        return None
    
    fig = px.bar(
        x=missing.index,
        y=missing.values,
        title="Eksik Değerler",
        labels={"x": "Sütun", "y": "Eksik Sayısı"},
        color=missing.values,
        color_continuous_scale="Reds"
    )
    return fig

def plot_outliers(outliers_dict):
    if not outliers_dict:
        return None
    
    cols = list(outliers_dict.keys())
    counts = [outliers_dict[c]['count'] for c in cols]
    pcts = [outliers_dict[c]['percentage'] for c in cols]
    
    fig = px.bar(
        x=cols, y=counts,
        title="Outlier (Aykırı Değer) Tespiti — IQR Yöntemi",
        labels={"x": "Sütun", "y": "Outlier Sayısı"},
        color=pcts,
        color_continuous_scale="Oranges",
        text=pcts
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    return fig

def plot_categorical(df):
    figures = []
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    
    for col in cat_cols:
        value_counts = df[col].value_counts().head(15)
        fig = px.bar(
            x=value_counts.index,
            y=value_counts.values,
            title=f"{col} — Kategori Dağılımı (Top 15)",
            labels={"x": col, "y": "Adet"},
            color=value_counts.values,
            color_continuous_scale="Blues"
        )
        figures.append((col, fig))
    
    return figures

def plot_scatter(df, col_x, col_y, color_col=None):
    fig = px.scatter(
        df, x=col_x, y=col_y,
        color=color_col if color_col != "Yok" else None,
        title=f"{col_x} vs {col_y} — Scatter Plot",
        trendline="ols",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    return fig

def plot_pie(df, col):
    value_counts = df[col].value_counts().head(10)
    fig = px.pie(
        values=value_counts.values,
        names=value_counts.index,
        title=f"{col} — Pasta Grafik (Top 10)",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def plot_feature_importance(importance_df):
    fig = px.bar(
        importance_df,
        x='importance',
        y='feature',
        orientation='h',
        title="Feature Importance — Hangi Sütun Daha Etkili?",
        labels={'importance': 'Önem Skoru', 'feature': 'Sütun'},
        color='importance',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig