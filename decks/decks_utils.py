from typing import Iterator, Callable
from pipe import Pipe, select, where, chain, groupby
import requests as r
from tqdm import tqdm
import os 
from pipe import select, where
import pandas as pd
from functools import reduce
import sys
 
# setting path
sys.path.append('../data_ingestion')

from pipe_helpers import as_list

BASE_PATH = 'decks'
def list_files(path=BASE_PATH):
    return (
        os.listdir(path)
        | where(lambda name: os.path.isfile(os.path.join(path, name)))
        | where(lambda name: name.endswith('.txt'))
        | select(lambda name: os.path.join(path, name))
        | as_list
    )

@Pipe
def split_list(l, x):
    curr_idx = 0
    parts = [[]]
    for item in l:
        if item == x:
            curr_idx = curr_idx + 1
            parts.append([])
        else:
            parts[curr_idx].append(item)
    return parts


@Pipe
def first(l):
    return l.__iter__().__next__()


def load_deck(file_path):
    deck = {}
    lines = open(file_path).read().split('\n')
    deck['name'] = lines[0]
    deck['cards'] = (
        lines[3:]
        | split_list("Sideboard")
        | first
        | where(lambda x: len(x) > 0) 
        | where(lambda x: x[0].isdigit()) 
        | as_list
    )
    
    return deck

def parse_line(line):
    card = {
        'name': line.split('(')[0].split('x ')[1].strip(),
        'quantity': int(line.split('x ')[0]),
        'pack': line.split('(')[1].split(')')[0].strip(),
    }
    return card

def dict_insert(d, k, v):
    d[k] = v
    return d

def count_cards_in_deck(deck):
    cards =  (
        deck['cards']
        | select(parse_line)
        | select(lambda c: dict_insert(c, 'deck_name', deck['name']))
        | as_list
    )
    return cards

def general_count(info):
    name, pack = info[0]
    card_copies = (list(info[1]))
    card = {
        'name': name,
        'quantity': sum([c['quantity'] for c in card_copies]),
        'pack': pack,
        'decks': [c['deck_name'] for c in card_copies]
    }
    
    return card

def count_cards(decks):
    return (
        decks
        | groupby(lambda c: (c['name'], c['pack']))
        | select(general_count)
        | as_list
    )

def load_decks(path):
    return (
        list_files(path) 
        | select(load_deck)
        | as_list
    )

def cards_in_decks(count_cards_in_deck, decks):
    cards_count = decks | select(count_cards_in_deck) | chain
    used_cards_df = pd.DataFrame(cards_count)
    return used_cards_df

def get_shared_cards(used_cards_df):
    shared_cards = used_cards_df.groupby(['name', 'pack']).count()[['deck_name']].reset_index()
    shared_cards = shared_cards[shared_cards['deck_name'] > 1].drop(columns=['deck_name'])
    shared_cards_df = shared_cards.merge(used_cards_df, on=['name', 'pack'], how='left')
    return shared_cards_df

def load_all_cards_df(file_name, cards_path="data/"):
    cards_path = f"{cards_path}{file_name}"
    collection = pd.read_csv(cards_path)
    collection['pack'] = collection['pack'].apply(
        lambda x: ('Over Hill and Under Hill' if x == 'The Hobbit: Over Hill and Under Hill' else x)
    )
    
    return collection

def get_used_cards_in_collection(decklist, all_cards):
    cards_per_pack = all_cards[['name', 'sphere', 'type', 'pack', 'quantity']]
    all_cards_count = all_cards.groupby(['name', 'sphere', 'type']).sum()
    all_cards_count = all_cards_count.reset_index()

    decklist = cards_per_pack\
                .drop(columns=['quantity'])\
                .merge(decklist, 
                    on=["name", "pack"], 
                    how="inner")
    decklist = decklist[['name', 'sphere', 'type', 'deck_name', 'quantity']]

    cards_in_use = decklist.groupby(['name', 'sphere', 'type']).sum().reset_index()
    cards_in_use = cards_in_use[['name', 'sphere', 'type', 'quantity']]
    cards_in_use = cards_in_use.merge(all_cards_count, 
                on=['name', 'sphere', 'type'], 
                how="inner", 
                suffixes=['_in_decks', '_in_collection'])
    cards_in_use = cards_in_use[['name', 'sphere', 'type', 'quantity_in_collection', 'quantity_in_decks']]
    cards_in_use['available_cards'] = cards_in_use['quantity_in_collection'] - cards_in_use['quantity_in_decks']
    cards_in_use = cards_in_use[cards_in_use['available_cards'] < 0]

    return decklist.merge(cards_in_use[['name', 'sphere', 'type']], 
                on=['name', 'sphere', 'type'], 
                how="inner")

if __name__ == '__main__':
    decks = load_decks('./decks/')
    decklist_df = cards_in_decks(count_cards_in_deck, decks)
    all_cards = load_all_cards_df()
    get_used_cards_in_collection(decklist_df, all_cards)
