import panel as pn
from collection_manager import CollectionManager
import decks_utils as du
import pandas as pd
import numpy as np
from itertools import combinations

def get_most_simultanious_deck(cards_map, i=None):
    deck_names = cards_map.drop(columns=['in_collection', 'used_in_decks', 'available']).columns
    if i is None:
        i = len(deck_names)
    combs = list(combinations(deck_names, i))
    filtered_combs = list(filter(lambda x: (cards_map['in_collection'] >= cards_map[list(x)].sum(axis=1)).all(), combs))
    if len(filtered_combs):
        return filtered_combs

    return get_most_simultanious_deck(cards_map, i-1)

class event:
    new = None
    def __init__(self, new):
        self.new = new

class CardsMapPage(pn.Column):
    def __init__(self, df):
        self.df = df
        self.cards_map = self.compute_cards_map(self.df)
        
        values = self.cards_map.columns.tolist()[1:-1]
        decks = self.df.deck_name.drop_duplicates().tolist()
        values = decks

        self.decks_select =  pn.widgets.CheckBoxGroup(
            name='Frequency',
            options=decks,
            value=values,
        )

        self.cards_map_obj = pn.widgets.Tabulator(
            self.cards_map,
            width=1200,
            show_index=False,
            selectable=False,
        )
        
        self.view_columns = pn.widgets.RadioButtonGroup(
            name='view_columns',
            options=['Geral', 'Por deck'],
            value='Geral',
        )
        
        self.view_rows = pn.widgets.RadioButtonGroup(
            name='view_rows',
            options=['Conlitos', 'Não conflitos', 'Todos'],
            value='Conlitos',
        )

        self.decks_select.param.watch(self.decks_select_cb, 'value')
        self.view_columns.param.watch(self.view_columns_cb, 'value')
        self.view_rows.param.watch(self.view_rows_cb, 'value')

        r = pn.Row(
            pn.Column(self.decks_select,),
            pn.Column(
                pn.Row(self.view_columns,self.view_rows),
                self.cards_map_obj
            )
        )

        self.sync_objs()

        super().__init__(
            f'# Mapeamento de cartas compartilhadas',
            r,
            name='cartas compartilhadas'
        )

    def sync_objs(self):
        self.decks_select_cb(event(self.decks_select.value))
        self.ensure_filters()

    def ensure_filters(self):
        self.view_columns_cb(event(self.view_columns.value))
        self.view_rows_cb(event(self.view_rows.value))

    def view_rows_cb(self, event):
        card_map = self.full_card_map
        if event.new == 'Conlitos':
            self.cards_map_obj.value = card_map[card_map['proxies_needed'] > 0]
        elif event.new == 'Não conflitos':
            self.cards_map_obj.value = card_map[card_map['proxies_needed'] <= 0]
        else:
            self.cards_map_obj.value = card_map

    def decks_select_cb(self, event):
        if len(event.new) <= 0:
            return
        df = self.df[self.df.deck_name.isin(event.new)]
        self.full_card_map = self.compute_cards_map(df)
        self.cards_map_obj.value = self.full_card_map
        self.ensure_filters()
    
    def view_columns_cb(self, event):
        if event.new == 'Geral':
            cols = self.cards_map_obj.value.columns.to_list()
            cols = cols[3:-3]
            self.cards_map_obj.hidden_columns = cols
        else:
            self.cards_map_obj.hidden_columns = []
    
    def compute_cards_map(self, decklists):
        all_cards = CollectionManager().published_cards_per_pack
        packs_in_collection = CollectionManager().packs_in_collection
        cards_in_collection = all_cards[all_cards.pack.isin(packs_in_collection)]
        

        cards_in_collection = cards_in_collection\
            .groupby(['name', 'sphere', 'type'])\
            .sum()\
            .drop(columns=['pack'])\
            .reset_index()
        
        decklists = CollectionManager().get_cards_sphere_and_type(decklists)
        cards_in_decks = decklists\
            .groupby(['name', 'sphere', 'type', 'deck_name'])\
            .sum()\
            .reset_index()
                        
        cards_map = pd.pivot_table(
            cards_in_decks, values='quantity',
            index=['name', 'sphere', 'type'],
            columns=['deck_name'], aggfunc=np.sum)\
        .fillna(0)
        cards_map['total_in_decks'] = cards_map.sum(axis=1)
        
        cards_map = cards_map.merge(cards_in_collection, 
                                    on=['name', 'sphere', 'type'], 
                                    how='left').fillna(0)
        cards_map.rename(columns={
            'quantity': 'in_collection',
            }, inplace=True)

        cards_map['proxies_needed'] = \
            cards_map['in_collection'] - cards_map['total_in_decks']
        cards_map['proxies_needed'] = cards_map.proxies_needed.apply(lambda x: -x if x < 0 else 0)

        return cards_map