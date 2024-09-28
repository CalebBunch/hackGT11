import pandas as pd

file_path = 'pavement_condition_index.csv'  # Update with your file path

df = pd.read_csv(file_path)

columns_to_keep = df.columns[[0, 1, 2, 3, 27, 28, 33]]

df_filtered = df[columns_to_keep]

output_path = 'filtered_pavement_condition_index.csv'
df_filtered.to_csv(output_path, index=False)

print(f"Filtered data has been saved to {output_path}")

# street name, from street, to street, Pavement Condition Index, Surface Distress Index, Roughness Index, Condition Rating
# 0-25(very poor), 26-40(poor), 41-50(marginal), 51-60(fair), 61-70(good), 71-85(very good), 86-100(excellent)
