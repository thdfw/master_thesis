import pandas as pd

# Read the CSV file into a DataFrame
file_path = input("\nResults file: ").replace(" ","")
df = pd.read_csv(file_path)

# Delete the first 12 rows
df = df.iloc[12:]

# Write the modified DataFrame back to a CSV file
df.to_csv('modified_file.csv', index=False)
