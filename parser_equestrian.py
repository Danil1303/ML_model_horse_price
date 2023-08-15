from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
from time import time
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
    soup_dollar_course = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
    dollar_course = float(soup_dollar_course[0].text.replace(',', '.'))

    response = requests.get(euro_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    soup_euro_course = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
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
    df.to_csv('raw_data/equestrian.csv', encoding='utf-8-sig', index=False)
    parse_time = time() - parse_start
    minutes = int(parse_time / 60)
    seconds = round(parse_time - minutes * 60, 2)
    print(f'Парсинг занял {str(minutes) + " мин. " if minutes else ""}{seconds} сек., получено {len(data)} объявлений.')


parse()
