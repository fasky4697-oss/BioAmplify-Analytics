import numpy as np
from typing import Dict, List

# Cost data based on real market research from web sources (in THB, ~35 THB = 1 USD)
TECHNIQUE_COSTS = {
    'PCR': {
        'equipment_cost': 525000,  # Basic PCR thermocycler
        'equipment_cost_range': (280000, 875000),
        'reagent_cost_per_test': 87.5,
        'reagent_cost_range': (52.5, 140),
        'maintenance_cost_annual': 52500,
        'power_consumption_watts': 800,
        'throughput_samples_per_hour': 48,
        'operator_skill_required': 'Medium',
        'temperature_requirement': 'Thermal cycling (50-95°C)',
        'time_per_test_minutes': 150,
        'multiplexing_capability': 'Good',
        'field_suitability': 'Poor'
    },
    'qPCR': {
        'equipment_cost': 1225000,  # Average cost in THB
        'equipment_cost_range': (525000, 1750000),
        'reagent_cost_per_test': 192.5,  # Average cost per test
        'reagent_cost_range': (105, 280),
        'maintenance_cost_annual': 122500,
        'power_consumption_watts': 1500,  # High due to thermal cycling
        'throughput_samples_per_hour': 96,
        'operator_skill_required': 'High',
        'temperature_requirement': 'Thermal cycling (50-94°C)',
        'time_per_test_minutes': 120,
        'multiplexing_capability': 'Excellent',
        'field_suitability': 'Poor'
    },
    'LAMP': {
        'equipment_cost': 87500,  # Much lower cost
        'equipment_cost_range': (5600, 175000),
        'reagent_cost_per_test': 105.0,  # Lower reagent costs
        'reagent_cost_range': (70, 140),
        'maintenance_cost_annual': 8750,
        'power_consumption_watts': 50,  # Low power consumption
        'throughput_samples_per_hour': 24,
        'operator_skill_required': 'Medium',
        'temperature_requirement': 'Isothermal 60-65°C',
        'time_per_test_minutes': 45,
        'multiplexing_capability': 'Limited',
        'field_suitability': 'Good'
    },
    'RPA': {
        'equipment_cost': 35000,  # Lowest equipment cost
        'equipment_cost_range': (7000, 70000),
        'reagent_cost_per_test': 402.5,  # Highest reagent cost (TwistDx monopoly)
        'reagent_cost_range': (280, 525),
        'maintenance_cost_annual': 3500,
        'power_consumption_watts': 20,  # Very low power
        'throughput_samples_per_hour': 12,
        'operator_skill_required': 'Low',
        'temperature_requirement': 'Low isothermal 37-42°C',
        'time_per_test_minutes': 15,
        'multiplexing_capability': 'Good',
        'field_suitability': 'Excellent'
    },
    'NASBA': {
        'equipment_cost': 52500,
        'equipment_cost_range': (17500, 105000),
        'reagent_cost_per_test': 297.5,
        'reagent_cost_range': (175, 420),
        'maintenance_cost_annual': 10500,
        'power_consumption_watts': 100,
        'throughput_samples_per_hour': 16,
        'operator_skill_required': 'Medium',
        'temperature_requirement': 'Isothermal 41°C',
        'time_per_test_minutes': 90,
        'multiplexing_capability': 'Moderate',
        'field_suitability': 'Moderate'
    },
    'TMA': {  # Transcription-Mediated Amplification
        'equipment_cost': 280000,
        'equipment_cost_range': (175000, 420000),
        'reagent_cost_per_test': 245.0,
        'reagent_cost_range': (175, 350),
        'maintenance_cost_annual': 14000,
        'power_consumption_watts': 200,
        'throughput_samples_per_hour': 20,
        'operator_skill_required': 'Medium',
        'temperature_requirement': 'Isothermal 42°C',
        'time_per_test_minutes': 60,
        'multiplexing_capability': 'Limited',
        'field_suitability': 'Good'
    },
    'HDA': {  # Helicase-Dependent Amplification
        'equipment_cost': 3000,
        'equipment_cost_range': (1500, 5000),
        'reagent_cost_per_test': 4.5,
        'reagent_cost_range': (3, 6),
        'maintenance_cost_annual': 200,
        'power_consumption_watts': 80,
        'throughput_samples_per_hour': 18,
        'operator_skill_required': 'Low',
        'temperature_requirement': 'Isothermal 65°C',
        'time_per_test_minutes': 75,
        'multiplexing_capability': 'Moderate',
        'field_suitability': 'Good'
    },
    'SDA': {  # Strand Displacement Amplification
        'equipment_cost': 4000,
        'equipment_cost_range': (2000, 6000),
        'reagent_cost_per_test': 6.0,
        'reagent_cost_range': (4, 8),
        'maintenance_cost_annual': 300,
        'power_consumption_watts': 120,
        'throughput_samples_per_hour': 15,
        'operator_skill_required': 'Medium',
        'temperature_requirement': 'Isothermal 37°C',
        'time_per_test_minutes': 120,
        'multiplexing_capability': 'Limited',
        'field_suitability': 'Moderate'
    },
    'NEAR': {  # Nicking Enzyme Amplification Reaction
        'equipment_cost': 2500,
        'equipment_cost_range': (1000, 4000),
        'reagent_cost_per_test': 5.5,
        'reagent_cost_range': (4, 7),
        'maintenance_cost_annual': 150,
        'power_consumption_watts': 60,
        'throughput_samples_per_hour': 12,
        'operator_skill_required': 'Low',
        'temperature_requirement': 'Isothermal 55°C',
        'time_per_test_minutes': 90,
        'multiplexing_capability': 'Limited',
        'field_suitability': 'Excellent'
    }
}

