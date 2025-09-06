# BioAmplify Analytics

## Overview

BioAmplify Analytics is a comprehensive bioinformatics web application designed for comparing and analyzing nucleic acid amplification techniques (qPCR, LAMP, RPA, NASBA). The platform provides statistical analysis, cost comparison, and diagnostic performance evaluation for experimental data. Users can input experimental results through manual entry or file upload, and receive detailed reports with confusion matrix analysis, diagnostic statistics (sensitivity, specificity, PPV, NPV), Cohen's Kappa calculations, and cost-effectiveness comparisons.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Flask-based application** with SQLAlchemy ORM for database operations
- **Template-driven frontend** using Jinja2 templates with Bootstrap 5 for responsive UI
- **Modular route structure** separating concerns between data input, analysis, and reporting
- **Session-based user interaction** with flash messaging for user feedback

### Database Design
- **SQLAlchemy with SQLite** as the default database (configurable via DATABASE_URL environment variable)
- **Two main models**: Experiment (storing individual test results and confusion matrix data) and ComparisonStudy (for multi-technique comparisons)
- **JSON storage for calculated statistics** within the database for flexible data retrieval
- **Automatic table creation** on application startup

### Data Processing Pipeline
- **Manual data entry** through web forms with real-time validation
- **File upload support** for CSV/Excel batch processing using pandas
- **Confusion matrix validation** ensuring data integrity before statistical calculations
- **Cost analysis integration** with predefined technique cost models

### Statistical Analysis Engine
- **Comprehensive diagnostic statistics** calculation (sensitivity, specificity, PPV, NPV, accuracy)
- **Cohen's Kappa implementation** for inter-rater reliability assessment
- **Cost-effectiveness analysis** comparing equipment costs, reagent costs, and operational expenses
- **Report generation** in PDF and Excel formats using ReportLab and pandas

### Frontend Architecture
- **Bootstrap 5 dark theme** with responsive design patterns
- **Chart.js integration** for data visualization and confusion matrix display
- **DataTables** for sortable, searchable experiment listings
- **Tab-based navigation** for different input methods and analysis views
- **AJAX-ready structure** for future real-time updates

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web framework with SQLAlchemy for database ORM
- **pandas**: Data processing and Excel/CSV file handling
- **numpy**: Numerical computations for statistical analysis
- **scipy**: Advanced statistical functions and hypothesis testing

### Data Visualization
- **Chart.js**: Client-side charting for confusion matrices and cost comparisons
- **matplotlib/seaborn**: Server-side chart generation for PDF reports
- **Bootstrap 5**: UI framework with dark theme support

### File Processing & Reporting
- **ReportLab**: PDF report generation with charts and tables
- **openpyxl**: Excel file reading/writing capabilities
- **Werkzeug**: File upload handling and validation

### Frontend Libraries
- **DataTables**: Enhanced table functionality with sorting and search
- **Font Awesome**: Icon library for consistent UI elements
- **Bootstrap JavaScript**: Interactive components and responsive behavior

### Development & Deployment
- **SQLite**: Default database (production can use PostgreSQL via DATABASE_URL)
- **Logging**: Built-in Python logging for debugging and monitoring
- **Environment variables**: Configuration management for secrets and database URLs