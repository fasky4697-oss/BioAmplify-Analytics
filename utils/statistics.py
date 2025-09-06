import numpy as np
from scipy import stats
from sklearn.metrics import cohen_kappa_score
import math

def calculate_diagnostic_stats(tp, fp, tn, fn, confidence=0.95):
    """
    Calculate diagnostic statistics from confusion matrix values
    
    Args:
        tp: True Positives
        fp: False Positives  
        tn: True Negatives
        fn: False Negatives
        confidence: Confidence level for intervals (default 0.95)
    
    Returns:
        dict: Dictionary containing all diagnostic statistics
    """
    
    # Basic validation
    if tp + fp + tn + fn == 0:
        raise ValueError("All confusion matrix values cannot be zero")
    
    # Calculate basic metrics
    total = tp + fp + tn + fn
    
    # Sensitivity (True Positive Rate, Recall)
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    # Specificity (True Negative Rate)
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    # Positive Predictive Value (Precision)
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    
    # Negative Predictive Value
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    
    # Accuracy
    accuracy = (tp + tn) / total
    
    # Prevalence
    prevalence = (tp + fn) / total
    
    # False Positive Rate
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    
    # False Negative Rate
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
    
    # Likelihood Ratios
    lr_positive = sensitivity / fpr if fpr > 0 else float('inf')
    lr_negative = fnr / specificity if specificity > 0 else float('inf')
    
    # Diagnostic Odds Ratio
    dor = lr_positive / lr_negative if lr_negative > 0 else float('inf')
    
    # F1 Score
    f1_score = 2 * (ppv * sensitivity) / (ppv + sensitivity) if (ppv + sensitivity) > 0 else 0
    
    # Matthews Correlation Coefficient
    mcc_numerator = (tp * tn) - (fp * fn)
    mcc_denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = mcc_numerator / mcc_denominator if mcc_denominator > 0 else 0
    
    # Calculate confidence intervals using Wilson score interval
    def wilson_ci(x, n, conf_level=confidence):
        """Calculate Wilson score confidence interval"""
        if n == 0:
            return (0, 0)
        
        z = stats.norm.ppf((1 + conf_level) / 2)
        p = x / n
        
        center = (p + z*z/(2*n)) / (1 + z*z/n)
        margin = z * math.sqrt((p*(1-p) + z*z/(4*n)) / n) / (1 + z*z/n)
        
        return (max(0, center - margin), min(1, center + margin))
    
    # Calculate confidence intervals
    sensitivity_ci = wilson_ci(tp, tp + fn)
    specificity_ci = wilson_ci(tn, tn + fp)
    ppv_ci = wilson_ci(tp, tp + fp)
    npv_ci = wilson_ci(tn, tn + fn)
    accuracy_ci = wilson_ci(tp + tn, total)
    
    # Calculate Cohen's Kappa for self-consistency (simulation)
    # For individual experiments, we calculate kappa as agreement between expected and observed
    total_samples = tp + fp + tn + fn
    kappa_value = 0.0
    kappa_ci = (0.0, 0.0)
    kappa_interpretation = "Not calculated"
    
    if total_samples > 0:
        # Calculate observed vs expected agreement as a proxy for Cohen's Kappa
        observed_agreement = (tp + tn) / total_samples
        expected_agreement = ((tp + fn) * (tp + fp) + (tn + fp) * (tn + fn)) / (total_samples * total_samples)
        
        if expected_agreement < 1.0:
            kappa_value = (observed_agreement - expected_agreement) / (1 - expected_agreement)
            
            # Simple approximation for kappa confidence interval
            se_kappa = math.sqrt(expected_agreement / (total_samples * (1 - expected_agreement)**2)) if expected_agreement < 1.0 else 0
            z_critical = stats.norm.ppf((1 + confidence) / 2)
            kappa_ci = (
                max(-1.0, kappa_value - z_critical * se_kappa),
                min(1.0, kappa_value + z_critical * se_kappa)
            )
            
            # Interpretation based on Altman scale
            if kappa_value < 0.20:
                kappa_interpretation = "Poor agreement"
            elif kappa_value < 0.40:
                kappa_interpretation = "Fair agreement"
            elif kappa_value < 0.60:
                kappa_interpretation = "Moderate agreement"
            elif kappa_value < 0.80:
                kappa_interpretation = "Good agreement"
            else:
                kappa_interpretation = "Very good agreement"

    return {
        'sensitivity': {
            'value': sensitivity,
            'percentage': sensitivity * 100,
            'ci_lower': sensitivity_ci[0],
            'ci_upper': sensitivity_ci[1]
        },
        'specificity': {
            'value': specificity,
            'percentage': specificity * 100,
            'ci_lower': specificity_ci[0],
            'ci_upper': specificity_ci[1]
        },
        'ppv': {
            'value': ppv,
            'percentage': ppv * 100,
            'ci_lower': ppv_ci[0],
            'ci_upper': ppv_ci[1]
        },
        'npv': {
            'value': npv,
            'percentage': npv * 100,
            'ci_lower': npv_ci[0],
            'ci_upper': npv_ci[1]
        },
        'accuracy': {
            'value': accuracy,
            'percentage': accuracy * 100,
            'ci_lower': accuracy_ci[0],
            'ci_upper': accuracy_ci[1]
        },
        'prevalence': {
            'value': prevalence,
            'percentage': prevalence * 100
        },
        'f1_score': f1_score,
        'mcc': mcc,
        'likelihood_ratios': {
            'positive': lr_positive,
            'negative': lr_negative
        },
        'diagnostic_odds_ratio': dor,
        'cohens_kappa': {
            'value': kappa_value,
            'ci_lower': kappa_ci[0],
            'ci_upper': kappa_ci[1],
            'interpretation': kappa_interpretation
        },
        'sample_size': total,
        'confidence_level': confidence
    }

