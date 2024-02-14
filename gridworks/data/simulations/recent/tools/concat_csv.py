import pandas as pd
import csv

first_file = input("Path to first csv file: ").replace(" ","")
second_file = input("Path to second csv file: ").replace(" ","")

df1 = pd.read_csv(first_file)
df2 = pd.read_csv(second_file)

df_combined = pd.concat([df1, df2], ignore_index=True)
df_combined.to_csv('appended_file.csv', index=False)
