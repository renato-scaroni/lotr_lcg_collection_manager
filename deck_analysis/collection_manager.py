import pandas as pd
import panel as pn
import decks_utils as du

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

current_collection = [
    "Core Set",
    "Revised Core Set",
    "Revised Core Set (Campaign Only)",
    "Khazad-dûm",
    "The Lost Realm",
    "The Grey Havens",
    "The Wilds of Rhovanion",

    "The Dark of Mirkwood",
    "Conflict at the Carrock",
    "A Journey to Rhosgobel",
    "The Hills of Emyn Muil",
    "The Dead Marshes",
    "Return to Mirkwood",

    "The Long Dark",
    "Foundations of Stone",

    "The Wastes of Eriador",
    "Escape from Mount Gram",
    "Across the Ettenmoors",
    "The Treachery of Rhudaur",
    "The Battle of Carn Dûm",
    "The Dread Realm",

    "Over Hill and Under Hill",
    "The Black Riders",
    "The Road Darkens",
    
    "Dwarves of Durin",
    "Elves of Lórien",

    "The Hunt for Gollum",
] 


class CollectionManager(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.published_cards_per_pack = CollectionManager.get_all_published_cards()
        self.published_cards_count = self.published_cards_per_pack\
            .groupby(['name', 'sphere', 'type'])\
            .sum()\
            .reset_index()\
            .drop(columns=['pack'])
        self.packs_in_collection = current_collection

        self.packs_widget =  pn.widgets.CheckBoxGroup(
            name='Frequency',
            options=self.published_cards_per_pack['pack'].drop_duplicates().tolist(),
            value=self.packs_in_collection
        )
        
        self.packs_widget.param.watch(self.run_packs_cb, 'value')
        
        self.packs_cb = []
        
    def load_decklists(self, path):
        decks = du.load_decks(path)
        decklist_df = du.cards_in_decks(du.count_cards_in_deck, decks)
        return decklist_df

    def run_packs_cb(self, event):
        for cb in self.packs_cb:
            cb(event)       

    def add_packs_cb(self, cb):
        self.packs_cb.append(cb)
        
    def get_packs_selected(self):
        return self.packs_widget.value

    def get_cards_sphere_and_type(self, df):
        return df.merge(self.published_cards_per_pack.drop(columns=['quantity']), on=['name', 'pack'], how='left')

    @staticmethod
    def get_all_published_cards(base_path="data"):
        columns = ['name', 'sphere', 'type', 'pack', 'quantity']
        all_cards_rings_db = pd.read_csv(f"{base_path}/cards_rings_db_info.csv")
        rename_dict = {
            'sphere_name': 'sphere',
            'type_name': 'type',
            'pack_name': 'pack'
        }
        all_cards_rings_db.rename(columns=rename_dict, inplace=True)
        all_cards_rings_db = all_cards_rings_db[columns]

        revised_core_set = all_cards_rings_db[all_cards_rings_db.pack == 'Core Set'].copy()
        revised_core_set['quantity'] = revised_core_set.apply(lambda x: 3 if x['type'] != 'Hero' else 1, axis=1)
        revised_core_set['pack'] = 'Revised Core Set'

        all_cards_rings_db = pd.concat([all_cards_rings_db, revised_core_set])
        return all_cards_rings_db