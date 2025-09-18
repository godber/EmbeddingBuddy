#!/usr/bin/env python3
"""
Development runner with auto-reload enabled.
This runs the Dash development server with hot reloading.
"""
import os
from src.embeddingbuddy.app import create_app, run_app

def main():
    """Run the application in development mode with auto-reload."""
    # Force development settings
    os.environ["EMBEDDINGBUDDY_ENV"] = "development"
    os.environ["EMBEDDINGBUDDY_DEBUG"] = "true"

    # Check for OpenSearch disable flag (optional for testing)
    # Set EMBEDDINGBUDDY_OPENSEARCH_ENABLED=false to test without OpenSearch
    opensearch_status = os.getenv("EMBEDDINGBUDDY_OPENSEARCH_ENABLED", "true")
    opensearch_enabled = opensearch_status.lower() == "true"
    
    print("🚀 Starting EmbeddingBuddy in development mode...")
    print("📁 Auto-reload enabled - changes will trigger restart")
    print("🌐 Server will be available at http://127.0.0.1:8050")
    print(f"🔍 OpenSearch: {'Enabled' if opensearch_enabled else 'Disabled'}")
    print("⏹️  Press Ctrl+C to stop")
    
    app = create_app()
    
    # Run with development server (includes auto-reload when debug=True)
    run_app(app, debug=True)

if __name__ == "__main__":
    main()