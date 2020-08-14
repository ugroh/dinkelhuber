import pickle
from go_game import Go_game,Rotater
import os,sys
import numpy as np
import logging
from tqdm import tqdm
from shove import Shove

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
    if rules in ("Korean","AGA","NZ","Ing"):
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

def update_statistics(book,game_info,myhash,player_color):
    avg_rating = (game_info["white_rating"]+game_info["black_rating"])/2
    player_rating = game_info["white_rating"] if player_color=="W" else game_info["black_rating"]
    #0: avg_rating, 1: ogs link, 2: black name, 3: white name, 4: black rating, 5: white rating, 6: winner, 7: year
    info_tuple = (avg_rating,game_info["ogs_link"],game_info["player_black"],game_info["player_white"],
                  game_info["black_rating"],game_info["white_rating"],game_info["winner"],game_info["year"])
    if myhash in book:
        entry = book[myhash]
        new_entry = entry[:3]+[entry[3].copy()]
        if new_entry[3][-1][0]<avg_rating:
            for i,val in enumerate(new_entry[3]):
                if val[0]<avg_rating:
                    new_entry[3].insert(i,info_tuple)
                    break
            new_entry[3] = new_entry[3][:4]
        elif len(new_entry[3])<4:
            new_entry[3].append(info_tuple)
        games = new_entry[0]+new_entry[1]
        new_entry[2] = (new_entry[2]+player_rating/(games+1))/(1+1/(games+1))
        new_entry[int(game_info["winner"]=="W")]+=1
        book[myhash] = new_entry
    else:
        book[myhash] = [int(game_info["winner"]=="B"),int(game_info["winner"]=="W"),player_rating,[info_tuple]]

letter_map = "abcdefghi"
def convert_move_to_num(move_str):
    if len(move_str)==0:
        return tuple()
    return letter_map.index(move_str[0]), letter_map.index(move_str[1])

def extract_a_game(game,filepath,book,gid,max_half_moves=20):
    def extract_val(line):
        return line.split("[")[1].split("]")[0]
    game.reset()
    komi = None
    rules = None
    usebook = None
    game_info = {}
    cur_move = 0
    with open(filepath,'r') as f:
        lines = f.read().splitlines()
    for line in lines:
        if line.startswith("BR"):
            game_info["black_rating"] = convert_kyu_to_num(extract_val(line))
        elif line.startswith("WR"):
            game_info["white_rating"] = convert_kyu_to_num(extract_val(line))
        elif line.startswith("PB"):
            game_info["player_black"] = extract_val(line)
        elif line.startswith("PW"):
            game_info["player_white"] = extract_val(line)
        elif line.startswith("DT"):
            game_info["year"] = extract_val(line).split("-")[0]
        elif line.startswith("RE"):
            if "W" in line:
                game_info["winner"] = "W"
            else:
                game_info["winner"] = "B"
        elif line.startswith("PC"):
            game_info["ogs_link"] = extract_val(line).replace("OGS: ","")
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
        elif usebook is None and line.startswith(";B"):
            if not "winner" in game_info:
                logger.warn("{}: Missing winner info".format(gid))
                return False
            usebook = select_book(book,(game_info["black_rating"]+game_info["white_rating"])/2,komi,rules,gid)
            if usebook is None:
                return False
            update_statistics(usebook,game_info,hash(game),"B" if (line.startswith(";B") or line.startswith("(;B")) else "W")
        if line.startswith(";B") or line.startswith("(;B") or line.startswith(";W") or line.startswith("(;W"):
            move = convert_move_to_num(extract_val(line))
            game.make_move(move)
            if usebook is None:
                logger.warn("{}: usebook is None, {}".format(gid,line))
                return False
            update_statistics(usebook,game_info,hash(game),"B" if (line.startswith(";B") or line.startswith("(;B")) else "W")
            cur_move+=1
        if cur_move>=max_half_moves:
            break
    return False if usebook is None else True

def create_book(gamefol="games"):
    book = {
        "dan":{
            "lower":{
                "Japanese":Shove("lite://python_server/books/dan_lower_Japanese.db"),
                "Chinese":Shove("lite://python_server/books/dan_lower_Chinese.db")
            },
            "5.5":{
                "Japanese":Shove("lite://python_server/books/dan_5.5_Japanese.db"),
                "Chinese":Shove("lite://python_server/books/dan_5.5_Chinese.db")
            },
            "higher":{
                "Japanese":Shove("lite://python_server/books/dan_higher_Japanese.db"),
                "Chinese":Shove("lite://python_server/books/dan_higher_Chinese.db")
            }
        },
        "kyu":{
            "lower":{
                "Japanese":Shove("lite://python_server/books/kyu_lower_Japanese.db"),
                "Chinese":Shove("lite://python_server/books/kyu_lower_Chinese.db")
            },
            "5.5":{
                "Japanese":Shove("lite://python_server/books/kyu_5.5_Japanese.db"),
                "Chinese":Shove("lite://python_server/books/kyu_5.5_Chinese.db")
            },
            "higher":{
                "Japanese":Shove("lite://python_server/books/kyu_higher_Japanese.db"),
                "Chinese":Shove("lite://python_server/books/kyu_higher_Chinese.db")
            }
        }
    }
    zobrist = np.load("python_server/binfiles/zobrist.npy")
    go_game = Go_game(Rotater(9),zobrist,size=9)
    already_games = set()
    game_num = 0
    failed_num = 0
    pid_num = 0
    num_players = len(os.listdir(gamefol))
    for player_id in os.listdir(gamefol):
        logger.info("extracting from pid: {}".format(player_id))
        path = os.path.join(gamefol, player_id)
        for game in tqdm(os.listdir(path)):
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

if __name__ == "__main__":
    create_book()