def get_technique_costs(technique: str) -> Dict:
    """
    Get cost data for a specific amplification technique
    
    Args:
        technique: Name of the technique (qPCR, LAMP, RPA, NASBA)
    
    Returns:
        dict: Cost and performance data for the technique
    """
    
    if technique not in TECHNIQUE_COSTS:
        raise ValueError(f"Unknown technique: {technique}")
    
    return TECHNIQUE_COSTS[technique].copy()

def calculate_total_cost(technique: str, sample_count: int, study_duration_years: float = 1.0) -> float:
    """
    Calculate total cost of ownership for a technique over a study period
    
    Args:
        technique: Name of the technique
        sample_count: Total number of samples to process
        study_duration_years: Duration of study in years
    
    Returns:
        float: Total cost in THB
    """
    
    cost_data = get_technique_costs(technique)
    
    # Equipment cost (amortized over 5 years typical lifespan)
    equipment_annual_cost = cost_data['equipment_cost'] / 5
    equipment_cost_study = equipment_annual_cost * study_duration_years
    
    # Reagent costs
    reagent_cost_total = cost_data['reagent_cost_per_test'] * sample_count
    
    # Maintenance costs
    maintenance_cost_study = cost_data['maintenance_cost_annual'] * study_duration_years
    
    # Power costs (assuming 4.2 THB/kWh, typical Thai electricity rate)
    power_cost_per_kwh = 4.2
    time_per_test_hours = cost_data['time_per_test_minutes'] / 60
    power_cost_total = (cost_data['power_consumption_watts'] / 1000) * time_per_test_hours * sample_count * power_cost_per_kwh
    
    total_cost = equipment_cost_study + reagent_cost_total + maintenance_cost_study + power_cost_total
    
    return round(total_cost, 2)

def compare_technique_costs(techniques: List[str], sample_count: int, study_duration_years: float = 1.0) -> Dict:
    """
    Compare costs across multiple techniques
    
    Args:
        techniques: List of technique names
        sample_count: Number of samples
        study_duration_years: Study duration
    
    Returns:
        dict: Comparison results with cost breakdown
    """
    
    comparison = {}
    
    for technique in techniques:
        if technique not in TECHNIQUE_COSTS:
            continue
            
        cost_data = get_technique_costs(technique)
        total_cost = calculate_total_cost(technique, sample_count, study_duration_years)
        
        # Calculate cost per sample
        cost_per_sample = total_cost / sample_count if sample_count > 0 else 0
        
        # Calculate component costs
        equipment_annual_cost = cost_data['equipment_cost'] / 5
        equipment_cost_study = equipment_annual_cost * study_duration_years
        reagent_cost_total = cost_data['reagent_cost_per_test'] * sample_count
        maintenance_cost_study = cost_data['maintenance_cost_annual'] * study_duration_years
        
        time_per_test_hours = cost_data['time_per_test_minutes'] / 60
        power_cost_total = (cost_data['power_consumption_watts'] / 1000) * time_per_test_hours * sample_count * 4.2
        
        comparison[technique] = {
            'total_cost': total_cost,
            'cost_per_sample': cost_per_sample,
            'cost_breakdown': {
                'equipment': equipment_cost_study,
                'reagents': reagent_cost_total,
                'maintenance': maintenance_cost_study,
                'power': power_cost_total
            },
            'performance_metrics': {
                'time_per_test': cost_data['time_per_test_minutes'],
                'throughput_per_hour': cost_data['throughput_samples_per_hour'],
                'field_suitability': cost_data['field_suitability'],
                'operator_skill': cost_data['operator_skill_required']
            }
        }
    
    return comparison

