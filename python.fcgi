#!/home/your_cpanel_username/virtualenv/your_project_folder/3.9/bin/python
import os
import sys

# Add the project directory to the sys.path
project_home = os.path.dirname(os.path.realpath(__file__))
if project_home not in sys.path:
    sys.path.append(project_home)

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings_prod'

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

from django.core.wsgi import get_wsgi_application
from flup.server.fcgi import WSGIServer

# Create the WSGI application
application = get_wsgi_application()

if __name__ == '__main__':
    WSGIServer(application).run() 