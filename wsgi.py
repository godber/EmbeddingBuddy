"""
WSGI entry point for production deployment.
Use this with a production WSGI server like Gunicorn.
"""
from src.embeddingbuddy.app import create_app

# Create the application instance
application = create_app()

# For compatibility with different WSGI servers
app = application

if __name__ == "__main__":
    # This won't be used in production, but useful for testing
    from src.embeddingbuddy.config.settings import AppSettings
    application.run(
        host=AppSettings.HOST,
        port=AppSettings.PORT,
        debug=False
    )