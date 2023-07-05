import sys
 
# setting path
sys.path.append('../')

from pipe_helpers import select, as_list, where
from pipe import chain
from tqdm import tqdm
from hall_of_beorn import fetch_info, get_card_list, is_player_card
import pandas as pd

def load_packs_to_import():
    parse_line = lambda t: t.strip('\n').lstrip('(').rstrip(')').split(',')
    clean_strings = lambda t: (
    t 
    | select(lambda s: s.strip().strip('\'')) 
    | as_list
)
    with open('packs_list', 'r') as f:
        packs = (
        f.readlines()
        | select(parse_line)
        | select(clean_strings)
        | select(lambda t: tuple(t))
        | as_list
    )
        f.close()
    return packs

def load_cards_from_packs(packs):
    return  (
        tqdm(packs, desc='fetching packs ...', position=0, leave=True)
        | select(lambda t: fetch_info(t[1], get_card_list))
        | select(lambda t: t | where(is_player_card) | as_list)
        | as_list
    )
    
packs = load_packs_to_import()
cards_per_pack = load_cards_from_packs(packs)

def build_card_entries(packs, cards_per_pack):
    pack_names = (
        packs
        | select(lambda t: t[0].split('(')[0].strip())
        | as_list
    )

    def include_pack_name_in_card(card, pack_name):
            return {
            'pack': pack_name,
            **card
        }

    list_of_cards = (
        zip(pack_names, cards_per_pack)
        | select(lambda l: l[1] | select(lambda c: include_pack_name_in_card(c, l[0])) | as_list)
        | chain
        | as_list
    )
    return list_of_cards

cards = build_card_entries(packs, cards_per_pack)

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

cards = (
    tqdm(cards, desc='getting cards details ...', position=0, leave=True)
    | select(update_card_info)
    | as_list
)

neutral_like_spheres = {
    'willpower-small': 'Neutral', 
    'attack-small': 'Neutral', 
    'defense-small': 'Neutral', 
    'threat-small': 'Neutral',
}

cards_df = pd.DataFrame(cards)
cards_df.replace(neutral_like_spheres, inplace=True)

# check if folder exists
import os

TEMP_FILES_FOLDER = 'data'

if os.path.exists(TEMP_FILES_FOLDER):
    # delete path
    os.rmdir(TEMP_FILES_FOLDER)

# create folder
os.mkdir(TEMP_FILES_FOLDER)
cards_df.to_csv(f'{TEMP_FILES_FOLDER}/cards.csv', index=False)