import pandas as pd

file_path = 'drug_intersection.xlsx'
sheet_name = 'drugs_1'

df_drug_1 = pd.read_excel(file_path, sheet_name=sheet_name)



print(df_drug_1.head(200))