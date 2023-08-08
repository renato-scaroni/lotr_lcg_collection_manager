from functools import reduce

HEADER = r"""
\documentclass{article}
\usepackage{geometry}
\usepackage{multicol} % Para criar colunas múltiplas
\usepackage{lipsum}   % Para gerar texto de exemplo (pode remover essa linha)
\usepackage[dvipsnames]{xcolor}

\geometry{a4paper, margin=1cm}

\begin{document}

\begin{center}
    \huge Decks montados
\end{center}
\small
\vspace{1pt}
"""

def build_card_line(card):
    quantity = card['quantity']
    name = card['name'].split('(')[0].strip()
    colors = {
        'Leadership': 'purple',
        'Tactics': 'red',
        'Spirit': 'cyan',
        'Lore': 'green',
        'Neutral': 'black',
        'Baggins': 'brown',
        'Fellowship': 'Goldenrod',
    }
    return f"\\textcolor{{{colors[card['sphere']]}}} {{{quantity} x {name}}}\\\\"

def generate_latex(decks, header=HEADER):
    txt = header
    
    for i, d in enumerate(decks.groupby('deck_name')):
        if i % 3 == 0:
            txt += "\n\\begin{multicols}{3}"

        cards_per_type = d[1].groupby("type")

        txt += "\n\\begin{minipage}{.9\\linewidth}" + \
        "\n\\section*{\\large " + d[0] + "}"
        for type, cards in cards_per_type:
            cards = cards.to_dict('records')
            txt += f"\n\\textbf{{{type}}}\\\\"
            txt += reduce(lambda x,i: x+build_card_line(i), cards, "\n")
        txt += f"\n\\\\Total: {d[1].quantity.sum()}\\\\"
        txt += "\n\end{minipage}" + \
        "\n\\vspace{\\fill} % Adicionar espaço vertical igual para equilibrar as 3 divisões"

        if i % 3 == 2:
            txt += "\n\end{multicols}"

        # if i>1 and i % 5 == 0 :
        #     txt += "\n\\pagebreak"

    if not txt.endswith("\end{multicols}"):
        txt += """\n\end{multicols}"""
    txt += "\n\\vspace{1pt}\n"
    # txt += shared_cards[['name', 'sphere', 'type', 'quantity_in_collection', 'available_cards']].to_latex(index=False)
    return txt + "\n\end{document}"
