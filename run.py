from app import create_app
from app.config.config import ProductionConfig
import os
from datetime import timedelta

class CustomProductionConfig(ProductionConfig):
    # Basic Flask settings
    DEBUG = True
    TESTING = False
    
    # Security settings
    TALISMAN_ENABLED = False
    HTTP_HEADERS = {
        "X-Frame-Options": "ALLOWALL",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-CSRF-Token"
    }
    
    # CORS settings
    ENABLE_CORS = True
    CORS_OPTIONS = {
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "X-CSRF-Token"],
        "expose_headers": ["Content-Type", "X-CSRF-Token"],
        "resources": r"/*",
        "origins": [
            "http://localhost:5000",
            "http://127.0.0.1:5000",
            "https://*.vercel.app",
            "*"  # Remove in production
        ]
    }
    
    # CSRF settings
    WTF_CSRF_ENABLED = False  # Enable in production
    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_SSL_STRICT = False
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Proxy settings
    ENABLE_PROXY_FIX = True
    PROXY_FIX_CONFIG = {
        "x_for": 1,
        "x_proto": 1,
        "x_host": 1,
        "x_port": 1,
        "x_prefix": 1
    }
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_DOMAIN = None

    # Cache settings
    CACHE_CONFIG = {
        'CACHE_TYPE': 'simple',
        'CACHE_DEFAULT_TIMEOUT': 300
    }
    DATA_CACHE_CONFIG = CACHE_CONFIG

app = create_app(CustomProductionConfig)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        ssl_context=None
    )
