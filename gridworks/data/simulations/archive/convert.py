import numpy as np
import csv
from datetime import datetime
import pandas as pd

# Open the file in read mode
with open('convert_me.txt', 'r') as file:
    # Read the content of the file
    text = file.read()

#text = input("Your text:")
#text = "0h-1h: [1, 1, 1]\n1h-2h: [1, 1, 1]\n2h-3h: [1, 1, 1]\n3h-4h: [1, 1, 1]\n4h-5h: [1, 1, 1]\n5h-6h: [1, 1, 1]\n6h-7h: [1, 1, 1]\n7h-8h: [0, 0, 0]"

dict = {}
for i in range(8):
    #print(text[17*i:17*(i+1)].replace(" ","").replace("\n","").split(":")[1])
    dict[f'combi{i+1}'] = text[17*i:17*(i+1)].replace(" ","").replace("\n","").split(":")[1]
    
if_statement = "if iter==0: sequence = "

print("")
print(if_statement)
print(dict)
print("")
