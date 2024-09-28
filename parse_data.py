import pandas as pd

CRIME_PATH = "data/crime_data.csv"
OUTPUT_PATH = "data/cleaned_crime_data.csv"

def parse_csv():
    df = pd.read_csv(CRIME_PATH, low_memory=False)
    columns_to_drop = [
        "Report Number", "Report Date", "Location", "Offense Start Date",
        "Offense End Date", "Social Media", "Victim Count", "Day of the week",
        "Watch", "Day Number", "Zone", "Beat", "Neighborhood", "NPU",
        "Council District", "Press Release", "OBJECTID", "Location Type",
        "Crime Against", "Was a firearm involved?", "UCR Grouping",
        "GlobalID", "x", "y", "NIBRS Code"
    ]

    df.drop(columns=columns_to_drop, inplace=True, errors="ignore")
    print("Remaining columns:", df.columns.tolist())
    
    df.sort_values(by=['Longitude', 'Latitude'], inplace=True)
    
    print(df.head().to_string())
    unique_nibrs_count = df["NIBRS Code Name"].nunique()
    print(f"Number of unique NIBRS code names: {unique_nibrs_count}")

    df.to_csv(OUTPUT_PATH, index=False)