def calculate_cost_effectiveness(technique: str, sensitivity: float, specificity: float, sample_count: int) -> Dict:
    """
    Calculate cost-effectiveness metrics incorporating diagnostic performance
    
    Args:
        technique: Technique name
        sensitivity: Diagnostic sensitivity (0-1)
        specificity: Diagnostic specificity (0-1)
        sample_count: Number of samples
    
    Returns:
        dict: Cost-effectiveness analysis
    """
    
    total_cost = calculate_total_cost(technique, sample_count)
    cost_per_sample = total_cost / sample_count if sample_count > 0 else 0
    
    # Calculate diagnostic utility score (weighted average of sensitivity and specificity)
    diagnostic_utility = (sensitivity + specificity) / 2
    
    # Cost per unit of diagnostic utility
    cost_per_utility = cost_per_sample / diagnostic_utility if diagnostic_utility > 0 else float('inf')
    
    # Calculate costs of misclassification (simplified model)
    # Assume false positive costs $100 in unnecessary treatment
    # Assume false negative costs $500 in missed diagnosis
    fp_cost_per_error = 100
    fn_cost_per_error = 500
    
    # Estimate error rates (simplified)
    fp_rate = 1 - specificity
    fn_rate = 1 - sensitivity
    
    # Expected misclassification costs per sample
    expected_fp_cost = fp_rate * fp_cost_per_error
    expected_fn_cost = fn_rate * fn_cost_per_error
    total_expected_error_cost = expected_fp_cost + expected_fn_cost
    
    # Total cost including misclassification
    total_cost_with_errors = cost_per_sample + total_expected_error_cost
    
    return {
        'technique': technique,
        'direct_cost_per_sample': cost_per_sample,
        'diagnostic_utility_score': diagnostic_utility,
        'cost_per_utility_unit': cost_per_utility,
        'misclassification_costs': {
            'false_positive_cost': expected_fp_cost,
            'false_negative_cost': expected_fn_cost,
            'total_error_cost': total_expected_error_cost
        },
        'total_cost_with_errors': total_cost_with_errors,
        'cost_effectiveness_rank': None  # To be filled when comparing multiple techniques
    }

def rank_techniques_by_cost_effectiveness(techniques_data: List[Dict]) -> List[Dict]:
    """
    Rank techniques by cost-effectiveness
    
    Args:
        techniques_data: List of cost-effectiveness dictionaries
    
    Returns:
        list: Ranked list of techniques
    """
    
    # Sort by total cost with errors (lower is better)
    ranked = sorted(techniques_data, key=lambda x: x['total_cost_with_errors'])
    
    # Add ranking
    for i, technique_data in enumerate(ranked):
        technique_data['cost_effectiveness_rank'] = i + 1
    
    return ranked

