"""Réglages de développement local (SQLite, hors Docker).
Ne pas utiliser en production : la stack officielle reste config.settings + PostgreSQL/PostGIS via docker-compose.
Usage : DJANGO_SETTINGS_MODULE=dev_settings python manage.py <commande>
"""
from config.settings import *
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'dev_db.sqlite3'}}
CORS_ALLOWED_ORIGINS=['http://localhost:5173']
ALLOWED_HOSTS=['*']
DEBUG=True
