release: DJANGO_SETTINGS_MODULE=snack_shop.settings_railway python manage.py migrate --noinput
web: DJANGO_SETTINGS_MODULE=snack_shop.settings_railway gunicorn snack_shop.wsgi:application --bind 0.0.0.0:$PORT
