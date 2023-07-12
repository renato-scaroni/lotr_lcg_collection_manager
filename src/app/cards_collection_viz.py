import pandas as pd
import panel as pn
from context_manager import ContextManager

pn.extension('tabulator', template='material')

def load_data():
    df1 = pd.read_csv('data_ingestion/data/cards.csv')
    df2 = pd.read_csv('data_ingestion/data/cards_rings_db_info.csv')

    df2.rename(columns={
        'type_name': 'type',
        'sphere_name': 'sphere',
        'pack_name': 'pack',
    }, inplace=True)
    df3 = df2.merge(df1, on=['name', 'type', 'sphere', 'pack'], how='left')

    df3.rename(columns={
        'quantity_x': 'quantity_in_pack',
        'quantity_y': 'quantity_in_collection',
    }, inplace=True)

    df3 = df3[[
        'name',
        'sphere',
        'pack',
        'quantity_in_pack', 
        'quantity_in_collection',
        'imagesrc'
    ]]
    
    return df3

df = load_data()
cm = ContextManager(df)

name_search = pn.widgets.AutocompleteInput(
    name='Search for a card by name:', 
    options=df.name.unique().tolist(),
    placeholder='Card name...',
    case_sensitive=False
)
name_search.param.watch(cm.name_search_handler, 'value_input')

sphere_selection = pn.widgets.RadioBoxGroup(
    name='Select a sphere:',
    options=['all']+df.sphere.unique().tolist(),
    inline=True,
    button_type='primary',
)
sphere_selection.param.watch(cm.sphere_selection_handler, 'value')

collection_select = pn.widgets.Switch(
    value= True
)
collection_select.param.watch(cm.collection_select_handler, 'value')
collection_select = pn.Row(
    'Show only cards in collection:',
    collection_select
)
sphere_and_collection_select = pn.Column(sphere_selection, collection_select)

pn.Column(
    pn.Row(name_search, sphere_and_collection_select),
    pn.Row(cm.df_widget, cm.box),
).servable()

