import os
import sys

# Path to your virtual environment
VENV = os.path.expanduser(u'/home/your_cpanel_username/virtualenv/your_project_folder/3.9/bin/python')
if sys.executable != VENV:
    os.execl(VENV, VENV, *sys.argv)

# Add your project directory to the sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings_prod'

# Create `application` callable object
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 