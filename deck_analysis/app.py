from typing import Any
import numpy as np
import matplotlib.pyplot as plt
import panel as pn
import pandas as pd
import os
from zipfile import ZipFile
from datetime import datetime
import decks_utils as du
import pandas as pd
import numpy as np
from itertools import combinations

pn.extension(template='fast')

class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class CollectionManager(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.cards_in_collection = CollectionManager.load_collection()

        self.packs_widget =  pn.widgets.CheckBoxGroup(
            name='Frequency',
            options=self.cards_in_collection['pack'].drop_duplicates().tolist(),
            value=pd.read_csv(f"data/packs.csv").head(33).pack_name.to_list()
        )

    def get_packs_selected(self):
        return self.packs_widget.value

    @staticmethod
    def load_collection(base_path="data"):
        columns = ['name', 'sphere', 'type', 'pack', 'quantity']
        packs_in_collection = pd.read_csv(f"{base_path}/packs.csv")
        all_cards_rings_db = pd.read_csv(f"{base_path}/cards_rings_db_info.csv")
        cards_in_collection = packs_in_collection.merge(all_cards_rings_db, on='pack_name', how='left')
        rename_dict = {
            'sphere_name': 'sphere',
            'type_name': 'type',
            'pack_name': 'pack'
        }
        cards_in_collection.rename(columns=rename_dict, inplace=True)
        cards_in_collection = cards_in_collection[columns]

        revised_core_set = cards_in_collection[cards_in_collection.pack == 'Core Set'].copy()
        revised_core_set['quantity'] = revised_core_set.apply(lambda x: 3 if x['type'] != 'Hero' else 1, axis=1)
        revised_core_set['pack'] = 'Revised Core Set'

        cards_in_collection = pd.concat([cards_in_collection, revised_core_set])
        return cards_in_collection

# pn.Column(
#     '# Selecione os packs da sua coleção',
#     CollectionManager().packs_widget
# ).servable(target='sidebar')

file_input = pn.widgets.FileInput(
    accept='.zip'
)

class MainApp(pn.Column):
    def __init__(self, **params):
        super().__init__(**params)
        self._cards_in_collection = CollectionManager.load_collection()
        self._cards_map = None
        self._decks = None
        self._shared_cards = None
        self._most_simultanious_deck = None

decks = pn.Tabs()

def extract_file(file_name):
    with ZipFile(f'tmp/{file_name}.zip', 'r') as zipObj:
        zipObj.extractall(f'tmp/{file_name}')

class DeckListPage(pn.Column):
    def __init__(self, title, df):
        self.df = df
        self.df_obj = pn.pane.DataFrame(df, width=400)
        self.title = title
        self.dropdown = pn.widgets.Select(
            name='Escolha um deck',
            options=['Todos'] + df['deck_name'].drop_duplicates().tolist(),
            value='Todos'
        )

        self.dropdown.param.watch(self.select_card_view, 'value')

        super().__init__(
            f'# {title}', 
            self.dropdown,
            self.df_obj, 
            name=title)

    def select_card_view(self, event):
        if event.new == 'Todos':
            self.df_obj.object = self.df
        else:
            self.df_obj.object = self.df[self.df.deck_name == event.new]

    def __repr__(self) -> str:
        return self.title

class CardsMapPage(pn.Column):
    def __init__(self, df):
        self.df = df
        self.cards_map = self.compute_cards_map(self.df)
        self.cards_map_obj = pn.pane.DataFrame(
            self.cards_map,
            width=1000
        )
        
        self.multiselect = pn.widgets.MultiSelect(
            name='Escolha os decks',
            options=self.df['deck_name'].drop_duplicates().tolist(),
            value=self.df['deck_name'].drop_duplicates().tolist()
        )

        self.multiselect.param.watch(self.update_df_obj, 'value')

        super().__init__(
            f'# Mapeamento de cartas compartilhadas',
            self.multiselect,
            self.cards_map_obj,
            name='cartas compartilhadas'
        )

    def update_df_obj(self, event):
        if len(event.new) <= 1:
            return
        df = self.df[self.df.deck_name.isin(event.new)]
        print(len(df))
        self.cards_map_obj.object = self.compute_cards_map(df)
    
    def compute_cards_map(self, df):
        cards_in_collection = CollectionManager().cards_in_collection
        shared_cards = du.get_used_cards_in_collection(df, cards_in_collection)
        cards_map = pd.pivot_table(
            shared_cards, values='quantity',
            index=['name', 'sphere', 'type'],
            columns=['deck_name'], aggfunc=np.sum)\
        .fillna(0)
        cards_map.reset_index(inplace=True)
        cards_in_collection = cards_in_collection.groupby(['name', 'sphere', 'type']).sum().reset_index().drop(columns=['pack'])
        cards_in_collection.rename(columns={'quantity': 'in_collection'}, inplace=True)
        cards_map = cards_map.merge(cards_in_collection, on=['name', 'sphere', 'type'], how='left')
        cards_map.set_index(['name', 'sphere', 'type'], inplace=True)
        return cards_map

class ProxiesPage(pn.Column):
    def __init__(self, df):
        self.df = df
        self.df_obj = pn.pane.DataFrame(df, width=400)
        super().__init__(
            '# Proxies', 
            self.df_obj, 
            name='proxies')

# file_input.loading = True
def save_file(event):
    os.makedirs('tmp', exist_ok=True)
    file_input.loading = True
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"decks_{ts}"
    file_input.save(f'tmp/{file_name}.zip')
    extract_file(file_name)

    df = load_decklists(f'tmp/{file_name}')
    loaded = DeckListPage('Decks carregados', df)
    decks.append(loaded)

    cards_map = CardsMapPage(df)
    decks.append(cards_map)

    file_input.loading = False

def load_decklists(path):
    decks = du.load_decks(path)
    decklist_df = du.cards_in_decks(du.count_cards_in_deck, decks)
    return decklist_df

# def get_most_simultanious_deck(cards_map, i=None):
#     deck_names = cards_map.drop(columns=['in_collection']).columns
#     if i is None:
#         i = len(deck_names)
#     combs = list(combinations(deck_names, i))
#     filtered_combs = list(filter(lambda x: (cards_map['in_collection'] >= cards_map[list(x)].sum(axis=1)).all(), combs))
#     if len(filtered_combs):
#         import math
#         total_decks = len(deck_names)
#         print("total decks", total_decks, "simultanious decks", i)
#         print("max combinations", math.comb(total_decks, i))
#         print("found combinations", len(filtered_combs))

#         return filtered_combs

#     return get_most_simultanious_deck(cards_map, i-1)

# get_most_simultanious_deck(cards_map, 5) + get_most_simultanious_deck(cards_map, 6)

file_input.param.watch(save_file, 'value')

df = load_decklists(f'tmp/decks')
loaded = DeckListPage('Decks carregados', df)
decks.append(loaded)

cards_map = CardsMapPage(df)
decks.append(cards_map)



pn.Column(
    # '# Escolha um arquivo com decks para analisar',
    # file_input,
    # '(arquivo .zip com decks em formato .txt como exportado pelo RingsDB))',
    decks
).servable(target='main')


