import panel as pn
import os
from zipfile import ZipFile
from datetime import datetime
import decks_utils as du
from itertools import combinations
from deck_list_page import DeckListPage
from cards_map_page import CardsMapPage

pn.extension('tabulator', template='fast')

file_input = pn.widgets.FileInput(
    accept='.zip'
)

decks = pn.Tabs()

def extract_file(file_name):
    with ZipFile(f'tmp/{file_name}.zip', 'r') as zipObj:
        zipObj.extractall(f'tmp/{file_name}')

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

file_input.param.watch(save_file, 'value')



# get_most_simultanious_deck(cards_map, 5) + get_most_simultanious_deck(cards_map, 6)


class ProxiesPage(pn.Column):
    def __init__(self, df):
        self.df = df
        self.df_obj = pn.pane.DataFrame(df, width=400)
        super().__init__(
            '# Proxies', 
            self.df_obj, 
            name='proxies')

df = load_decklists(f'tmp/ringsdb')
# loaded = DeckListPage('Decks carregados', df)
# decks.append(loaded)

cards_map = CardsMapPage(df)
decks.append(cards_map)

pn.Column(
    # '# Escolha um arquivo com decks para analisar',
    # file_input,
    # '(arquivo .zip com decks em formato .txt como exportado pelo RingsDB))',
    decks
).servable(target='main')


