import numpy as np
import csv
from datetime import datetime
import optimizer, forecasts, plot, functions

import pandas as pd

# Assuming df1 and df2 are your DataFrames from CSV files
df1 = pd.read_csv('/Users/thomasdefauw/Desktop/repo/gridworks/results_2023-12-22_02-53-34.csv')
df2 = pd.read_csv('/Users/thomasdefauw/Desktop/repo/gridworks/results_2023-12-22_10-52-35.csv')

# Concatenate df2 to df1
df_combined = pd.concat([df1, df2], ignore_index=True)

# Save the combined DataFrame to a new CSV file
df_combined.to_csv('appended_file.csv', index=False)
