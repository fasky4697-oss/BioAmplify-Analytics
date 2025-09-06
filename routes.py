from flask import render_template, request, jsonify, redirect, url_for, flash, send_file
from app import app, db
from models import Experiment, ComparisonStudy
from utils.statistics import calculate_diagnostic_stats, calculate_cohens_kappa
from utils.cost_analysis import get_technique_costs, calculate_total_cost
from utils.file_processing import process_uploaded_file
from utils.report_generation import generate_pdf_report, generate_excel_report
import json
import io
import logging

@app.route('/')
def index():
    """Home page with overview of the application"""
    recent_experiments = Experiment.query.order_by(Experiment.created_at.desc()).limit(5).all()
    return render_template('index.html', recent_experiments=recent_experiments)

@app.route('/data_input')
def data_input():
    """Data input page for manual entry or file upload"""
    return render_template('data_input.html')

@app.route('/submit_experiment', methods=['POST'])
def submit_experiment():
    """Process experiment data submission"""
    try:
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description', '')
        technique = request.form.get('technique')
        confidence_level = float(request.form.get('confidence_level', 0.95))
        
        # Get confusion matrix values
        tp = int(request.form.get('true_positive', 0))
        fp = int(request.form.get('false_positive', 0))
        tn = int(request.form.get('true_negative', 0))
        fn = int(request.form.get('false_negative', 0))
        
        # Validate inputs
        if not name or not technique:
            flash('Name and technique are required', 'error')
            return redirect(url_for('data_input'))
        
        if tp + fp + tn + fn == 0:
            flash('At least one confusion matrix value must be greater than 0', 'error')
            return redirect(url_for('data_input'))
        
        # Calculate diagnostic statistics
        stats = calculate_diagnostic_stats(tp, fp, tn, fn, confidence_level)
        
        # Get cost analysis
        cost_data = get_technique_costs(technique)
        total_cost = calculate_total_cost(technique, tp + fp + tn + fn)
        
        # Create experiment record
        experiment = Experiment(
            name=name,
            description=description,
            technique=technique,
            true_positive=tp,
            false_positive=fp,
            true_negative=tn,
            false_negative=fn,
            confidence_level=confidence_level,
            reagent_cost=cost_data['reagent_cost_per_test'],
            equipment_cost=cost_data['equipment_cost'],
            total_cost=total_cost
        )
        
        experiment.set_statistics(stats)
        
        db.session.add(experiment)
        db.session.commit()
        
        flash(f'Experiment "{name}" created successfully!', 'success')
        return redirect(url_for('view_experiment', id=experiment.id))
        
    except Exception as e:
        logging.error(f"Error submitting experiment: {str(e)}")
        flash('Error processing experiment data', 'error')
        return redirect(url_for('data_input'))

@app.route('/upload_file', methods=['POST'])
def upload_file():
    """Process file upload (CSV/Excel)"""
    try:
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('data_input'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('data_input'))
        
        # Process the uploaded file
        experiments_data = process_uploaded_file(file)
        
        if not experiments_data:
            flash('No valid data found in file', 'error')
            return redirect(url_for('data_input'))
        
        # Create experiments from file data
        created_count = 0
        for exp_data in experiments_data:
            try:
                stats = calculate_diagnostic_stats(
                    exp_data['tp'], exp_data['fp'], 
                    exp_data['tn'], exp_data['fn']
                )
                
                cost_data = get_technique_costs(exp_data['technique'])
                total_samples = exp_data['tp'] + exp_data['fp'] + exp_data['tn'] + exp_data['fn']
                total_cost = calculate_total_cost(exp_data['technique'], total_samples)
                
                experiment = Experiment(
                    name=exp_data['name'],
                    description=exp_data.get('description', ''),
                    technique=exp_data['technique'],
                    true_positive=exp_data['tp'],
                    false_positive=exp_data['fp'],
                    true_negative=exp_data['tn'],
                    false_negative=exp_data['fn'],
                    reagent_cost=cost_data['reagent_cost_per_test'],
                    equipment_cost=cost_data['equipment_cost'],
                    total_cost=total_cost
                )
                
                experiment.set_statistics(stats)
                db.session.add(experiment)
                created_count += 1
                
            except Exception as e:
                logging.error(f"Error creating experiment from file data: {str(e)}")
                continue
        
        db.session.commit()
        flash(f'Successfully created {created_count} experiments from file', 'success')
        return redirect(url_for('analysis'))
        
    except Exception as e:
        logging.error(f"Error processing file upload: {str(e)}")
        flash('Error processing uploaded file', 'error')
        return redirect(url_for('data_input'))

@app.route('/experiment/<int:id>')
def view_experiment(id):
    """View individual experiment results"""
    experiment = Experiment.query.get_or_404(id)
    stats = experiment.get_statistics()
    cost_data = get_technique_costs(experiment.technique)
    
    return render_template('results.html', 
                         experiment=experiment, 
                         statistics=stats,
                         cost_data=cost_data)

@app.route('/analysis')
def analysis():
    """Analysis page showing all experiments"""
    experiments = Experiment.query.order_by(Experiment.created_at.desc()).all()
    
    # Group experiments by technique for comparison
    techniques = {}
    for exp in experiments:
        if exp.technique not in techniques:
            techniques[exp.technique] = []
        techniques[exp.technique].append(exp)
    
    return render_template('analysis.html', 
                         experiments=experiments,
                         techniques=techniques)

