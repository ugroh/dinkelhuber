import numpy as np
from sqlitedict import SqliteDict
import time

class Book_lookupper():
    def __init__(self,settings):
        self.books = {
            "dan":{
                "lower":{
                    "Japanese":SqliteDict("./books/dan_lower_Japanese.sqlite"),
                    "Chinese":SqliteDict("./books/dan_lower_Chinese.sqlite")
                },
                "5.5":{
                    "Japanese":SqliteDict("./books/dan_5.5_Japanese.sqlite"),
                    "Chinese":SqliteDict("./books/dan_5.5_Chinese.sqlite")
                },
                "higher":{
                    "Japanese":SqliteDict("./books/dan_higher_Japanese.sqlite"),
                    "Chinese":SqliteDict("./books/dan_higher_Chinese.sqlite")
                }
            },
            "kyu":{
                "lower":{
                    "Japanese":SqliteDict("./books/kyu_lower_Japanese.sqlite"),
                    "Chinese":SqliteDict("./books/kyu_lower_Chinese.sqlite")
                },
                "5.5":{
                    "Japanese":SqliteDict("./books/kyu_5.5_Japanese.sqlite"),
                    "Chinese":SqliteDict("./books/kyu_5.5_Chinese.sqlite")
                },
                "higher":{
                    "Japanese":SqliteDict("./books/kyu_higher_Japanese.sqlite"),
                    "Chinese":SqliteDict("./books/kyu_higher_Chinese.sqlite")
                }
            }
        }
        self.change_settings(settings)

    def merge_books(self,books):
        keys = set(sum([list(book.keys()) for book in books], []))
        new_book = dict()
        for key in keys:        
            white_wins = 0
            black_wins = 0
            rating = None
            num_games = 0
            for book in books:
                if key in book:
                    white_wins += book[key][0]
                    black_wins += book[key][1]
                    inner_games = book[key][0]+book[key][1]
                    num_games+=inner_games
                    if rating is None:
                        rating = book[key][2]
                    else:
                        rating = (rating + (inner_games/num_games)*book[key][2])/(1+(inner_games/num_games))
            new_book[key] = np.array([white_wins, black_wins, rating])
        return new_book

    def change_settings(self, settings):
        self.settings = settings
        self.cur_books = [self.books]
        for setting in self.settings:
            new_layer = []
            for book in self.cur_books:
                for ok_val in setting:
                    new_layer.append(book[ok_val])
            self.cur_books = new_layer

    def lookup_hash(self,myhash,with_games_tuples=True):
        cum_info = {"black_wins":0,"white_wins":0,"rating":0}
        if with_games_tuples:
            cum_info["games_tuples"] = []
        start = time.perf_counter()
        for book in self.cur_books:
            try:
                entry = book[myhash]
            except:
                pass
            else:
                cum_info["black_wins"] += entry[0]
                cum_info["white_wins"] += entry[1]
                new_games = entry[0]+entry[1]
                new_game_percent = new_games/(cum_info["black_wins"]+cum_info["white_wins"])
                cum_info["rating"] = (cum_info["rating"]*(1-new_game_percent)+new_game_percent*entry[2])
                if with_games_tuples:
                    cum_info["games_tuples"].extend(entry[3])
        print(time.perf_counter()-start)
        if with_games_tuples:
            cum_info["games_tuples"].sort(key=lambda x:-x[0])
        return cum_info

    def lookup_moves(self,moves_with_hash):
        moves_with_data = []
        for move,myhash in moves_with_hash:
            cum_info = self.lookup_hash(myhash,with_games_tuples=False)
            if cum_info["black_wins"]>0 or cum_info["black_wins"]>0:
                cum_info["move"] = move
                moves_with_data.append(cum_info)
        return moves_with_data