import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level.upper()))

db = SQLAlchemy()

# Create the app
app = Flask(__name__)
# Use environment variable for secret key in production
app.secret_key = os.environ.get("SESSION_SECRET") or os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Configure the database
database_url = os.environ.get("DATABASE_URL", "sqlite:///bioinformatics.db")
# Fix for Render PostgreSQL URL format
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models
    # Import routes after models are registered
    from routes import *
    db.create_all()
