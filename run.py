from app import create_app
from app.config.config import ProductionConfig
import os

class CustomProductionConfig(ProductionConfig):
    WTF_CSRF_ENABLED = True
    WTF_CSRF_CHECK_DEFAULT = True
    WTF_CSRF_SSL_STRICT = False
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_CSRF_TRUSTED_ORIGINS = [
        'https://*.vercel.app',
        'http://localhost:5000',
        'http://127.0.0.1:5000',
        'https://sqhpctrack.vercel.app'
    ]
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

app = create_app(CustomProductionConfig)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', 
            port=port,
            debug=False,
            ssl_context=None)
