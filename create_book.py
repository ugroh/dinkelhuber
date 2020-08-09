import pickle
from go_game import Go_game,Rotater
import os,sys
import numpy as np

def convert_kyu_to_num(rat_str):
    if "k" in rat_str:
        return -int(rat_str.replace("k", ""))
    elif "d" in rat_str:
        return int(rat_str.replace("d", ""))

def select_book(book,rating,komi,rules):
    if rating is None or komi is None or rules not in ("Japanese", "Chinese"):
        return "Missing info: rating {}, komi {}, rules {}".format(rating,komi,rules)
    if rating>0:
        mybook = book["dan"]
    else:
        mybook = book["kyu"]
    if komi == 5.5:
        mybook = mybook["5.5"]
    elif komi < 5.5:
        mybook = mybook["lower"]
    elif komi > 5.5:
        mybook = mybook["higher"]
    mybook = mybook[rules]
    return mybook

def update_statistics(book,myhash,rating,win)
    if myhash in book:
        entry = book[myhash]
        games = entry[0]+entry[1]
        entry[2] = (entry[2]+rating/games)/(1+1/games)
        entry[win=="W"]+=1
    else:
        book[myhash] = np.array([win=="B",win=="W",rating],dtype=np.float32)

letter_map = "abcdefghi"
def convert_move_to_num(move_str):
    return letter_map.index(move_str[0]), letter_map.index(move_str[1])

def extract_a_game(game,filepath,book,max_half_moves=30):
    def extract_val(line):
        return line.split("[")[1].split("]")[0]
    game.reset()
    black_rating = None
    white_rating = None
    komi = None
    rules = None
    winner = None
    blackbook = None
    whitebook = None
    cur_move = 0
    with open(filepath,'r') as f:
        lines = f.read().splitlines()
    for line in lines:
        if line.startswith("BR"):
            black_rating = convert_kyu_to_num(extract_val(line))
        elif line.startswith("WR"):
            white_rating = convert_kyu_to_num(extract_val(line))ä
        elif line.startswith("RE"):
            if "W" in line:
                winner = "W"
            else:
                winner = "B"
        elif line.startswith("SZ"):
            if int(extract_val(line))!=9:
                return "Error: invalid board size: {}".format(line)
        elif line.startswith("KM"):
            komi = float(extract_val(line))
        elif line.startswith("RU"):
            rules = extract_val(line)
        elif blackbook is None and line.startswith(";B"):
            if winner is None:
                return "Missing winner info, {}".format(winner)
            blackbook = select_book(book,black_rating,komi,rules)
            whitebook = select_book(book,white_rating,komi,rules)
            if type(blackbook) == str:
                return blackbook
            if type(whitebook) == str:
                return whitebook
        if line.startswith(";B") or line.startswith("(;B"):
            move = convert_move_to_num(extract_val(line))
            game.make_move(move)
            update_statistics(blackbook,hash(game),black_rating,winner)
            cur_move+=1
        if line.startswith(";W") or line.startswith("(;W"):
            move = convert_move_to_num(extract_val(line))
            game.make_move(move)
            update_statistics(whitebook,hash(game),white_rating,winner)
            cur_move+=1
        if cur_move>=max_half_moves:
            break
    return True