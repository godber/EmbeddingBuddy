"""
WSGI entry point for production deployment.
Use this with a production WSGI server like Gunicorn.
"""

from embeddingbuddy.app import create_app

# Create the application instance
application = create_app()

# For compatibility with different WSGI servers
app = application
