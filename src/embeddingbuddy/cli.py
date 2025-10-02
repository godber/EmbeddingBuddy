"""
Lightweight CLI entry point for EmbeddingBuddy.

This module provides a fast command-line interface that only imports
heavy dependencies when actually needed by subcommands.
"""

import argparse
import sys


def main():
    """Main CLI entry point with minimal imports for fast help text."""
    parser = argparse.ArgumentParser(
        prog="embeddingbuddy",
        description="EmbeddingBuddy - Interactive embedding visualization tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  embeddingbuddy serve                    # Production mode (no debug, no auto-reload)
  embeddingbuddy serve --dev              # Development mode (debug + auto-reload)
  embeddingbuddy serve --debug            # Debug logging only (no auto-reload)
  embeddingbuddy serve --port 8080        # Custom port
  embeddingbuddy serve --host 0.0.0.0     # Bind to all interfaces
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", metavar="<command>"
    )

    # Serve subcommand
    serve_parser = subparsers.add_parser(
        "serve",
        help="Start the web server",
        description="Start the EmbeddingBuddy web server for interactive visualization",
    )
    serve_parser.add_argument(
        "--host", default=None, help="Host to bind to (default: 127.0.0.1)"
    )
    serve_parser.add_argument(
        "--port", type=int, default=None, help="Port to bind to (default: 8050)"
    )
    serve_parser.add_argument(
        "--dev",
        action="store_true",
        help="Development mode: enable debug logging and auto-reload",
    )
    serve_parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging (no auto-reload)"
    )

    args = parser.parse_args()

    if args.command == "serve":
        # Only import heavy dependencies when actually running serve
        from embeddingbuddy.app import serve

        serve(host=args.host, port=args.port, dev=args.dev, debug=args.debug)
    else:
        # No command specified, show help
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