@app.route('/compare_techniques', methods=['POST'])
def compare_techniques():
    """Compare multiple techniques using Cohen's Kappa"""
    try:
        experiment_ids = request.form.getlist('experiment_ids')
        comparison_name = request.form.get('comparison_name', 'Technique Comparison')
        
        if len(experiment_ids) < 2:
            flash('Please select at least 2 experiments to compare', 'error')
            return redirect(url_for('analysis'))
        
        # Get experiments
        experiments = Experiment.query.filter(Experiment.id.in_(experiment_ids)).all()
        
        if len(experiments) < 2:
            flash('Selected experiments not found', 'error')
            return redirect(url_for('analysis'))
        
        # Calculate Cohen's Kappa for pairwise comparisons
        kappa_results = {}
        for i, exp1 in enumerate(experiments):
            for j, exp2 in enumerate(experiments[i+1:], i+1):
                # Create binary classification arrays for comparison
                # For simplicity, we'll use positive/negative classification
                rater1 = []
                rater2 = []
                
                # Create arrays based on confusion matrix proportions
                total1 = exp1.true_positive + exp1.false_positive + exp1.true_negative + exp1.false_negative
                total2 = exp2.true_positive + exp2.false_positive + exp2.true_negative + exp2.false_negative
                
                # Normalize to smaller sample size for comparison
                min_total = min(total1, total2)
                
                # Create proportional arrays
                for _ in range(int((exp1.true_positive / total1) * min_total)):
                    rater1.append(1)
                    rater2.append(1)
                for _ in range(int((exp1.false_positive / total1) * min_total)):
                    rater1.append(1)
                    rater2.append(0)
                for _ in range(int((exp1.false_negative / total1) * min_total)):
                    rater1.append(0)
                    rater2.append(1)
                for _ in range(int((exp1.true_negative / total1) * min_total)):
                    rater1.append(0)
                    rater2.append(0)
                
                # Calculate Cohen's Kappa
                kappa_result = calculate_cohens_kappa(rater1, rater2)
                
                comparison_key = f"{exp1.name} vs {exp2.name}"
                kappa_results[comparison_key] = {
                    'kappa': kappa_result['kappa'],
                    'confidence_interval': kappa_result['confidence_interval'],
                    'standard_error': kappa_result['standard_error'],
                    'interpretation': kappa_result['interpretation']
                }
        
        # Create comparison study record
        comparison = ComparisonStudy(
            comparison_name,
            f"Comparison of {len(experiments)} techniques"
        )
        comparison.set_experiment_ids([int(id) for id in experiment_ids])
        comparison.set_kappa_results(kappa_results)
        
        db.session.add(comparison)
        db.session.commit()
        
        return render_template('results.html', 
                             comparison=comparison,
                             experiments=experiments,
                             kappa_results=kappa_results)
        
    except Exception as e:
        logging.error(f"Error in technique comparison: {str(e)}")
        flash('Error performing technique comparison', 'error')
        return redirect(url_for('analysis'))

@app.route('/cost_comparison')
def cost_comparison():
    """Cost comparison analysis page"""
    techniques = ['PCR', 'qPCR', 'LAMP', 'RPA', 'NASBA', 'TMA', 'HDA', 'SDA', 'NEAR']
    cost_data = {}
    
    for technique in techniques:
        cost_data[technique] = get_technique_costs(technique)
    
    # Get experiments grouped by technique for real cost analysis
    experiments = Experiment.query.all()
    technique_experiments = {}
    for exp in experiments:
        if exp.technique not in technique_experiments:
            technique_experiments[exp.technique] = []
        technique_experiments[exp.technique].append(exp)
    
    return render_template('cost_comparison.html', 
                         cost_data=cost_data,
                         technique_experiments=technique_experiments)

@app.route('/export/<format>/<int:experiment_id>')
def export_results(format, experiment_id):
    """Export experiment results to PDF or Excel"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        if format == 'pdf':
            pdf_buffer = generate_pdf_report(experiment)
            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name=f"{experiment.name}_report.pdf",
                mimetype='application/pdf'
            )
        elif format == 'excel':
            excel_buffer = generate_excel_report(experiment)
            return send_file(
                excel_buffer,
                as_attachment=True,
                download_name=f"{experiment.name}_data.xlsx",
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            flash('Invalid export format', 'error')
            return redirect(url_for('view_experiment', id=experiment_id))
            
    except Exception as e:
        logging.error(f"Error exporting results: {str(e)}")
        flash('Error generating export file', 'error')
        return redirect(url_for('view_experiment', id=experiment_id))

@app.route('/api/experiment/<int:id>/data')
def get_experiment_data(id):
    """API endpoint to get experiment data for charts"""
    experiment = Experiment.query.get_or_404(id)
    stats = experiment.get_statistics()
    
    return jsonify({
        'name': experiment.name,
        'technique': experiment.technique,
        'confusion_matrix': {
            'tp': experiment.true_positive,
            'fp': experiment.false_positive,
            'tn': experiment.true_negative,
            'fn': experiment.false_negative
        },
        'statistics': stats,
        'costs': {
            'reagent_cost': experiment.reagent_cost,
            'equipment_cost': experiment.equipment_cost,
            'total_cost': experiment.total_cost
        }
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('index.html'), 500
