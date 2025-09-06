import pandas as pd
import numpy as np
from werkzeug.datastructures import FileStorage
import io
import logging
from typing import List, Dict, Optional

def process_uploaded_file(file: FileStorage) -> List[Dict]:
    """
    Process uploaded CSV or Excel file containing experimental data
    
    Args:
        file: Uploaded file object
    
    Returns:
        list: List of experiment data dictionaries
    """
    
    try:
        filename = file.filename.lower()
        
        # Read file based on extension
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            raise ValueError("Unsupported file format. Please upload CSV or Excel files.")
        
        # Validate and process the dataframe
        experiments_data = validate_and_extract_data(df)
        
        return experiments_data
        
    except Exception as e:
        logging.error(f"Error processing uploaded file: {str(e)}")
        raise

def validate_and_extract_data(df: pd.DataFrame) -> List[Dict]:
    """
    Validate and extract experiment data from DataFrame
    
    Expected columns:
    - name: Experiment name
    - description: Experiment description (optional)
    - technique: Amplification technique (qPCR, LAMP, RPA, NASBA)
    - true_positive: Number of true positives
    - false_positive: Number of false positives  
    - true_negative: Number of true negatives
    - false_negative: Number of false negatives
    
    Alternative column names are also supported for flexibility
    """
    
    # Define possible column name mappings
    column_mappings = {
        'name': ['name', 'experiment_name', 'test_name', 'study_name'],
        'description': ['description', 'desc', 'notes', 'comments'],
        'technique': ['technique', 'method', 'amplification_method', 'technology'],
        'true_positive': ['true_positive', 'tp', 'true_pos', 'correct_positive'],
        'false_positive': ['false_positive', 'fp', 'false_pos', 'incorrect_positive'],
        'true_negative': ['true_negative', 'tn', 'true_neg', 'correct_negative'],
        'false_negative': ['false_negative', 'fn', 'false_neg', 'incorrect_negative']
    }
    
    # Map column names to standardized names
    df_columns_lower = [col.lower().replace(' ', '_') for col in df.columns]
    column_map = {}
    
    for standard_name, possible_names in column_mappings.items():
        for possible_name in possible_names:
            if possible_name in df_columns_lower:
                original_col = df.columns[df_columns_lower.index(possible_name)]
                column_map[standard_name] = original_col
                break
    
    # Check for required columns
    required_columns = ['name', 'technique', 'true_positive', 'false_positive', 'true_negative', 'false_negative']
    missing_columns = [col for col in required_columns if col not in column_map]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}. Please ensure your file contains these columns.")
    
    experiments_data = []
    valid_techniques = ['PCR', 'qPCR', 'LAMP', 'RPA', 'NASBA', 'TMA', 'HDA', 'SDA', 'NEAR']
    
    for index, row in df.iterrows():
        try:
            # Extract data using column mapping
            name = str(row[column_map['name']]).strip()
            technique = str(row[column_map['technique']]).strip()
            
            # Validate technique
            technique_upper = technique.upper()
            if technique_upper not in [t.upper() for t in valid_techniques]:
                logging.warning(f"Row {index + 1}: Invalid technique '{technique}'. Skipping.")
                continue
            
            # Find matching technique (case insensitive)
            technique_matched = next(t for t in valid_techniques if t.upper() == technique_upper)
            
            # Extract confusion matrix values
            tp = int(row[column_map['true_positive']])
            fp = int(row[column_map['false_positive']])
            tn = int(row[column_map['true_negative']])
            fn = int(row[column_map['false_negative']])
            
            # Validate confusion matrix values
            if tp < 0 or fp < 0 or tn < 0 or fn < 0:
                logging.warning(f"Row {index + 1}: Negative values in confusion matrix. Skipping.")
                continue
            
            if tp + fp + tn + fn == 0:
                logging.warning(f"Row {index + 1}: All confusion matrix values are zero. Skipping.")
                continue
            
            # Extract optional description
            description = ""
            if 'description' in column_map:
                description = str(row[column_map['description']]) if pd.notna(row[column_map['description']]) else ""
            
            experiment_data = {
                'name': name,
                'description': description,
                'technique': technique_matched,
                'tp': tp,
                'fp': fp,
                'tn': tn,
                'fn': fn
            }
            
            experiments_data.append(experiment_data)
            
        except Exception as e:
            logging.warning(f"Row {index + 1}: Error processing data - {str(e)}. Skipping.")
            continue
    
    if not experiments_data:
        raise ValueError("No valid experiment data found in file.")
    
    return experiments_data

