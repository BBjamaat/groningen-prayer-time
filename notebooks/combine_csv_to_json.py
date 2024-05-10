# %%
import os
import json

import pandas as pd

# %%
data_dir = '../assets/times/'
files = os.listdir(data_dir)

files_paths = [data_dir+f for f in files if f.endswith('.csv')]
files_paths.sort()
files_paths

# %%
months = ['january', 'february', 'march', 'april', 'may', 'june',
          'july', 'august', 'september', 'october', 'november', 'december']

# %%
data = []
for i, file_path in enumerate(files_paths):
    print(f'Processing {file_path}')
    df = pd.read_csv(file_path, sep=' ')
    data.append({
        'month': i+1,
        'month_name': months[i],
        'data': df.to_dict(orient='records')
    })

data

# %%
with open('../assets/times.json', 'w') as f:
    json.dump(data, f, indent=4)

# %%