def calculate_cohens_kappa(rater1, rater2, confidence=0.95):
    """
    Calculate Cohen's Kappa with confidence intervals using GraphPad/Fleiss methodology
    
    Args:
        rater1: Array of ratings from first rater/method
        rater2: Array of ratings from second rater/method
        confidence: Confidence level (default 0.95 for 95% CI)
    
    Returns:
        dict: Kappa value, confidence interval, and interpretation
    """
    
    if len(rater1) != len(rater2):
        raise ValueError("Rater arrays must have the same length")
    
    if len(rater1) == 0:
        raise ValueError("Rater arrays cannot be empty")
    
    # Convert to numpy arrays
    rater1 = np.array(rater1)
    rater2 = np.array(rater2)
    
    # Calculate Cohen's Kappa using sklearn
    kappa = cohen_kappa_score(rater1, rater2)
    
    # Calculate standard error using Fleiss methodology
    n = len(rater1)
    
    # Create contingency table
    categories = np.unique(np.concatenate([rater1, rater2]))
    k = len(categories)
    
    # Build contingency matrix
    contingency = np.zeros((k, k))
    for i, cat1 in enumerate(categories):
        for j, cat2 in enumerate(categories):
            contingency[i, j] = np.sum((rater1 == cat1) & (rater2 == cat2))
    
    # Calculate marginal probabilities
    p_obs = np.trace(contingency) / n  # Observed agreement
    
    row_marginals = np.sum(contingency, axis=1) / n
    col_marginals = np.sum(contingency, axis=0) / n
    p_exp = np.sum(row_marginals * col_marginals)  # Expected agreement
    
    # Standard error calculation (Fleiss method)
    # This is a simplified version - full Fleiss calculation is more complex
    if p_exp == 1:
        se_kappa = 0
    else:
        # Simplified SE calculation
        se_kappa = math.sqrt(p_exp / (n * (1 - p_exp)**2))
    
    # Calculate confidence interval
    z_critical = stats.norm.ppf((1 + confidence) / 2)
    ci_lower = kappa - z_critical * se_kappa
    ci_upper = kappa + z_critical * se_kappa
    
    # Cap upper CI at 1.0 (GraphPad methodology)
    ci_upper = min(1.0, ci_upper)
    
    # Interpretation based on Altman scale
    def interpret_kappa(k):
        if k < 0.20:
            return "Poor agreement"
        elif k < 0.40:
            return "Fair agreement"
        elif k < 0.60:
            return "Moderate agreement"
        elif k < 0.80:
            return "Good agreement"
        else:
            return "Very good agreement"
    
    return {
        'kappa': kappa,
        'confidence_interval': {
            'lower': ci_lower,
            'upper': ci_upper,
            'confidence_level': confidence
        },
        'standard_error': se_kappa,
        'interpretation': interpret_kappa(kappa),
        'sample_size': n,
        'observed_agreement': p_obs,
        'expected_agreement': p_exp
    }

def calculate_multiple_comparisons_correction(p_values, method='bonferroni'):
    """
    Apply multiple comparisons correction to p-values
    
    Args:
        p_values: List of p-values
        method: Correction method ('bonferroni', 'holm', 'fdr_bh')
    
    Returns:
        dict: Corrected p-values and significance results
    """
    
    p_array = np.array(p_values)
    n = len(p_array)
    
    if method == 'bonferroni':
        corrected = p_array * n
        corrected = np.minimum(corrected, 1.0)  # Cap at 1.0
    elif method == 'holm':
        # Holm-Bonferroni method
        sorted_indices = np.argsort(p_array)
        corrected = np.zeros_like(p_array)
        
        for i, idx in enumerate(sorted_indices):
            corrected[idx] = min(1.0, p_array[idx] * (n - i))
            
        # Ensure monotonicity
        sorted_corrected = corrected[sorted_indices]
        for i in range(1, len(sorted_corrected)):
            sorted_corrected[i] = max(sorted_corrected[i], sorted_corrected[i-1])
        corrected[sorted_indices] = sorted_corrected
        
    elif method == 'fdr_bh':
        # Benjamini-Hochberg FDR correction
        sorted_indices = np.argsort(p_array)
        corrected = np.zeros_like(p_array)
        
        for i, idx in enumerate(sorted_indices):
            corrected[idx] = min(1.0, p_array[idx] * n / (i + 1))
            
        # Ensure monotonicity (decreasing)
        sorted_corrected = corrected[sorted_indices]
        for i in range(len(sorted_corrected) - 2, -1, -1):
            sorted_corrected[i] = min(sorted_corrected[i], sorted_corrected[i + 1])
        corrected[sorted_indices] = sorted_corrected
    
    return {
        'original_p_values': p_values,
        'corrected_p_values': corrected.tolist(),
        'method': method,
        'significant_at_05': (corrected < 0.05).tolist(),
        'significant_at_01': (corrected < 0.01).tolist()
    }
