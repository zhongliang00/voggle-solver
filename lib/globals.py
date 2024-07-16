import pickle
from pathlib import Path

ROWS = 4
COLS = 4
WORDLIST = pickle.load(open(Path(__file__).parent / 'dev_voggle_wordlist.pkl', 'rb'))
