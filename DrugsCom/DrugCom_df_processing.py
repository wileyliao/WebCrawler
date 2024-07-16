import pandas as pd

def load_data(file):
    df = pd.read_excel(file)
    df['interactions_DrugCom'] = df['interactions_DrugCom'].astype(object)
    return df

def save_data(df, file):
    df.to_excel(file, index=False)

def mark_skipped_drugs(df, index, message):
    df.at[index, 'interactions_DrugCom'] = message
