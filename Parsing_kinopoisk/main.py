import csv
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

headers = {
    'authority': 'graphql.kinopoisk.ru',
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9',
    'content-type': 'application/json',
    'dnt': '1',
    'origin': 'https://www.kinopoisk.ru',
    'referer': 'https://www.kinopoisk.ru/',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'service-id': '25',
    'uber-trace-id': '9ecf4b7860a891a5:1ae73c12a911d5ad:0:1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51',
    'x-request-id': '1687261876555367-14143657862820114590',
}

params = {
    'operationName': 'BoxOffices',
}

json_data = {
    'operationName': 'BoxOffices',
    'variables': {},
    'query': 'query BoxOffices { weekendBoxOfficeMovies { endDate startDate russiaBoxOfficeMovies { movie { ...BoxOfficeMovie __typename } weekendBoxOffice { rusBox { amount __typename } __typename } totalBoxOffice { weeks rusBox { amount __typename } __typename } __typename } usaBoxOfficeMovies { movie { ...BoxOfficeMovie __typename } weekendBoxOffice { usaBox { amount __typename } __typename } totalBoxOffice { weeks usaBox { amount __typename } __typename } __typename } worldBoxOfficeMovies { movie { ...BoxOfficeMovie __typename } weekendBoxOffice { worldBox { amount __typename } __typename } totalBoxOffice { weeks worldBox { amount __typename } __typename } __typename } __typename } } fragment BoxOfficeMovie on Movie { id title { russian original __typename } poster { avatarsUrl __typename } __typename } ',
}

response = requests.post('https://graphql.kinopoisk.ru/graphql/', params=params, headers=headers, json=json_data)

# Сохраняем название и бюджет фильмов

srcs = response.json()
result = {}
id_list = []
with open('box_office_data.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Название', 'Бюджет', 'Рейтинг'])

    for key, value in srcs["data"].items():
        inner_russia = value.get("russiaBoxOfficeMovies")
        inner_usa = value.get("usaBoxOfficeMovies")
        inner_world = value.get("worldBoxOfficeMovies")

        if inner_russia:
            for item in inner_russia:
                movie = item['movie']
                title = movie['title']['russian']
                film_id = movie['id']
                box_office = item['weekendBoxOffice']['rusBox']['amount']
                formatted_box_office = "{:.1f} млн. руб".format(box_office / 10 ** 6)
                writer.writerow([title, formatted_box_office])
                id_list.append(film_id)

        if inner_usa:
            for item in inner_usa:
                movie = item['movie']
                title = movie['title']['russian']
                film_id = movie['id']
                box_office = item['weekendBoxOffice']['usaBox']['amount']
                formatted_box_office = "{:.1f} млн. руб".format(box_office / 10 ** 6)
                writer.writerow([title, formatted_box_office])
                id_list.append(film_id)

        if inner_world:
            for item in inner_world:
                movie = item['movie']
                title = movie['title']['russian']
                film_id = movie['id']
                box_office = item['weekendBoxOffice']['worldBox']['amount']
                formatted_box_office = "{:.1f} млн. руб".format(box_office / 10 ** 6)
                writer.writerow([title, formatted_box_office])
                id_list.append(film_id)

print("Данные успешно сохранены в CSV-файл.")
print(id_list)

# Сохраняем рейтинг фильмов

chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service('/path/to/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

count_id = 0
num_row = 1
while count_id < 15:
    id_value = id_list[count_id]
    url = f'https://www.kinopoisk.ru/film/{id_value}'
    print(id_value)

    driver.get(url)

    driver.execute_script("return document.readyState")

    html = driver.page_source

    folder_path = 'film_html'
    filename = os.path.join(folder_path, f'film{id_value}.html')

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html)
        print(f"HTML-код сохранен в файл: {filename}")

    soup = BeautifulSoup(html, 'html.parser')

    element = soup.find('span', class_=lambda c: c and 'styles_rating' in c)

    rating = element.text if element else 'Рейтинг не найден'

    filename = 'box_office_data.csv'

    rows = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)

    if len(rows) > 0:
        row = rows[num_row]
        row.append(rating)
    num_row += 1

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print(f"Рейтинг добавлен в файл: {filename}")
    count_id += 1
