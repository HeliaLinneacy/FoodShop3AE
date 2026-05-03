"""
WSGI config for snack_shop project.
"""

import os
from django.core.wsgi import get_wsgi_application

# Tự động dùng settings_railway khi chạy trên Railway
# Railway luôn set biến RAILWAY_ENVIRONMENT hoặc RAILWAY_PROJECT_ID
IS_RAILWAY = bool(
    os.environ.get('RAILWAY_ENVIRONMENT') or
    os.environ.get('RAILWAY_PROJECT_ID') or
    os.environ.get('RAILWAY_SERVICE_NAME')
)

if IS_RAILWAY:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'snack_shop.settings_railway')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'snack_shop.settings')

application = get_wsgi_application()
