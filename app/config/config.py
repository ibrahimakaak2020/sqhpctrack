import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
  
    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site99.db'
    MYSQL_DATABASE_URI = os.environ.get('MYSQL_DATABASE_URL') or 'mysql://user:password@localhost/dbname'
    POSTGRESQL_DATABASE_URI = os.environ.get('POSTGRESQL_DATABASE_URL') or 'postgresql://user:password@localhost/dbname'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Login config
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    
    # Other configurations
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
  
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    # Add production-specific settings here

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class MySQLConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = Config.MYSQL_DATABASE_URI
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 30

class PostgreSQLConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = Config.POSTGRESQL_DATABASE_URI
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_MAX_OVERFLOW = 20

# Configuration dictionary
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'mysql': MySQLConfig,
    'postgresql': PostgreSQLConfig,
    'default': DevelopmentConfig
}