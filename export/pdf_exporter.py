from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os
import urllib.request
from datetime import datetime

def get_font():
    font_path = "C:/Windows/Fonts/arial.ttf"
    try:
        pdfmetrics.registerFont(TTFont('Arial', font_path))
        return 'Arial'
    except:
        return 'Helvetica'
    
def create_pdf_report(stats, outliers, ai_report, filename="eda_report.pdf"):
    buffer = io.BytesIO()
    font = get_font()
    
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        fontName=font,
        textColor=colors.HexColor('#2E4057'),
        spaceAfter=10
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        fontName=font,
        textColor=colors.HexColor('#048A81'),
        spaceBefore=15,
        spaceAfter=8
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        fontName=font,
        leading=16
    )

    # Başlık
    story.append(Paragraph("AutoEDA Pro — Otomatik Veri Analizi Raporu", title_style))
    story.append(Paragraph(f"Olusturulma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#048A81')))
    story.append(Spacer(1, 0.5*cm))

    # Genel Bilgiler
    story.append(Paragraph("1. Veri Seti Genel Bilgileri", heading_style))
    rows, cols = stats['shape']
    general_data = [
        ['Ozellik', 'Deger'],
        ['Satir Sayisi', str(rows)],
        ['Sutun Sayisi', str(cols)],
        ['Yinelenen Satir', str(stats['duplicates'])],
        ['Toplam Eksik Deger', str(sum(stats['missing'].values()))],
    ]
    
    table = Table(general_data, colWidths=[8*cm, 8*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (-1, -1), font),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5*cm))

    # Eksik Degerler
    story.append(Paragraph("2. Eksik Deger Analizi", heading_style))
    missing_cols = {k: v for k, v in stats['missing'].items() if v > 0}
    if missing_cols:
        missing_data = [['Sutun', 'Eksik Sayisi', 'Eksik Yuzdesi']]
        for col, count in missing_cols.items():
            pct = stats['missing_pct'][col]
            missing_data.append([col, str(count), f"%{pct}"])
        
        table2 = Table(missing_data, colWidths=[6*cm, 5*cm, 5*cm])
        table2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), font),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(table2)
    else:
        story.append(Paragraph("Eksik deger tespit edilmedi.", normal_style))
    
    story.append(Spacer(1, 0.5*cm))

    # Outlier Analizi
    story.append(Paragraph("3. Aykiri Deger (Outlier) Analizi", heading_style))
    outlier_data = [['Sutun', 'Outlier Sayisi', 'Yuzdesi', 'Alt Sinir', 'Ust Sinir']]
    for col, info in outliers.items():
        outlier_data.append([
            col,
            str(info['count']),
            f"%{info['percentage']}",
            str(info['lower_bound']),
            str(info['upper_bound'])
        ])
    
    table3 = Table(outlier_data, colWidths=[4*cm, 3.5*cm, 3*cm, 3*cm, 3*cm])
    table3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), font),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(table3)
    story.append(Spacer(1, 0.5*cm))

    # AI Raporu
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Paragraph("4. AI Destekli Analiz Yorumu", heading_style))
    
    clean_report = ai_report.replace('**', '').replace('##', '').replace('#', '').replace('*', '-')
    for line in clean_report.split('\n'):
        if line.strip():
            # Türkçe karakterleri koru
            safe_line = line.strip()
            try:
                story.append(Paragraph(safe_line, normal_style))
                story.append(Spacer(1, 0.2*cm))
            except:
                pass

    doc.build(story)
    buffer.seek(0)
    return buffer