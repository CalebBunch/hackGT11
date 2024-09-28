from __init__ import create_app
import pandas as pd


def print_csv():
    df = pd.read_csv("cleaned_crime_data.csv", low_memory=False)
    print(df.head().to_string())

def main() -> None:
    # print_csv()
    app = create_app()
    app.run(host="0.0.0.0", port=8001)

if __name__ == "__main__":
    main()

