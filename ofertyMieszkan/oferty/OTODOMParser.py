import os

from bs4 import BeautifulSoup
import json

from oferty import db
from oferty.models import Appartment


def find_title(flat):
    return flat.find('span', {'class': 'offer-item-title'}).getText()


class OTODOMParser:

    def __init__(self, html):
        self.html = html
        self.soup_html = BeautifulSoup(self.html, features='html.parser')
        self.flats = self.find_flats()
        self.lista_mieszkan = {}
        self.city = self.find_city()

    def find_city(self):
        return self.soup_html.find('h1', {'class': 'query-text-h1'})

    def find_flats(self):
        return self.soup_html.find_all('article', {'class': 'offer-item'})

    def find_price_of_flats(self, flat):
        return flat.find('li', {'class': 'offer-item-price'}).getText().strip()

    def find_district_of_city(self, flat):
        return flat.find('p', {'class': 'text-nowrap'}).getText().strip().split(": ")[1].split(', ')[1]

    def find_kind_of_flat(self, flat):
        return flat.find('p', {'class': 'text-nowrap'}).getText().strip().split(": ")[1].split(' ')

    def find_link(self, flat):
        return flat.find('a')['href']

    def find_image(self, flat):
        return flat.find('span')['data-src']

    def collect_info_about_flats(self):
        for i, flat in enumerate(self.flats):
            title = find_title(flat)
            price = self.find_price_of_flats(flat)
            city_district = self.find_district_of_city(flat)
            type_of_sale = self.find_kind_of_flat(flat)
            link = self.find_link(flat)
            image = self.find_image(flat)
            appartment = Appartment(image=image, title=title, price=price, city_district=city_district, type_of_sale='sprzedaż',link=link)
            db.session.add(appartment)
            db.session.commit()


    # def save_to_json(self, name_file):
    #     with open(name_file, 'w+') as file:
    #         json.dump(self.lista_mieszkan, file, ensure_ascii=True, indent=4)
