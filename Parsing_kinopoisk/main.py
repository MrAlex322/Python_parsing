import csv
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class KinopoiskScraper:
    def __init__(self):
        self.headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'service-id': '25',
        }
        self.params = {'operationName': 'BoxOffices'}
        self.json_data = {
            'operationName': 'BoxOffices',
            'variables': {},
            'query': 'query BoxOffices { weekendBoxOfficeMovies { endDate startDate russiaBoxOfficeMovies { movie { ...BoxOfficeMovie __typename } weekendBoxOffice { rusBox { amount __typename } __typename } totalBoxOffice { weeks rusBox { amount __typename } __typename } __typename } usaBoxOfficeMovies { movie { ...BoxOfficeMovie __typename } weekendBoxOffice { usaBox { amount __typename } __typename } totalBoxOffice { weeks usaBox { amount __typename } __typename } __typename } worldBoxOfficeMovies { movie { ...BoxOfficeMovie __typename } weekendBoxOffice { worldBox { amount __typename } __typename } totalBoxOffice { weeks worldBox { amount __typename } __typename } __typename } __typename } } fragment BoxOfficeMovie on Movie { id title { russian original __typename } poster { avatarsUrl __typename } __typename } ',
        }

    def scrape_box_office_movies(self):
        response = requests.post('https://graphql.kinopoisk.ru/graphql/', params=self.params, headers=self.headers, json=self.json_data)
        srcs = response.json()
        id_list = []
        with open('movies_data.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Название', 'Бюджет', 'Рейтинг'])

            for key, value in srcs["data"].items():
                russia_movie_rental = value.get("russiaBoxOfficeMovies")
                usa_movie_rental = value.get("usaBoxOfficeMovies")
                world_movie_rental = value.get("worldBoxOfficeMovies")

                if russia_movie_rental:
                    for item in russia_movie_rental:
                        movie = item['movie']
                        title = movie['title']['russian']
                        film_id = movie['id']
                        box_office = item['weekendBoxOffice']['rusBox']['amount']
                        formatted_box_office = "{:.1f} млн. руб".format(box_office / 10 ** 6)
                        writer.writerow([title, formatted_box_office])
                        id_list.append(film_id)

                if usa_movie_rental:
                    for item in usa_movie_rental:
                        movie = item['movie']
                        title = movie['title']['russian']
                        film_id = movie['id']
                        box_office = item['weekendBoxOffice']['usaBox']['amount']
                        formatted_box_office = "{:.1f} млн. руб".format(box_office / 10 ** 6)
                        writer.writerow([title, formatted_box_office])
                        id_list.append(film_id)

                if world_movie_rental:
                    for item in world_movie_rental:
                        movie = item['movie']
                        title = movie['title']['russian']
                        film_id = movie['id']
                        box_office = item['weekendBoxOffice']['worldBox']['amount']
                        formatted_box_office = "{:.1f} млн. руб".format(box_office / 10 ** 6)
                        writer.writerow([title, formatted_box_office])
                        id_list.append(film_id)

        print("Данные успешно сохранены в CSV-файл.")
        return id_list


class RatingScraper:
    def __init__(self, id_list):
        self.id_list = id_list

    def scrape_ratings(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service('/path/to/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)

        for i, elem in enumerate(self.id_list):
            id_value = elem
            url = f'https://www.kinopoisk.ru/film/{id_value}'
            print(id_value)

            driver.get(url)

            driver.execute_script("return document.readyState")

            html = driver.page_source

            folder_path = 'film_html'
            filename = os.path.join(folder_path, f'films{id_value}.html')

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

            if len(rows) > 0 and i < len(rows):
                row = rows[i]
                row.append(rating)

            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(rows)

            print(f"Рейтинг добавлен в файл: {filename}")


if __name__ == '__main__':
    scraper = KinopoiskScraper()
    id_list = scraper.scrape_box_office_movies()

    rating_scraper = RatingScraper(id_list)
    rating_scraper.scrape_ratings()
