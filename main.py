from src.embeddingbuddy.app import create_app, run_app


def main():
    app = create_app()
    run_app(app)


if __name__ == "__main__":
    main()
