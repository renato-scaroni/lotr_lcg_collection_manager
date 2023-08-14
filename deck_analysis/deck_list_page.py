import panel as pn

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
