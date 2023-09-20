import os
import re
import glob
import requests
import numpy as np
import pandas as pd
from time import time
from typing import Union
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry


def parse():
    parse_start = time()
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    url = 'https://www.equestrian.ru'
    category = '/market/horses/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/110.0.0.0 YaBrowser/23.3.3.719 Yowser/2.5 Safari/537.36'}

    dollar_url = 'https://www.google.ru/search?newwindow=1&sca_esv=556757575&sxsrf=AB5stBiwKyw7D6S3QgvMZkY3UZxhk2So9A:1692019453036&q=Курс+доллара+к+рублю+на+сегодня&uds=H4sIAAAAAAAA_-Oq5BK-MPfCBoWLjRe2Xth8Yd-FLRf2XuwXUr2w62LzxYaLjQpAgX0XdgPhhosNQHUXdikAhZsvbLyw-2KfAVOR5YVZRChUuLAXww4AoNTqbnsAAAA&sa=X&ved=2ahUKEwiR2M3Tn9yAAxUWIBAIHfZKDXIQxKsJegQICxAB&ictx=0&biw=867&bih=724&dpr=1.25'
    euro_url = 'https://www.google.ru/search?newwindow=1&sca_esv=556757575&sxsrf=AB5stBjzP_7eUM5V7wzNNpWaOMAl82TB6g:1692019571030&q=Курс+евро+к+рублю+на+сегодня&uds=H4sIAAAAAAAA_-PK5RK-MPfCBoWLjRe2Xth8Yd-FLRf2XuwXkr-w62LzxYaLjQpA4U0XGy7sU7iwSwEo0Hxh44XdF_sMmIqML8zCq0Thwl4McwF6BQTgbwAAAA&sa=X&ved=2ahUKEwiYx--LoNyAAxWNIhAIHTCBCssQxKsJegQICRAB&ictx=0&biw=1488&bih=724&dpr=1.25'
    response = requests.get(dollar_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    soup_dollar_course = soup.findAll("span", {"class": "DFlfde SwHCTb", "data-precision": 2})
    dollar_course = float(soup_dollar_course[0].text.replace(',', '.'))

    response = requests.get(euro_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    soup_euro_course = soup.findAll("span", {"class": "DFlfde SwHCTb", "data-precision": 2})
    euro_course = float(soup_euro_course[0].text.replace(',', '.'))

    p, i = 0, 0
    data = []
    columns = ['Name', 'Price', 'Age', 'Sex', 'Color', 'Height', 'Sizes', 'Breed', 'Advertisement data',
               'Region', 'Location', 'Horse club', 'Contacts']
    while True:
        start = time()
        page = f'?p={p}'
        response = session.get(url + category + (page if p else ''))
        p += 1
        soup = BeautifulSoup(response.content, 'html.parser')
        contents = soup.findAll('div', class_='offer')

        if not contents:
            break

        links = []
        for item in contents:
            try:
                name = next(iter(item.find('a', href=True))).strip()
                price = next(iter(item.find('div', class_='price'))).strip()
                links.append(item.find('a', href=True)['href'])
            except StopIteration:
                print(f'Пустое объявление по адресу {url + item.find("a", href=True)["href"]}')
            else:
                try:
                    if price == 'цена по запросу':
                        price = None
                    elif '$' in price:
                        price = int(int(price.split(' ')[0].replace(' ', '')) * dollar_course)
                    elif '€' in price:
                        price = int(int(price.split(' ')[0].replace(' ', '')) * euro_course)
                    else:
                        price = int(price.split(' руб.')[0].replace(' ', ''))
                except:
                    price = None
                data.append([name, price])

        for link in links:
            response = session.get(url + link)
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                table = soup.find('table', class_='market_descr')
                rows = table.findAll('tr')
            except AttributeError:
                print(f'Не считалась таблица по адресу {url + link}.')
            else:
                for row in rows:
                    cols = row.find_all('td')
                    cols = [element.text.strip() for element in cols]
                    data[i].append(next(element.capitalize() if element else None for element in cols[1:]))
                i += 1
        print(f'Обработана страница {p} за {round(time() - start, 2)} сек.')

    df = pd.DataFrame(data, columns=columns)

    if not os.path.exists('raw_data'):
        os.makedirs('raw_data')
    df.to_csv(f'raw_data/equestrian_{len(glob.glob("raw_data/equestrian*")) + 1}.csv', encoding='utf-8-sig',
              index=False)
    parse_time = time() - parse_start
    minutes = int(parse_time / 60)
    seconds = round(parse_time - minutes * 60, 2)
    print(f'Парсинг занял {str(minutes) + " мин. " if minutes else ""}{seconds} сек., получено {len(data)} объявлений.')
    clear_data(df)


def get_breeds() -> list[str]:
    # Функция, получающая с сайта список всех представленных пород

    if os.path.exists('breeds.txt'):
        with open('breeds.txt', 'r') as file:
            breeds = []
            while line := file.readline():
                breeds.append(line[:-1])
    else:
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
                breeds.append(element.lower())
            else:
                with open('breeds.txt', 'w') as output:
                    for breed in breeds:
                        output.write(str(breed) + '\n')
                break
    return breeds


def height_clear(height_str: str) -> Union[float, None]:
    # Функция для форматирования столбца 'Heights'

    # Подсчёт среднего для диапазонов в виде 'число-число'
    if bool(re.search(r'\d+-\d+', height_str)):
        split_digit = height_str.split('-')
        part_1 = split_digit[0]
        part_2 = ''.join(filter(str.isdigit, split_digit[1]))
        return float(np.mean(list(map(int, [part_1, part_2]))))

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
    # Очистка записи, не содержащей цифр
    elif re.match(r'^[а-яА-Я]+$', height_str):
        return None
    # Удаление посторонних букв в записи, сохраняя цифры
    else:
        return float(''.join(filter(str.isdigit, height_str)))


def color_clear(df_color: str, main_colors: list[str]) -> Union[str, None]:
    # Функция для форматирования столбца 'Color'
    for color in main_colors:
        if color.lower() in df_color.lower():
            return color + 'ой'
    if ' ' in df_color or '-' in df_color:
        return 'Смешанный'
    else:
        return None


def breed_clear(breed: str, breeds: list[str]) -> Union[str, None]:
    # Функция для форматирования столбца 'Breed'
    if breed.lower() in breeds:
        return breed.capitalize()
    elif bool(re.search(r'Пони|они', breed)):
        return 'Помесь пони'
    elif bool(re.search(r'олу|омес|-|\+|/', breed)):
        return 'Помесь'
    else:
        return None


def age_clear(age: str) -> Union[int, None]:
    if '-' in age:
        return 0
    search_digits = re.search(r'\((\d+) [а-яА-Я]+\)', age)
    if bool(search_digits):
        return search_digits.group(1)


def clear_data(df: pd.DataFrame) -> None:
    df.dropna(subset=['Price'], inplace=True)
    df.dropna(subset=['Color'], inplace=True)
    df.dropna(subset=['Height'], inplace=True)
    df = df.loc[df['Price'] >= 30000]
    df['Breed'] = df['Breed'].fillna('Без породы')
    df.drop(['Name', 'Sizes', 'Advertisement data', 'Region', 'Location', 'Horse club', 'Contacts'], axis=1,
            inplace=True)

    # Форматирование столбца 'Breed'
    breeds = get_breeds()
    df['Breed'] = df['Breed'].apply(lambda breed: breed_clear(breed, breeds))

    # Форматирование столбца 'Height'
    df['Height'] = df['Height'].apply(height_clear)
    df = df.drop(df[(df['Height'] < 30) | (df['Height'] > 250)].index)

    # Форматирование столбца 'Color'
    main_colors = ['Гнед', 'Рыж', 'Сер', 'Ворон', 'Пег', 'Солов', 'Караков', 'Булан', 'Бур', 'Чубар',
                   'Изабеллов', 'Игренев', 'Мышаст', 'Саврас', 'Чал']
    df['Color'] = df['Color'].apply(lambda color: color_clear(color, main_colors))

    # Форматирование столбца 'Age'
    df['Age'] = df['Age'].apply(age_clear)

    df.dropna(subset=['Breed'], inplace=True)
    df.dropna(subset=['Height'], inplace=True)
    df.dropna(subset=['Color'], inplace=True)

    if not os.path.exists('clean_data'):
        os.makedirs('clean_data')
    df.to_csv(f'clean_data/equestrian_{len(glob.glob("clean_data/equestrian*")) + 1}.csv', encoding='utf-8-sig',
              index=False)
