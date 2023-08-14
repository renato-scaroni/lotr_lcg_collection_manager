import panel as pn
import os
from zipfile import ZipFile
from datetime import datetime
import decks_utils as du
from itertools import combinations
from deck_list_page import DeckListPage
from cards_map_page import CardsMapPage

pn.extension('tabulator', template='fast')

class MainApp(pn.Column):
    def __init__(self):
        self.main_area = pn.Tabs()
        self.file_input = pn.widgets.FileInput(
            accept='.zip'
        )
        self.file_input.param.watch(self.save_file, 'value')
        
        
        super().__init__(
            '# Deck Analysis',
            self.file_input,
            '# Escolha um arquivo com decks para analisar',
            '(arquivo .zip com decks em formato .txt como exportado pelo RingsDB))',
            self.main_area
       )
        
    def save_file(self, event):
        self.file_input.loading = True
        os.makedirs('tmp', exist_ok=True)
        self.file_input.loading = True
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"decks_{ts}"
        self.file_input.save(f'tmp/{file_name}.zip')
        with ZipFile(f'tmp/{file_name}.zip', 'r') as zipObj:
            zipObj.extractall(f'tmp/{file_name}')

        df = self.load_decklists(f'tmp/{file_name}')
        cards_map = CardsMapPage(df)
        self.main_area.append(cards_map)

        loaded = DeckListPage('Decks carregados', df)
        self.main_area.append(loaded)

        self.file_input.loading = False

    def load_decklists(self, path):
        decks = du.load_decks(path)
        decklist_df = du.cards_in_decks(du.count_cards_in_deck, decks)
        return decklist_df


MainApp().servable(target='main')
