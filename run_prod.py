#!/usr/bin/env python3
"""
Production runner using Gunicorn WSGI server.
This provides better performance and stability for production deployments.
"""
import os
import subprocess
import sys
from src.embeddingbuddy.config.settings import AppSettings

def main():
    """Run the application in production mode with Gunicorn."""
    # Force production settings
    os.environ["EMBEDDINGBUDDY_ENV"] = "production"
    os.environ["EMBEDDINGBUDDY_DEBUG"] = "false"
    
    print("🚀 Starting EmbeddingBuddy in production mode...")
    print(f"⚙️  Workers: {AppSettings.GUNICORN_WORKERS}")
    print(f"🌐 Server will be available at http://{AppSettings.GUNICORN_BIND}")
    print("⏹️  Press Ctrl+C to stop")
    
    # Gunicorn command
    cmd = [
        "gunicorn",
        "--workers", str(AppSettings.GUNICORN_WORKERS),
        "--bind", AppSettings.GUNICORN_BIND,
        "--timeout", str(AppSettings.GUNICORN_TIMEOUT),
        "--keepalive", str(AppSettings.GUNICORN_KEEPALIVE),
        "--access-logfile", "-",
        "--error-logfile", "-",
        "--log-level", "info",
        "wsgi:application"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Gunicorn: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Gunicorn not found. Install it with: uv add gunicorn")
        print("💡 Or run in development mode with: python run_dev.py")
        sys.exit(1)

if __name__ == "__main__":
    main()