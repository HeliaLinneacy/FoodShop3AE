"""
Django Settings cho Railway/Cloud Deployment
Tự động đọc biến môi trường từ Railway.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Đọc SECRET_KEY từ biến môi trường Railway
SECRET_KEY = os.environ.get('SECRET_KEY', 'thay-bang-key-that-khi-deploy')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    'nguyenducthang.id.vn',
    'www.nguyenducthang.id.vn',
    '.railway.app',   # Cho phép domain Railway
    '*',              # Tạm thời - thu hẹp lại sau khi chạy ổn
]

INSTALLED_APPS = [
    'jazzmin',                       # Phải đứng trước django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'accounts',
    'products',
    'cart',
    'orders',
    'reviews',
    'dashboard',
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Phục vụ static files trên cloud
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'snack_shop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_item_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'snack_shop.wsgi.application'

# ======================================================
# DATABASE
# Railway cung cấp MySQL qua plugin, đọc từ biến môi trường
# ======================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE', 'fs_t5'),
        'USER': os.environ.get('MYSQL_USER', 'root'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
        'HOST': os.environ.get('MYSQL_HOST', 'localhost'),
        'PORT': os.environ.get('MYSQL_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True
DECIMAL_SEPARATOR = ','
THOUSAND_SEPARATOR = '.'
NUMBER_GROUPING = 3

# ======================================================
# STATIC FILES - Dùng WhiteNoise cho cloud deployment
# ======================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'accounts.User'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─────────────────────────────────────────────
# JAZZMIN – Giao diện Admin đẹp
# ─────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    'site_title': 'Ba Anh Em Shop',
    'site_header': 'Ba Anh Em Shop',
    'site_brand': 'Ba Anh Em Shop',
    'welcome_sign': 'Chào mừng đến với trang quản trị',
    'copyright': 'Ba Anh Em Shop © 2026',
    'site_logo': None,
    'site_icon': None,
    'search_model': ['accounts.User', 'products.Snack', 'orders.Order'],
    'user_avatar': None,
    'topmenu_links': [
        {'name': '🏠 Trang chủ shop', 'url': '/', 'new_window': True},
        {'name': '📦 Đơn hàng', 'model': 'orders.Order'},
        {'name': '⭐ Đánh giá', 'model': 'reviews.Review'},
    ],
    'show_sidebar': True,
    'navigation_expanded': True,
    'order_with_respect_to': ['accounts', 'products', 'orders', 'reviews', 'cart'],
    'icons': {
        'auth':               'fas fa-users-cog',
        'accounts.User':      'fas fa-user',
        'products.Category':  'fas fa-tags',
        'products.Snack':     'fas fa-cookie-bite',
        'orders.Order':       'fas fa-shopping-bag',
        'orders.OrderDetail': 'fas fa-list-ul',
        'reviews.Review':     'fas fa-star',
        'cart.Cart':          'fas fa-shopping-cart',
        'cart.CartDetail':    'fas fa-cart-plus',
    },
    'default_icon_parents': 'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-circle',
    'related_modal_active': True,
    'custom_css': None,
    'custom_js': None,
    'use_google_fonts_cdn': True,
    'show_ui_builder': False,   # Tắt trên production
    'changeform_format': 'horizontal_tabs',
    'language_chooser': False,
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text': False,
    'footer_small_text': False,
    'body_small_text': False,
    'brand_small_text': False,
    'brand_colour': 'navbar-danger',
    'accent': 'accent-danger',
    'navbar': 'navbar-danger navbar-dark',
    'no_navbar_border': True,
    'navbar_fixed': True,
    'layout_boxed': False,
    'footer_fixed': False,
    'sidebar_fixed': True,
    'sidebar': 'sidebar-dark-danger',
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent': True,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': False,
    'theme': 'default',
    'dark_mode_theme': None,
    'button_classes': {
        'primary':   'btn-primary',
        'secondary': 'btn-outline-secondary',
        'info':      'btn-outline-info',
        'warning':   'btn-warning',
        'danger':    'btn-danger',
        'success':   'btn-success',
    },
}
