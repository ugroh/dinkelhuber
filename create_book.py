import pickle
from go_game import Go_game,Rotater
import os,sys
import numpy as np
import logging

# create logger with 'root'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('create_book.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(file_formatter)
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
ch.setFormatter(console_formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
logger.debug("\n\n")

def convert_kyu_to_num(rat_str):
    if rat_str=="?":
        return -25
    elif "k" in rat_str:
        return -int(rat_str.replace("k", ""))
    elif "d" in rat_str:
        return int(rat_str.replace("d", ""))

def select_book(book,rating,komi,rules,gid):
    if rules in ("Korean","AGA","New Zealand","Ing"):
        logger.debug("{}: {} rules, skipping game".format(gid,rules))
        return None
    if komi is None:
        logger.debug("{}: Zero komi game, skipping".format(gid))
        return None
    if rating is None or rules not in ("Japanese", "Chinese"):
        logger.warn("{}: Missing info: rating {}, komi {}, rules {}".format(gid,rating,komi,rules))
        return None
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

def update_statistics(book,myhash,rating,win):
    if myhash in book:
        entry = book[myhash]
        games = entry[0]+entry[1]
        entry[2] = (entry[2]+rating/(games+1))/(1+1/(games+1))
        entry[int(win=="W")]+=1
    else:
        book[myhash] = np.array([int(win=="B"),int(win=="W"),rating],dtype=np.float32)

letter_map = "abcdefghi"
def convert_move_to_num(move_str):
    if len(move_str)==0:
        return tuple()
    return letter_map.index(move_str[0]), letter_map.index(move_str[1])

def extract_a_game(game,filepath,book,gid,max_half_moves=30):
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
            white_rating = convert_kyu_to_num(extract_val(line))
        elif line.startswith("RE"):
            if "W" in line:
                winner = "W"
            else:
                winner = "B"
        elif line.startswith("SZ"):
            if int(extract_val(line))!=9:
                logger.warn("{}: Invalid board size: {}".format(gid,line))
                return False
        elif line.startswith("HA") or line.startswith("AB"):
            logger.debug("{}: Invalid game, contains handicap".format(gid))
            return False
        elif line.startswith("KM"):
            komi = float(extract_val(line))
        elif line.startswith("RU"):
            rules = extract_val(line)
        elif blackbook is None and line.startswith(";B"):
            if winner is None:
                logger.warn("{}: Missing winner info, {}".format(gid,winner))
                return False
            blackbook = select_book(book,black_rating,komi,rules,gid)
            whitebook = select_book(book,white_rating,komi,rules,gid)
            if blackbook is None or whitebook is None:
                return False
        if line.startswith(";B") or line.startswith("(;B"):
            move = convert_move_to_num(extract_val(line))
            game.make_move(move)
            if blackbook is None:
                logger.warn("{}: blackbook is None, {}".format(gid,line))
                return False
            update_statistics(blackbook,hash(game),black_rating,winner)
            cur_move+=1
        if line.startswith(";W") or line.startswith("(;W"):
            move = convert_move_to_num(extract_val(line))
            game.make_move(move)
            if whitebook is None:
                logger.warn("{}: whitebook is None, {}".format(gid,line))
                return False
            update_statistics(whitebook,hash(game),white_rating,winner)
            cur_move+=1
        if cur_move>=max_half_moves:
            break
    return True

def create_book(gamefol="games"):
    book = {
        "dan":{
            "lower":{
                "Japanese":{},
                "Chinese":{}
            },
            "5.5":{
                "Japanese":{},
                "Chinese":{}
            },
            "higher":{
                "Japanese":{},
                "Chinese":{}
            }
        },
        "kyu":{
            "lower":{
                "Japanese":{},
                "Chinese":{}
            },
            "5.5":{
                "Japanese":{},
                "Chinese":{}
            },
            "higher":{
                "Japanese":{},
                "Chinese":{}
            }
        }
    }
    zobrist = np.load("zobrist.npy")
    go_game = Go_game(Rotater(9),zobrist,size=9)
    already_games = set()
    game_num = 0
    failed_num = 0
    pid_num = 0
    num_players = len(os.listdir(gamefol))
    for player_id in os.listdir(gamefol):
        logger.info("extracting from pid: {}".format(player_id))
        path = os.path.join(gamefol, player_id)
        for game in os.listdir(path):
            gid = game.split(".")[0]
            if gid in already_games:
                continue
            else:
                already_games.add(gid)
            filepath = os.path.join(path,game)
            res = extract_a_game(go_game,filepath,book,gid)
            if res:
                game_num += 1
            else:
                failed_num += 1
        pid_num+=1
        logger.info("Games extracted: {}, Games failed: {}, Players done: {}, Players left: {}".format(game_num,failed_num,pid_num,num_players-pid_num))
        if pid_num%10==0:
            logger.info("Saving")
            with open("book.pkl","wb") as f:
                pickle.dump(book,f)
    with open("book.pkl","wb") as f:
        pickle.dump(book,f)

if __name__ == "__main__":
    create_book()