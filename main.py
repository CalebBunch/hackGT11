from __init__ import create_app
import pandas as pd

# NOTE: this is bad practice
API_KEY = "sk.eyJ1IjoiY2J1bmNoIiwiYSI6ImNtMWxkdHRhNDA3eWgyam92b3ByMmJzMm0ifQ.2ZWLAmAditf8rkHwAEonWA"

def print_csv():
    df = pd.read_csv("crime_data.csv")
    # print(df.to_string())

def main() -> None:
    print_csv()
    app = create_app()
    app.run(host="0.0.0.0", port=8001)

if __name__ == "__main__":
    main()

