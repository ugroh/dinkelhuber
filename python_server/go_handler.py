import sys,os
basepath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(basepath,".."))
sys.path.append(os.path.join(basepath,"..",".."))
from db_manager import Go_user
from flask_app_provider import db
from go_game import Go_game,Rotater
from sqlitedict import SqliteDict
from book_lookup import Book_lookupper,Lookup_api
import pickle
import numpy as np
import webbrowser
import threading
import time
import json
from datetime import datetime, timedelta
from load_sgf import load_sgf, sync_to_equal_move
from urllib.parse import parse_qs
from flask import jsonify, render_template

class Go_handler():
    def __init__(self):
        self.zobrist = np.load(os.path.join(basepath,"binfiles/zobrist.npy"))
        self.book_handler = Book_lookupper()

    def handle_get(self,uid):
        user = Go_user.query.filter_by(uid=uid).first()
        if user is not None:
            user.last_access = int(time.time())
            db.session.commit()
        self.expire_ids()
        return render_template("go.html")

    def expire_ids(self):
        Go_user.query.filter(Go_user.last_access<time.time()-3600*48).delete()
        db.session.commit()

    def handle_post(self,data,uid):
        if self.book_handler.books is None:
            print("loading books")
            self.book_handler.set_books()
            print("loaded books")

        user = Go_user.query.filter_by(uid=uid).first()
        if user is None:
            game = Go_game(self.zobrist,size=9)
            setting = [["dan","kyu"],["lower","5.5","higher"],["Japanese"]]
            user = Go_user(uid=uid,game=json.dumps(game.get_dump_list()),settings=json.dumps(setting),last_access=int(time.time()))
            db.session.add(user)
        else:
            game = Go_game.from_dump(user.game,self.zobrist)
            setting = json.loads(user.settings)
            user.last_access = int(time.time())
        lookup_api = Lookup_api(setting,self.book_handler)
        
        if "request" in data:
            if data["request"] == "settings":
                return_data = {"settings":setting}
        else:
            return_data = {}
            if "game_sgf" in data:
                new_game = load_sgf(data["game_sgf"],self.zobrist)
                game,made_moves = sync_to_equal_move(game,new_game)
                return_data["made_moves"] = [["reset",True]]+game.convert_gtp_readable(made_moves)
            elif "reset" in data:
                game.reset()
                return_data["made_moves"] = [["reset",True]]
            elif "revert" in data:
                reverted = game.revert_move(data["revert"])
                return_data["made_moves"] = [["undo",reverted]]
            elif "forward" in data:
                made_moves = game.forward(data["forward"])
                if made_moves:
                    return_data["made_moves"] = game.convert_gtp_readable(made_moves)
                else:
                    move = tuple(self.moves_with_data[0]["move"])
                    return_data["made_moves"] = game.convert_gtp_readable([[game.onturn,move]])
                    game.make_move(move)
            elif "move" in data:
                move = tuple(data["move"])
                return_data["made_moves"] = game.convert_gtp_readable([[game.onturn,move]])
                game.make_move(move)
            elif "settings" in data:
                user.settings = json.dumps(data["settings"])
                lookup_api.change_settings(data["settings"])
            moves_with_hash = game.get_next_hashes()
            self.moves_with_data = lookup_api.lookup_moves(moves_with_hash)
            self.moves_with_data.sort(key=lambda x:-(x["white_wins"]+x["black_wins"]))
            cur_info = lookup_api.lookup_hash(game.do_hash(),with_games_tuples=True)
            return_data.update({
                "position": [x.tolist() for x in game.position],
                "moves": self.moves_with_data,
                "pos_info":cur_info,
                "onturn":game.onturn,
                "movenum":game.hist_index
            })
            user.game = json.dumps(game.get_dump_list())
        db.session.commit()
        return jsonify(return_data)

go_handler = Go_handler()