def generate_template_csv() -> str:
    """
    Generate a CSV template string for users to download
    
    Returns:
        str: CSV template content
    """
    
    template_data = {
        'name': ['Experiment_1', 'Experiment_2', 'Experiment_3'],
        'description': ['qPCR validation study', 'LAMP comparison test', 'RPA field trial'],
        'technique': ['qPCR', 'LAMP', 'RPA'],
        'true_positive': [85, 78, 82],
        'false_positive': [3, 5, 4],
        'true_negative': [92, 88, 89],
        'false_negative': [5, 9, 7]
    }
    
    df = pd.DataFrame(template_data)
    
    # Convert to CSV string
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

def generate_template_excel() -> bytes:
    """
    Generate an Excel template file for users to download
    
    Returns:
        bytes: Excel file content
    """
    
    template_data = {
        'name': ['Experiment_1', 'Experiment_2', 'Experiment_3'],
        'description': ['qPCR validation study', 'LAMP comparison test', 'RPA field trial'],
        'technique': ['qPCR', 'LAMP', 'RPA'],
        'true_positive': [85, 78, 82],
        'false_positive': [3, 5, 4],
        'true_negative': [92, 88, 89],
        'false_negative': [5, 9, 7]
    }
    
    df = pd.DataFrame(template_data)
    
    # Create Excel file in memory
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Experiments', index=False)
        
        # Add instructions sheet
        instructions = pd.DataFrame({
            'Column': ['name', 'description', 'technique', 'true_positive', 'false_positive', 'true_negative', 'false_negative'],
            'Description': [
                'Unique name for the experiment',
                'Optional description of the experiment',
                'Amplification technique: qPCR, LAMP, RPA, or NASBA',
                'Number of true positive results',
                'Number of false positive results',
                'Number of true negative results',
                'Number of false negative results'
            ],
            'Required': ['Yes', 'No', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes']
        })
        instructions.to_excel(writer, sheet_name='Instructions', index=False)
    
    excel_buffer.seek(0)
    return excel_buffer.getvalue()

def validate_confusion_matrix_data(tp: int, fp: int, tn: int, fn: int) -> Dict[str, str]:
    """
    Validate confusion matrix data and return any warnings or errors
    
    Args:
        tp, fp, tn, fn: Confusion matrix values
    
    Returns:
        dict: Validation results with warnings and errors
    """
    
    warnings = []
    errors = []
    
    # Check for negative values
    if any(val < 0 for val in [tp, fp, tn, fn]):
        errors.append("All confusion matrix values must be non-negative")
    
    # Check for zero total
    total = tp + fp + tn + fn
    if total == 0:
        errors.append("At least one confusion matrix value must be greater than zero")
    
    # Check for unusual patterns
    if total > 0:
        # Very small sample size
        if total < 10:
            warnings.append(f"Small sample size (n={total}) may lead to unreliable statistical estimates")
        
        # Unusual distribution warnings
        positive_count = tp + fn
        negative_count = fp + tn
        
        if positive_count == 0:
            warnings.append("No positive cases in the dataset")
        elif negative_count == 0:
            warnings.append("No negative cases in the dataset")
        
        # Check for extreme imbalance
        if positive_count > 0 and negative_count > 0:
            ratio = max(positive_count, negative_count) / min(positive_count, negative_count)
            if ratio > 10:
                warnings.append(f"Highly imbalanced dataset (ratio: {ratio:.1f}:1)")
        
        # Check for perfect classification
        if fp == 0 and fn == 0:
            warnings.append("Perfect classification detected - verify data accuracy")
        
        # Check for no correct classifications
        if tp == 0 and tn == 0:
            warnings.append("No correct classifications detected - verify data accuracy")
    
    return {
        'errors': errors,
        'warnings': warnings,
        'is_valid': len(errors) == 0
    }

def batch_validate_experiments(experiments_data: List[Dict]) -> Dict:
    """
    Validate a batch of experiment data
    
    Args:
        experiments_data: List of experiment dictionaries
    
    Returns:
        dict: Batch validation results
    """
    
    valid_experiments = []
    invalid_experiments = []
    warnings_summary = []
    
    for i, exp_data in enumerate(experiments_data):
        validation = validate_confusion_matrix_data(
            exp_data['tp'], exp_data['fp'], 
            exp_data['tn'], exp_data['fn']
        )
        
        if validation['is_valid']:
            valid_experiments.append(exp_data)
            if validation['warnings']:
                warnings_summary.extend([f"Experiment {i+1}: {w}" for w in validation['warnings']])
        else:
            invalid_experiments.append({
                'experiment': exp_data,
                'errors': validation['errors']
            })
    
    return {
        'valid_count': len(valid_experiments),
        'invalid_count': len(invalid_experiments),
        'valid_experiments': valid_experiments,
        'invalid_experiments': invalid_experiments,
        'warnings': warnings_summary,
        'success_rate': len(valid_experiments) / len(experiments_data) if experiments_data else 0
    }
