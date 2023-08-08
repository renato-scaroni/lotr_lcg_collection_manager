import decks_utils as du
import pdf_generator as pdf
import os 

LATEX_DIR = 'latex/'
PDF_DIR = 'pdf/'

decks = du.load_decks('./decks/')
decklist_df = du.cards_in_decks(du.count_cards_in_deck, decks)
all_cards = du.load_all_cards_df()
shared_cards = du.get_used_cards_in_collection(decklist_df, all_cards)

def try_create_dir(directory):
    try:
        # Create target Directory
        os.makedir(directory)
        print("Directory " , directory ,  " Created ") 
    except FileExistsError:
        print("Directory " , directory ,  " already exists")   

try_create_dir(LATEX_DIR)
with open(f'{LATEX_DIR}/decks.tex', 'w') as f:
    txt = pdf.generate_latex(shared_cards)
    f.write(txt)
    f.close()

os.system(f"pdflatex -output-directory={LATEX_DIR} decks.tex")

try_create_dir(PDF_DIR)
if os.path.isfile(LATEX_DIR + 'decks.pdf'):
    os.rename(LATEX_DIR + 'decks.pdf', PDF_DIR + 'decks.pdf')