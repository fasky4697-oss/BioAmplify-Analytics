from app import db
from datetime import datetime
import json

class Experiment(db.Model):
    """Model for storing experimental data and results"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    technique = db.Column(db.String(50), nullable=False)  # qPCR, RPA, LAMP, NASBA
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Confusion matrix data
    true_positive = db.Column(db.Integer, nullable=False)
    false_positive = db.Column(db.Integer, nullable=False)
    true_negative = db.Column(db.Integer, nullable=False)
    false_negative = db.Column(db.Integer, nullable=False)
    
    # Calculated statistics (stored as JSON)
    statistics = db.Column(db.Text)  # JSON string
    
    # Analysis settings
    confidence_level = db.Column(db.Float, default=0.95)
    
    # Cost analysis
    reagent_cost = db.Column(db.Float)
    equipment_cost = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    
    def __init__(self, name, technique, true_positive, false_positive, true_negative, false_negative, 
                 description='', confidence_level=0.95, reagent_cost=0.0, equipment_cost=0.0, total_cost=0.0):
        """Initialize Experiment with required fields"""
        self.name = name
        self.description = description
        self.technique = technique
        self.true_positive = true_positive
        self.false_positive = false_positive
        self.true_negative = true_negative
        self.false_negative = false_negative
        self.confidence_level = confidence_level
        self.reagent_cost = reagent_cost
        self.equipment_cost = equipment_cost
        self.total_cost = total_cost
    
    def set_statistics(self, stats_dict):
        """Store statistics as JSON string"""
        self.statistics = json.dumps(stats_dict)
    
    def get_statistics(self):
        """Retrieve statistics as dictionary"""
        if self.statistics:
            return json.loads(self.statistics)
        return {}
    
    def get_confusion_matrix(self):
        """Return confusion matrix as 2x2 numpy array"""
        import numpy as np
        return np.array([
            [self.true_positive, self.false_positive],
            [self.false_negative, self.true_negative]
        ])

class ComparisonStudy(db.Model):
    """Model for storing comparison studies between multiple techniques"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Reference to experiments being compared
    experiment_ids = db.Column(db.Text)  # JSON array of experiment IDs
    
    # Cohen's Kappa results
    kappa_results = db.Column(db.Text)  # JSON string
    
    def __init__(self, name, description=''):
        """Initialize ComparisonStudy with required fields"""
        self.name = name
        self.description = description
    
    def set_experiment_ids(self, ids_list):
        """Store experiment IDs as JSON string"""
        self.experiment_ids = json.dumps(ids_list)
    
    def get_experiment_ids(self):
        """Retrieve experiment IDs as list"""
        if self.experiment_ids:
            return json.loads(self.experiment_ids)
        return []
    
    def set_kappa_results(self, kappa_dict):
        """Store kappa results as JSON string"""
        self.kappa_results = json.dumps(kappa_dict)
    
    def get_kappa_results(self):
        """Retrieve kappa results as dictionary"""
        if self.kappa_results:
            return json.loads(self.kappa_results)
        return {}
