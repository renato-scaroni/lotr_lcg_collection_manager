import requests
from bs4 import BeautifulSoup
import requests as r

BASE_URL = 'https://ringsdb.com/'

def fetch_info(path, rule):
    html = fetch_html(path)
    soup = BeautifulSoup(html, 'html.parser')
    return rule(soup)

def fetch_html(path, base_url=BASE_URL):
    url = f'{base_url}{path}'
    r = requests.get(url)
    html = r.text
    return html

def get_decks(soup):
    a_tags = soup.find_all('a', class_='decklist-name')
    return [(t.text, t['href'].split('/')[-2]) for t in a_tags]

apis = {
    'cards': 'api/public/cards/',
    'packs': 'api/public/packs/',
    'cards_in_pack': 'api/public/cards/',
    'cycles': 'api/public/scenario/01001'
}

def get_packs():
    return r.get(BASE_URL + apis['packs']).json()

def get_cards_in_pack(pack_id):
    return r.get(BASE_URL + apis['cards_in_pack'] + str(pack_id)).json()

def get_cycle():
    return r.get(BASE_URL + apis['cycles'])