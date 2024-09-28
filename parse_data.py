from os import error
import pandas as pd

CRIME_PATH = "data/crime_data.csv"
CRIME_OUTPUT_PATH = "data/cleaned/cleaned_crime_data.csv"
ROADS_PATH = "data/pavement_condition_index.csv"
ROADS_OUTPUT_PATH = "data/cleaned/cleaned_pavement_condition_index.csv"

def parse_crime_csv():
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

    df.to_csv(CRIME_OUTPUT_PATH, index=False)


def parse_roads_csv():
    # street name, from street, to street, Pavement Condition Index, Surface Distress Index, Roughness Index
    # 0-25(very poor), 26-40(poor), 41-50(marginal), 51-60(fair), 61-70(good), 71-85(very good), 86-100(excellent)
    df = pd.read_csv(ROADS_PATH)

    keep = ["Street Name", "From Street Name", "To Street Name", "Surface Distress Index", "Roughness Index", "Condition Rating"]
    
    df_filtered = df[keep]

    print("Remaining columns:", df_filtered.columns.tolist())
    df_filtered.sort_values(by=["Street Name"], inplace=True)
    
    print(df_filtered.head().to_string())

    df_filtered.to_csv(ROADS_OUTPUT_PATH, index=False)

