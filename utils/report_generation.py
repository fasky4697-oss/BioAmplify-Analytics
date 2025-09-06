import io
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import seaborn as sns
from datetime import datetime
import base64
from models import Experiment
from utils.statistics import calculate_diagnostic_stats
from utils.cost_analysis import get_technique_costs

def generate_pdf_report(experiment: Experiment) -> io.BytesIO:
    """
    Generate comprehensive PDF report for an experiment
    
    Args:
        experiment: Experiment model instance
    
    Returns:
        io.BytesIO: PDF file buffer
    """
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        alignment=1,  # Center alignment
        spaceAfter=30
    )
    
    story.append(Paragraph("Bioinformatics Amplification Analysis Report", title_style))
    story.append(Spacer(1, 20))
    
    # Experiment Information
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10
    )
    
    story.append(Paragraph("<b>Experiment Information</b>", styles['Heading2']))
    story.append(Paragraph(f"<b>Name:</b> {experiment.name}", info_style))
    story.append(Paragraph(f"<b>Technique:</b> {experiment.technique}", info_style))
    story.append(Paragraph(f"<b>Date Created:</b> {experiment.created_at.strftime('%Y-%m-%d %H:%M')}", info_style))
    if experiment.description:
        story.append(Paragraph(f"<b>Description:</b> {experiment.description}", info_style))
    story.append(Spacer(1, 20))
    
    # Confusion Matrix
    story.append(Paragraph("<b>Confusion Matrix</b>", styles['Heading2']))
    
    confusion_data = [
        ['', 'Predicted Positive', 'Predicted Negative'],
        ['Actual Positive', str(experiment.true_positive), str(experiment.false_negative)],
        ['Actual Negative', str(experiment.false_positive), str(experiment.true_negative)]
    ]
    
    confusion_table = Table(confusion_data)
    confusion_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 1), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(confusion_table)
    story.append(Spacer(1, 20))
    
    # Diagnostic Statistics
    story.append(Paragraph("<b>Diagnostic Statistics</b>", styles['Heading2']))
    
    stats = experiment.get_statistics()
    
    stats_data = [
        ['Metric', 'Value (%)', '95% Confidence Interval'],
        ['Sensitivity', f"{stats['sensitivity']['percentage']:.2f}%", 
         f"({stats['sensitivity']['ci_lower']:.3f} - {stats['sensitivity']['ci_upper']:.3f})"],
        ['Specificity', f"{stats['specificity']['percentage']:.2f}%",
         f"({stats['specificity']['ci_lower']:.3f} - {stats['specificity']['ci_upper']:.3f})"],
        ['Positive Predictive Value', f"{stats['ppv']['percentage']:.2f}%",
         f"({stats['ppv']['ci_lower']:.3f} - {stats['ppv']['ci_upper']:.3f})"],
        ['Negative Predictive Value', f"{stats['npv']['percentage']:.2f}%",
         f"({stats['npv']['ci_lower']:.3f} - {stats['npv']['ci_upper']:.3f})"],
        ['Accuracy', f"{stats['accuracy']['percentage']:.2f}%",
         f"({stats['accuracy']['ci_lower']:.3f} - {stats['accuracy']['ci_upper']:.3f})"],
        ['F1 Score', f"{stats['f1_score']:.3f}", ""],
        ['Matthews Correlation Coefficient', f"{stats['mcc']:.3f}", ""]
    ]
    
    stats_table = Table(stats_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')])
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 20))
    
    # Cost Analysis
    story.append(Paragraph("<b>Cost Analysis</b>", styles['Heading2']))
    
    cost_data = get_technique_costs(experiment.technique)
    total_samples = experiment.true_positive + experiment.false_positive + experiment.true_negative + experiment.false_negative
    
    cost_analysis_data = [
        ['Cost Component', 'Value'],
        ['Equipment Cost', f"฿{cost_data['equipment_cost']:,.2f}"],
        ['Reagent Cost per Test', f"฿{cost_data['reagent_cost_per_test']:.2f}"],
        ['Total Samples', str(total_samples)],
        ['Total Reagent Cost', f"฿{experiment.reagent_cost * total_samples:.2f}"],
        ['Estimated Total Cost', f"฿{experiment.total_cost:.2f}"],
        ['Cost per Sample', f"฿{experiment.total_cost / total_samples:.2f}"]
    ]
    
    cost_table = Table(cost_analysis_data, colWidths=[3*inch, 2*inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fadbd8')])
    ]))
    
    story.append(cost_table)
    story.append(Spacer(1, 20))
    
    # Technique Characteristics
    story.append(Paragraph("<b>Technique Characteristics</b>", styles['Heading2']))
    
    char_data = [
        ['Characteristic', 'Value'],
        ['Temperature Requirement', cost_data['temperature_requirement']],
        ['Time per Test', f"{cost_data['time_per_test_minutes']} minutes"],
        ['Throughput per Hour', f"{cost_data['throughput_samples_per_hour']} samples"],
        ['Power Consumption', f"{cost_data['power_consumption_watts']} watts"],
        ['Operator Skill Required', cost_data['operator_skill_required']],
        ['Field Suitability', cost_data['field_suitability']],
        ['Multiplexing Capability', cost_data['multiplexing_capability']]
    ]
    
    char_table = Table(char_data, colWidths=[3*inch, 2*inch])
    char_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ebdef0')])
    ]))
    
    story.append(char_table)
    
    # Footer
    story.append(Spacer(1, 40))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Bioinformatics Amplification Analysis Tool", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_excel_report(experiment: Experiment) -> io.BytesIO:
    """
    Generate comprehensive Excel report for an experiment
    
    Args:
        experiment: Experiment model instance
    
    Returns:
        io.BytesIO: Excel file buffer
    """
    
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        
        # Summary Sheet
        summary_data = {
            'Experiment Information': [
                'Name', 'Technique', 'Date Created', 'Description',
                'True Positives', 'False Positives', 'True Negatives', 'False Negatives',
                'Total Samples'
            ],
            'Values': [
                experiment.name,
                experiment.technique,
                experiment.created_at.strftime('%Y-%m-%d %H:%M'),
                experiment.description or 'N/A',
                experiment.true_positive,
                experiment.false_positive,
                experiment.true_negative,
                experiment.false_negative,
                experiment.true_positive + experiment.false_positive + experiment.true_negative + experiment.false_negative
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Statistics Sheet
        stats = experiment.get_statistics()
        
        stats_data = {
            'Metric': [
                'Sensitivity', 'Specificity', 'Positive Predictive Value',
                'Negative Predictive Value', 'Accuracy', 'F1 Score',
                'Matthews Correlation Coefficient', 'Prevalence'
            ],
            'Value': [
                stats['sensitivity']['value'],
                stats['specificity']['value'],
                stats['ppv']['value'],
                stats['npv']['value'],
                stats['accuracy']['value'],
                stats['f1_score'],
                stats['mcc'],
                stats['prevalence']['value']
            ],
            'Percentage': [
                stats['sensitivity']['percentage'],
                stats['specificity']['percentage'],
                stats['ppv']['percentage'],
                stats['npv']['percentage'],
                stats['accuracy']['percentage'],
                stats['f1_score'] * 100,
                stats['mcc'] * 100,
                stats['prevalence']['percentage']
            ],
            'CI_Lower': [
                stats['sensitivity']['ci_lower'],
                stats['specificity']['ci_lower'],
                stats['ppv']['ci_lower'],
                stats['npv']['ci_lower'],
                stats['accuracy']['ci_lower'],
                None, None, None
            ],
            'CI_Upper': [
                stats['sensitivity']['ci_upper'],
                stats['specificity']['ci_upper'],
                stats['ppv']['ci_upper'],
                stats['npv']['ci_upper'],
                stats['accuracy']['ci_upper'],
                None, None, None
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        # Cost Analysis Sheet
        cost_data = get_technique_costs(experiment.technique)
        total_samples = experiment.true_positive + experiment.false_positive + experiment.true_negative + experiment.false_negative
        
        cost_analysis_data = {
            'Cost Component': [
                'Equipment Cost', 'Equipment Cost Range (Min)', 'Equipment Cost Range (Max)',
                'Reagent Cost per Test', 'Reagent Cost Range (Min)', 'Reagent Cost Range (Max)',
                'Total Samples', 'Total Reagent Cost', 'Maintenance Cost (Annual)',
                'Power Consumption (Watts)', 'Estimated Total Cost', 'Cost per Sample'
            ],
            'Value': [
                cost_data['equipment_cost'],
                cost_data['equipment_cost_range'][0],
                cost_data['equipment_cost_range'][1],
                cost_data['reagent_cost_per_test'],
                cost_data['reagent_cost_range'][0],
                cost_data['reagent_cost_range'][1],
                total_samples,
                experiment.reagent_cost * total_samples,
                cost_data['maintenance_cost_annual'],
                cost_data['power_consumption_watts'],
                experiment.total_cost,
                experiment.total_cost / total_samples if total_samples > 0 else 0
            ]
        }
        
        cost_df = pd.DataFrame(cost_analysis_data)
        cost_df.to_excel(writer, sheet_name='Cost Analysis', index=False)
        
        # Performance Characteristics Sheet
        performance_data = {
            'Characteristic': [
                'Temperature Requirement', 'Time per Test (minutes)',
                'Throughput per Hour', 'Power Consumption (watts)',
                'Operator Skill Required', 'Field Suitability',
                'Multiplexing Capability'
            ],
            'Value': [
                cost_data['temperature_requirement'],
                cost_data['time_per_test_minutes'],
                cost_data['throughput_samples_per_hour'],
                cost_data['power_consumption_watts'],
                cost_data['operator_skill_required'],
                cost_data['field_suitability'],
                cost_data['multiplexing_capability']
            ]
        }
        
        performance_df = pd.DataFrame(performance_data)
        performance_df.to_excel(writer, sheet_name='Performance', index=False)
        
        # Raw Data Sheet
        raw_data = {
            'Classification': ['True Positive', 'False Positive', 'True Negative', 'False Negative'],
            'Count': [experiment.true_positive, experiment.false_positive, experiment.true_negative, experiment.false_negative],
            'Percentage': [
                (experiment.true_positive / total_samples * 100) if total_samples > 0 else 0,
                (experiment.false_positive / total_samples * 100) if total_samples > 0 else 0,
                (experiment.true_negative / total_samples * 100) if total_samples > 0 else 0,
                (experiment.false_negative / total_samples * 100) if total_samples > 0 else 0
            ]
        }
        
        raw_df = pd.DataFrame(raw_data)
        raw_df.to_excel(writer, sheet_name='Raw Data', index=False)
    
    buffer.seek(0)
    return buffer

def create_statistics_chart(experiment: Experiment) -> str:
    """
    Create a statistics visualization chart and return as base64 string
    
    Args:
        experiment: Experiment model instance
    
    Returns:
        str: Base64 encoded image
    """
    
    stats = experiment.get_statistics()
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Performance metrics bar chart
    metrics = ['Sensitivity', 'Specificity', 'PPV', 'NPV', 'Accuracy']
    values = [
        stats['sensitivity']['percentage'],
        stats['specificity']['percentage'],
        stats['ppv']['percentage'],
        stats['npv']['percentage'],
        stats['accuracy']['percentage']
    ]
    
    colors_list = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
    
    bars = ax1.bar(metrics, values, color=colors_list)
    ax1.set_ylabel('Percentage (%)')
    ax1.set_title(f'Diagnostic Performance - {experiment.technique}')
    ax1.set_ylim(0, 100)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value:.1f}%', ha='center', va='bottom')
    
    # Confusion matrix heatmap
    confusion_matrix = [
        [experiment.true_positive, experiment.false_negative],
        [experiment.false_positive, experiment.true_negative]
    ]
    
    im = ax2.imshow(confusion_matrix, cmap='Blues', interpolation='nearest')
    ax2.set_title('Confusion Matrix')
    ax2.set_xlabel('Predicted')
    ax2.set_ylabel('Actual')
    
    # Add text annotations
    for i in range(2):
        for j in range(2):
            text = ax2.text(j, i, confusion_matrix[i][j],
                           ha="center", va="center", color="black", fontweight='bold')
    
    ax2.set_xticks([0, 1])
    ax2.set_yticks([0, 1])
    ax2.set_xticklabels(['Positive', 'Negative'])
    ax2.set_yticklabels(['Positive', 'Negative'])
    
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return image_base64

def create_cost_comparison_chart(experiments: list) -> str:
    """
    Create cost comparison chart for multiple experiments
    
    Args:
        experiments: List of Experiment model instances
    
    Returns:
        str: Base64 encoded image
    """
    
    if not experiments:
        return ""
    
    # Prepare data
    techniques = [exp.technique for exp in experiments]
    costs_per_sample = [
        exp.total_cost / (exp.true_positive + exp.false_positive + exp.true_negative + exp.false_negative)
        for exp in experiments
    ]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar chart
    bars = ax.bar(techniques, costs_per_sample, 
                  color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'][:len(techniques)])
    
    ax.set_ylabel('Cost per Sample ($)')
    ax.set_title('Cost Comparison by Technique')
    
    # Add value labels on bars
    for bar, cost in zip(bars, costs_per_sample):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'${cost:.2f}', ha='center', va='bottom')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return image_base64
