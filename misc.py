import pandas as pd
import os

def create_description(description_csv_fn, output_path):
    description_df = pd.read_csv(description_csv_fn, index_col = False, header = 0)
    array_cols = ['Authors', 'ReferencesAndLinks']
    for col in array_cols:
        try:
            description_df[col].iloc[0] = description_df[col].tolist()
        except:
            print('{} empty. Not writing into json.'.format(col))
    output_fn = os.path.join(output_path, 'dataset_description.json')
    description_df.dropna(axis = 1, inplace = True, how = 'all')
    description_df.iloc[0].to_json(output_fn)
