import numpy as np
from sqlitedict import SqliteDict
import time
import os,sys
basepath = os.path.abspath(os.path.dirname(__file__))

class Book_lookupper():
    def __init__(self):
        self.books = {
            "dan":{
                "lower":{
                    "Japanese":SqliteDict(os.path.join(basepath,"python_server","books/dan_lower_Japanese.sqlite")),
                    "Chinese":SqliteDict(os.path.join(basepath,"python_server","books/dan_lower_Chinese.sqlite"))
                },
                "5.5":{
                    "Japanese":SqliteDict(os.path.join(basepath,"python_server","books/dan_5.5_Japanese.sqlite")),
                    "Chinese":SqliteDict(os.path.join(basepath,"python_server","books/dan_5.5_Chinese.sqlite"))
                },
                "higher":{
                    "Japanese":SqliteDict(os.path.join(basepath,"python_server","books/dan_higher_Japanese.sqlite")),
                    "Chinese":SqliteDict(os.path.join(basepath,"python_server","books/dan_higher_Chinese.sqlite"))
                }
            },
            "kyu":{
                "lower":{
                    "Japanese":SqliteDict(os.path.join(basepath,"python_server","books/kyu_lower_Japanese.sqlite")),
                    "Chinese":SqliteDict(os.path.join(basepath,"python_server","books/kyu_lower_Chinese.sqlite"))
                },
                "5.5":{
                    "Japanese":SqliteDict(os.path.join(basepath,"python_server","books/kyu_5.5_Japanese.sqlite")),
                    "Chinese":SqliteDict(os.path.join(basepath,"python_server","books/kyu_5.5_Chinese.sqlite"))
                },
                "higher":{
                    "Japanese":SqliteDict(os.path.join(basepath,"python_server","books/kyu_higher_Japanese.sqlite")),
                    "Chinese":SqliteDict(os.path.join(basepath,"python_server","books/kyu_higher_Chinese.sqlite"))
                }
            }
        }

    def lookup_hash(self,myhash,cur_books,with_games_tuples=True):
        cum_info = {"black_wins":0,"white_wins":0,"rating":0}
        if with_games_tuples:
            cum_info["games_tuples"] = []
        for book in cur_books:
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
        if with_games_tuples:
            cum_info["games_tuples"].sort(key=lambda x:-x[0])
        return cum_info

    def lookup_moves(self,moves_with_hash,cur_books):
        moves_with_data = []
        for move,myhash in moves_with_hash:
            cum_info = self.lookup_hash(myhash,cur_books,with_games_tuples=False)
            if cum_info["black_wins"]>0 or cum_info["white_wins"]>0:
                cum_info["move"] = move
                moves_with_data.append(cum_info)
        return moves_with_data

class Lookup_api():
    def __init__(self,settings,book_lookupper):
        self.lookupper = book_lookupper
        self.change_settings(settings)

    def change_settings(self, settings):
        self.settings = settings
        self.cur_books = [self.lookupper.books]
        for setting in self.settings:
            new_layer = []
            for book in self.cur_books:
                for ok_val in setting:
                    new_layer.append(book[ok_val])
            self.cur_books = new_layer

    def lookup_hash(self,myhash,with_games_tuples=True):
        return self.lookupper.lookup_hash(myhash,self.cur_books,with_games_tuples=True)
    
    def lookup_moves(self,moves_with_hash):
        return self.lookupper.lookup_moves(moves_with_hash,self.cur_books)