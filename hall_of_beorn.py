import requests
from bs4 import BeautifulSoup
from pipe_helpers import select, as_list

BASE_URL = 'http://hallofbeorn.com'

def fetch_info(path, rule):
    html = fetch_html(path)
    soup = BeautifulSoup(html, 'html.parser')
    return rule(soup)

def fetch_html(path, base_url=BASE_URL):
    url = f'{base_url}{path}'
    r = requests.get(url)
    html = r.text
    return html


def parse_pack_urls(soup):
    return [(i['title'], i['href']) for i in soup.find_all('a') if 'Products/' in i['href']]

def build_card_dict(card):
    return {
        'name': card[0],
        'type': card[1][1:-1],
        'quantity': int(card[2]),
        'hallofbeorn_url': card[3],
        'card_id': card[3].split('/')[-1]
    }

def get_card_list(soup):
    card_list_div = [d for d in soup.find_all('div') if 'Card List' in d.text][-1]
    card_list_a = card_list_div.find_next_sibling('div').find_all('a')
    card_info = (
        card_list_a
        | select(lambda a: a.find_all('span')[-3:] + [a['href']])
        | select(lambda a: (a[:-1] | select(lambda s: s.text) | as_list) + [a[-1]])
        | select(build_card_dict)
        | as_list
    )
    return card_info

parse_line = lambda t: t.strip('\n').lstrip('(').rstrip(')').split(',')
clean_strings = lambda t: (
    t 
    | select(lambda s: s.strip().strip('\'')) 
    | as_list
)
# with open('packs_list', 'r') as f:
#     packs = (
#         f.readlines()
#         | select(parse_line)
#         | select(clean_strings)
#         | select(lambda t: tuple(t))
#         | as_list
#     )
#     f.close()

def is_player_card(card):
    return card['type'] in ['Hero', 'Ally', 'Attachment', 'Event']

parse_line = lambda t: t.strip('\n').lstrip('(').rstrip(')').split(',')

def fetch_card_details(soup):
    info_soup = soup.find_all('div', {'class': 'statTextBox'})
    sphere_img = info_soup[0].find_all('img')
    if len(sphere_img) == 0:
        sphere = 'Neutral'
    else:
        sphere = sphere_img[0]['src'].split('/')[-1][:-4]
    traits_and_keywords = (
        info_soup[0].find_all('a')
        | select(lambda a: a.text)
        | as_list
        if len(info_soup[0].find_all('a')) > 0 else []
    )
    card_info = {
        'sphere': sphere,
        'traits_and_keywords': traits_and_keywords
    }
    return card_info

def update_card_info(card):
    info = fetch_info(card['hallofbeorn_url'], fetch_card_details)
    card.update(info)
    return card