"""
HRMS Portal - WSGI Configuration
WSGI config for hrms_project project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_project.settings')

application = get_wsgi_application()
