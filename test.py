from sqlitedict import SqliteDict
from go_game import Go_game,Rotater
import time
import random
import numpy as np
from tqdm import tqdm

mydict = SqliteDict('./python_server/books/kyu_5.5_Japanese.sqlite')
game = Go_game(Rotater(9),np.load("python_server/binfiles/zobrist.npy"))
game.set_pos_from_str("""
###########
#         #
#         #
#      W  #
#      WB #
#  BBB  B #
#   WB    #
#   WWBB  #
#     WW  #
#         #
###########""")
print(mydict[118966001714952367])
print(118966001714952367,game.do_hash())
print(game)