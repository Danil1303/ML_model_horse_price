import os
import re
import requests
import numpy as np
import pandas as pd
from typing import Union
from bs4 import BeautifulSoup


def get_breeds() -> list[str]:
    # Функция, получающая с сайта список всех заданных пород
    url = 'https://www.equestrian.ru'
    category = '/market/horses/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/110.0.0.0 YaBrowser/23.3.3.719 Yowser/2.5 Safari/537.36'}
    response = requests.get(url + category, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    soup_options = soup.findAll('option')
    soup_options = [element.text.strip() for element in soup_options]
    breeds = []
    for element in soup_options:
        if element[0].isalpha():
            breeds.append(element)
        else:
            return breeds


def height_clear(height_str: str) -> Union[float, None]:
    # Функция для форматирования столбца Heights

    # Подсчёт среднего для диапазонов в виде 'число-число'
    if bool(re.search(r'\d+-\d+', height_str)):
        return float(np.mean(list(map(int, height_str.split('-')))))
    # Перевод из десятичной записи в целочисленную
    elif bool(re.search(r'\d+[.,]\d+', height_str)):
        height_str = re.sub(r'[a-zA-Zа-яА-Я]', '', height_str)
        heights = re.split(r'[.,]', height_str)
        heights[1] = heights[1].replace('0', '')
        # Например 1.05 м
        if len(heights[0]) == 1:
            return float(heights[0]) * 100 + float(heights[1])
        # Например 100.5 см
        else:
            return float(heights[0]) + float(heights[1]) / 10
    #
    elif re.match(r'^[а-яА-Я]+$', height_str):
        return None
    # Удаление посторонних букв в записи
    else:
        return float(''.join(filter(str.isdigit, height_str)))


df = pd.read_csv('raw_data/equestrian.csv')
df.dropna(subset=['Price'], inplace=True)
df.dropna(subset=['Color'], inplace=True)
df.dropna(subset=['Height'], inplace=True)
df = df.loc[df['Price'] >= 30000]
df['Breed'] = df['Breed'].fillna('Без породы')
df.drop(['Name', 'Sizes', 'Advertisement data', 'Region', 'Location', 'Horse club', 'Contacts'], axis=1, inplace=True)

breeds = get_breeds()
df_raw_breeds = df[df['Breed'].isin(breeds) == False]

df = df[df['Breed'].isin(breeds) == True]

raw_breeds = set(df_raw_breeds['Breed'].tolist())
# Объединение нескольких семантически одинаковых типов, но имеющих разное написание, в один
df_pony = df_raw_breeds[df_raw_breeds['Breed'].str.contains(r'Пони|они')]
df_raw_breeds = df_raw_breeds.drop(df_pony.index)
df_pony.reset_index(drop=True)
df_pony['Breed'] = 'Помесь пони'

df_crossbreed = df_raw_breeds[df_raw_breeds['Breed'].str.contains(r'олу|омес|-|\+|/')]
df_raw_breeds = df_raw_breeds.drop(df_crossbreed.index)
df_crossbreed.reset_index(drop=True)
df_crossbreed['Breed'] = 'Помесь'

df = pd.concat([df, df_crossbreed, df_pony])

df['Height'] = df['Height'].apply(height_clear)
df.dropna(subset=['Height'], inplace=True)
df = df.drop(df[(df['Height'] < 30) | (df['Height'] > 250)].index)

if not os.path.exists('clean_data'):
    os.makedirs('clean_data')
df.to_csv('clean_data/equestrian.csv', encoding='utf-8-sig', index=False)
