import os
import sys
 # setting path
sys.path.append('../')

from ringsdb import get_packs, get_cards_in_pack
from tqdm import tqdm
import pandas as pd


cycles = {
    'Shadows of Mirkwood': ['Core Set','Revised Core Set (Campaign Only)','Two-Player Limited Edition Starter','The Hunt for Gollum','Conflict at the Carrock','A Journey to Rhosgobel','The Hills of Emyn Muil','The Dead Marshes','Return to Mirkwood'],
    'Dwarrowdelf': ['Khazad-dûm','The Redhorn Gate','Road to Rivendell','The Watcher in the Water','The Long Dark','Foundations of Stone','Shadow and Flame'],
    'Against the Shadow': ['Heirs of Númenor',"The Steward's Fear",'The Drúadan Forest','Encounter at Amon Dîn','Assault on Osgiliath','The Blood of Gondor','The Morgul Vale'],
    'The Ring-maker': ['The Voice of Isengard','The Dunland Trap','The Three Trials','Trouble in Tharbad','The Nîn-in-Eilph',"Celebrimbor's Secret",'The Antlered Crown'],
    'Angmar Awakened': ['Angmar Awakened Campaign Expansion','The Lost Realm','The Wastes of Eriador','Escape from Mount Gram','Across the Ettenmoors','The Treachery of Rhudaur','The Battle of Carn Dûm','The Dread Realm'],
    'Dream-chaser': ['The Grey Havens','Flight of the Stormcaller','The Thing in the Depths','Temple of the Deceived','The Drowned Ruins','A Storm on Cobas Haven','The City of Corsairs'],
    'The Haradrim': ['The Sands of Harad','The Mûmakil','Race Across Harad','Beneath the Sands','The Black Serpent','The Dungeons of Cirith Gurat','The Crossings of Poros'],
    'Ered Mithrin': ['The Wilds of Rhovanion','The Withered Heath','Roam Across Rhovanion','Fire in the Night','The Ghost of Framsburg','Mount Gundabad','The Fate of Wilderland'],
    'The Vengeance of Mordor': ['A Shadow in the East','Wrath and Ruin','The City of Ulfast','Challenge of the Wainriders','Under the Ash Mountains','The Land of Sorrow','The Fortress of Nurn'],
    'The Hobbit': ['Over Hill and Under Hill', 'On the Doorstep'],
    'The Lord of the Rings': ['The Black Riders','The Road Darkens','The Treason of Saruman','The Land of Shadow','The Flame of the West','The Mountain of Fire'],
    'Standalone Scenarios': ['The Old Forest','Fog on the Barrow-downs','The Hunt for the Dreadnaught','The Dark of Mirkwood'],
    'Starter Decks': ['Dwarves of Durin','Elves of Lórien','Defenders of Gondor','Riders of Rohan']
}
packs = get_packs()
print('loading cards in packs')
cards = {p['code']:get_cards_in_pack(p['code']) for p in tqdm(packs, desc='loading cards in pack')}

cards_list = [card for card_list in cards.values() for card in card_list]


TEMP_FILES_FOLDER = 'data'
pd.DataFrame(cards_list).to_csv(f'{TEMP_FILES_FOLDER}/cards_rings_db_info.csv', index=False)