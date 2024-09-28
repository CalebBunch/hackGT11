from . import create_app

# NOTE: this is bad practice
API_KEY = "sk.eyJ1IjoiY2J1bmNoIiwiYSI6ImNtMWxkdHRhNDA3eWgyam92b3ByMmJzMm0ifQ.2ZWLAmAditf8rkHwAEonWA"

def main() -> None:
    app = create_app()
    app.run()

if __name__ == "__main__":
    main()

