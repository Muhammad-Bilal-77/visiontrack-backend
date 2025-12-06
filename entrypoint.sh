#!/bin/sh
set -e

# Run migrations and collect static files at runtime when env vars are available
python manage.py migrate --no-input
python manage.py collectstatic --no-input

# Start gunicorn
exec gunicorn visiontrack.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60