def generate_cost_summary(techniques: List[str], sample_counts: List[int]) -> Dict:
    """
    Generate comprehensive cost summary for different scenarios
    
    Args:
        techniques: List of techniques to analyze
        sample_counts: List of sample count scenarios
    
    Returns:
        dict: Comprehensive cost analysis
    """
    
    summary = {
        'scenarios': {},
        'technique_comparison': {},
        'recommendations': {}
    }
    
    for sample_count in sample_counts:
        scenario_name = f"{sample_count}_samples"
        comparison = compare_technique_costs(techniques, sample_count)
        summary['scenarios'][scenario_name] = comparison
        
        # Find most cost-effective technique for this scenario
        min_cost_technique = min(comparison.keys(), key=lambda t: comparison[t]['total_cost'])
        summary['recommendations'][scenario_name] = {
            'most_cost_effective': min_cost_technique,
            'cost_savings_vs_most_expensive': max(comparison[t]['total_cost'] for t in comparison) - comparison[min_cost_technique]['total_cost']
        }
    
    # Overall technique characteristics
    for technique in techniques:
        if technique in TECHNIQUE_COSTS:
            cost_data = get_technique_costs(technique)
            summary['technique_comparison'][technique] = {
                'equipment_cost': cost_data['equipment_cost'],
                'reagent_cost_per_test': cost_data['reagent_cost_per_test'],
                'strengths': get_technique_strengths(technique),
                'limitations': get_technique_limitations(technique)
            }
    
    return summary

def get_technique_strengths(technique: str) -> List[str]:
    """Get key strengths of a technique"""
    strengths_map = {
        'PCR': [
            'Well-established and widely used',
            'Simple and reliable',
            'Low equipment cost compared to qPCR',
            'Good for qualitative analysis',
            'Extensive literature and protocols'
        ],
        'qPCR': [
            'Gold standard for sensitivity',
            'Excellent multiplexing capability',
            'Quantitative results',
            'Well-established protocols',
            'Wide acceptance in clinical settings'
        ],
        'LAMP': [
            'Low equipment costs',
            'Good cost per test',
            'Simple isothermal operation',
            'Rapid results (15-60 min)',
            'Good field suitability'
        ],
        'RPA': [
            'Fastest results (5-20 min)',
            'Works at body temperature',
            'Minimal equipment required',
            'Excellent portability',
            'High sensitivity'
        ],
        'NASBA': [
            'RNA amplification without reverse transcription',
            'Isothermal operation',
            'Good for viral RNA detection',
            'Moderate equipment costs'
        ],
        'TMA': [
            'RNA amplification at low temperature',
            'High sensitivity for RNA targets',
            'Simple automation potential',
            'Good for clinical diagnostics'
        ],
        'HDA': [
            'Simple enzyme requirements',
            'Good temperature tolerance',
            'Fast amplification',
            'Cost-effective equipment'
        ],
        'SDA': [
            'Isothermal amplification',
            'Good specificity',
            'Well-established protocols',
            'Suitable for automation'
        ],
        'NEAR': [
            'Very simple equipment',
            'Visual detection possible',
            'Excellent portability',
            'Low power consumption'
        ]
    }
    return strengths_map.get(technique, [])

def get_technique_limitations(technique: str) -> List[str]:
    """Get key limitations of a technique"""
    limitations_map = {
        'PCR': [
            'No quantitative results',
            'Requires gel electrophoresis',
            'Thermal cycling required',
            'Time-consuming post-PCR analysis',
            'Limited throughput'
        ],
        'qPCR': [
            'High equipment costs',
            'Requires thermal cycling',
            'High power consumption',
            'Not suitable for field use',
            'Requires skilled operators'
        ],
        'LAMP': [
            'Complex primer design',
            'Limited multiplexing',
            'Potential for primer-dimer formation',
            'Less established than qPCR'
        ],
        'RPA': [
            'Highest reagent costs',
            'Proprietary enzyme system',
            'Limited supplier options',
            'Temperature sensitive'
        ],
        'NASBA': [
            'Limited to RNA targets',
            'Moderate equipment costs',
            'Less widely adopted',
            'Requires multiple enzymes'
        ],
        'TMA': [
            'Limited to RNA targets',
            'Requires multiple enzymes',
            'Less established than other methods',
            'Moderate reagent costs'
        ],
        'HDA': [
            'Slower than RPA',
            'Limited multiplexing',
            'Newer technology',
            'Requires helicase enzyme'
        ],
        'SDA': [
            'Complex primer design',
            'Requires nicking enzymes',
            'Limited temperature range',
            'Moderate costs'
        ],
        'NEAR': [
            'Limited commercial availability',
            'Newer technology',
            'Limited multiplexing',
            'Requires specialized primers'
        ]
    }
    return limitations_map.get(technique, [])
