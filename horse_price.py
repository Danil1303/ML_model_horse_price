import pandas as pd
import os
if not os.path.exists('raw_data'):
    os.makedirs('raw_data')
df= pd.read_csv('equestrian_raw_data.csv')
df1= pd.read_csv('equestrian_raw_data1.csv')
df