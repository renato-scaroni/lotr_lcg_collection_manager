import pandas as pd
import panel as pn
import panel as pn
import param
from collections import namedtuple
from functools import reduce

pn.extension('tabulator', template='material')

class ContextManager:
    def __init__(self, df):
        self.df = df
        self.df_widget = pn.widgets.Tabulator(
            df, 
            page_size=9,
            show_index=False,
            layout='fit_columns',
            hidden_columns=['imagesrc'],
            sizing_mode='stretch_both'
        )

        self.df_widget.disabled = True
        self.df_widget.param.watch(self.update_grid_box_state, 'page')
        self.df_widget.on_click(self.update_grid_box_state)
        
        page = self.df.head(9).imagesrc.tolist()
        base_url = "https://ringsdb.com"
        imgs = [pn.pane.PNG(base_url+i) for i in page]
        self.box = pn.GridBox(
            *imgs, 
            ncols=3, 
            nrows=3,
            sizing_mode='stretch_width',
            max_width=525
        )
        Param = namedtuple('Param', ['new'])
        self.filters = {
            
        }
        self.collection_select_handler(Param(True))
    

    def update_global_context(self, df_filter, filter_label):
        if df_filter is None and filter_label in self.filters:
            self.filters[filter_label] = None

        self.filters[filter_label] = df_filter
        filters = filter(lambda x: x is not None, self.filters.values())
        df_filter = reduce(lambda x, y: x & y, filters)

        self.df_widget.value = self.df[df_filter]
        self.df_widget.param.trigger('value')
        
        self.update_grid_box_state()
        
    def update_grid_box_state(self, event=None):
        if not event:
            page = self.df_widget.current_view\
                .head(9)\
                .imagesrc\
                .tolist()
        elif type(event) == param.parameterized.Event and event.name == 'page':
            page_size = self.df_widget.page_size
            idx_init = (event.new-1) * page_size
            idx_end = idx_init + page_size
            page = self.df_widget.current_view\
                .iloc[idx_init:idx_end]\
                .imagesrc\
                .tolist()
        else:
            idx = event.row
            img = self.df_widget.current_view.iloc[idx].imagesrc
            page = [img]
        
        base_url = "https://ringsdb.com"
        imgs = [pn.pane.PNG(base_url+i) for i in page]
        self.box.objects = imgs

    def name_search_handler(self, event):
        if event.new:
            df_filter = self.df.name.str.contains(event.new, case=False)
            if event.new == '':
                df_filter = None
            self.update_global_context(df_filter, 'search')

    def sphere_selection_handler(self, event):
        if event.new == 'all':
            self.update_global_context(None, 'sphere')
        else:
            self.update_global_context(self.df.sphere == event.new, 'sphere')

    def collection_select_handler(self, event):
        if event.new:
            self.update_global_context(self.df.quantity_in_collection > 0, 'collection')
        else:
            self.update_global_context(None, 'collection')

def load_data():
    df1 = pd.read_csv('data/cards.csv')
    df2 = pd.read_csv('data/cards_rings_db_info.csv')

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

file_donwloader = pn.widgets.FileDownload(
    file='decks/decks.pdf', button_type='success', auto=False,
    embed=False, name="Right-click to download using 'Save as' dialog"
)

pn.Column(
    pn.Row(name_search, sphere_and_collection_select, file_donwloader),
    pn.Row(cm.df_widget, cm.box),
).servable()

