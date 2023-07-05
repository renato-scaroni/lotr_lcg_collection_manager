import requests
from bs4 import BeautifulSoup

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
