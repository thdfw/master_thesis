import numpy as np
import csv
from datetime import datetime
import pandas as pd

first_file = input("Path to first csv file: ").replace(" ","")
second_file = input("Path to second csv file: ").replace(" ","")

# Assuming df1 and df2 are your DataFrames from CSV files
df1 = pd.read_csv(first_file)
df2 = pd.read_csv(second_file)

# Concatenate df2 to df1
df_combined = pd.concat([df1, df2], ignore_index=True)

# Save the combined DataFrame to a new CSV file
df_combined.to_csv('appended_file.csv', index=False)
