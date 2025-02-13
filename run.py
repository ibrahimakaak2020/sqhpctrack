from app import create_app
from app.config.config import ProductionConfig
import os
from datetime import timedelta
from app import app


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        ssl_context=None
    )
