from bs4 import BeautifulSoup
import json


class OLXParser:

    def __init__(self, html):
        self.html = html
        self.soup_html = BeautifulSoup(self.html, features='html.parser')
        self.flats = self.find_flats()
        self.lista_mieszkan = {}

    def find_flats(self):
        return self.soup_html.find_all('tr', {'class': 'offer'})

    def find_title(self, flat):
        return flat.find('strong').getText()

    def find_price(self, flat):
        return flat.find('p', {'class': 'price'}).getText().strip()

    def find_dzielnica(self, flat):
        return flat.find('span').getText().strip()

    def find_link(self, flat):
        return flat.find('a')['href']

    def find_negocjacja(self, flat):
        if flat.find('span', {'class': 'normal inlblk'}):
            return flat.find('span', {'class': 'normal inlblk'}).getText().strip()

    def collect_info_about_flats(self):
        for i, flat in enumerate(self.flats):
            title = self.find_title(flat)
            price = self.find_price(flat)
            dzielnica = self.find_dzielnica(flat)
            link = self.find_link(flat)
            negocjacja = self.find_negocjacja(flat)
            self.lista_mieszkan[i] = {'Tytuł': title, 'Cena': price, 'dzielnica': dzielnica, 'link': link,
                                      'negocjacje': negocjacja}
        return self.lista_mieszkan

    def save_to_json(self, name_file):
        with open(name_file, 'w') as file_json:
            json.dump(self.lista_mieszkan, file_json, ensure_ascii=True, indent=4)
