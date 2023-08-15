from bs4 import BeautifulSoup
import requests
import pandas as pd
import os


url = 'https://www.equestrian.ru'
category = '/market/horses/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/110.0.0.0 YaBrowser/23.3.3.719 Yowser/2.5 Safari/537.36'}
response = requests.get(url+category, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')
soup_options = soup.findAll('option')
soup_options = [element.text.strip() for element in soup_options]
breeds = ['Полукровная']
for element in soup_options:
    if element[0].isalpha():
        breeds.append(element)
    else:
        break



df = pd.read_csv('raw_data/equestrian.csv')
df.dropna(subset=['Price'], inplace=True)
df['Breed'] = df['Breed'].fillna('Без породы')
df.drop(['Name', 'Sizes', 'Advertisement data','Region', 'Location', 'Horse club', 'Contacts'], axis=1, inplace=True)
df_raw_breeds = df[df['Breed'].isin(breeds) == False]

df = df[df['Breed'].isin(breeds) == True]

raw_breeds = set(df_raw_breeds['Breed'].tolist())
df_clear_breeds = pd.DataFrame(columns=df.columns.values)
df_pony = df_raw_breeds[df_raw_breeds['Breed'].str.contains(r'Пони|они')]

duplicates = df_raw_breeds[df_raw_breeds.loc[:,'Breed'].isin(df_pony['Breed'])]
df_pony['Breed'] = 'Пони'
df_raw_breeds = df_raw_breeds.drop(duplicates.index)

crossbreed=df_raw_breeds[df_raw_breeds['Breed'].str.contains(r'Полу|Помес|-')]
if not os.path.exists('clean_data'):
    os.makedirs('clean_data')


df.to_csv('clean_data/equestrian.csv', encoding='utf-8-sig', index=False)

