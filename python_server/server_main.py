import sys
sys.path.append("..")
from go_game import Go_game,Rotater
from sqlitedict import SqliteDict
from book_lookup import Book_lookupper,Lookup_api
import pickle
import numpy as np
import webbrowser
import threading
import json
import os
from datetime import datetime, timedelta
from load_sgf import load_sgf, sync_to_equal_move
from urllib.parse import parse_qs

def path_is_parent(parent_path, child_path):
    # Smooth out relative path names, note: if you are concerned about symbolic links, you should use os.path.realpath too
    parent_path = os.path.abspath(parent_path)
    child_path = os.path.abspath(child_path)

    # Compare the common path of the parent and child path with the common path of just the parent path. Using the commonpath method on just the parent path will regularise the path name in the same way as the comparison that deals with both paths, removing any trailing path separator
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])

class Stuff_handler():
    def __init__(self):
        self.ending_to_content_type = {
            "/":"text/html",
            "html": "text/html",
            "css": "text/css",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "json": "application/json"
        }
        self.id_expiration = {}
        self.settings = {}
        self.game = {}
        self.lookup_api = {}
        self.zobrist = np.load("binfiles/zobrist.npy")
        self.book_handler = Book_lookupper()
        self.read_visits()

    def read_visits(self):
        try:
            with open("visits.txt","r") as f:
                lines = f.read.splitlines()
                self.visits = int(lines[0].split(": ")[1])
                self.individual_visits = int(lines[1].split(": ")[1])
        except:
            self.individual_visits = 0
            self.visits = 0

    def write_visits(self):
        with open("visits.txt", "w") as f:
            f.write(f"visits: {self.visits}\nindividual visits: {self.individual_visits}")

    def handle_get(self,uri):
        print("Received get request")
        if uri=="/":
            uri = "/html/go.html"
        try:
            if not path_is_parent(".",uri[1:]):
                return "NOT FOUND"
            with open(uri[1:],"r") as f:
                my_content = f.read().encode()
        except FileNotFoundError:
            return "NOT FOUND"
        except UnicodeDecodeError as e:
            with open(uri[1:],"rb") as f:
                my_content = f.read()
        return [my_content]

    def expire_ids(self):
        today = datetime.now()
        for go_id,expiration_date in list(self.id_expiration.items()):
            if today > expiration_date:
                del self.settings[go_id]
                del self.game[go_id]
                del self.id_expiration[go_id]
                del self.lookup_api[go_id]

    def handle_post(self,data):
        self.visits += 1
        print(data)
        go_id = data["go_id"]

        if not go_id in self.id_expiration:
            self.individual_visits+=1
            self.settings[go_id] = [["dan","kyu"],["lower","5.5","higher"],["Japanese"]]
            self.game[go_id] = Go_game(Rotater(9),self.zobrist,size=9)
            self.lookup_api[go_id] = Lookup_api(self.settings[go_id],self.book_handler)
        self.id_expiration[go_id] = datetime.now()+timedelta(days=5)

        if self.visits%20 == 1:
            self.write_visits()
            self.expire_ids()
        
        if "request" in data:
            if data["request"] == "settings":
                return_data = {"settings":self.settings[go_id]}
        else:
            return_data = {}
            if "game_sgf" in data:
                new_game = load_sgf(data["game_sgf"])
                self.game[go_id],made_moves = sync_to_equal_move(self.game[go_id],new_game)
                return_data["made_moves"] = [["reset",True]]+self.game[go_id].convert_gtp_readable(made_moves)
            elif "reset" in data:
                self.game[go_id].reset()
                return_data["made_moves"] = [["reset",True]]
            elif "revert" in data:
                reverted = self.game[go_id].revert_move(data["revert"])
                return_data["made_moves"] = [["undo",reverted]]
            elif "forward" in data:
                made_moves = self.game[go_id].forward(data["forward"])
                if made_moves:
                    return_data["made_moves"] = self.game[go_id].convert_gtp_readable(made_moves)
                else:
                    move = tuple(self.moves_with_data[0]["move"])
                    return_data["made_moves"] = self.game[go_id].convert_gtp_readable([[self.game[go_id].onturn,move]])
                    self.game[go_id].make_move(move)
            elif "move" in data:
                move = tuple(data["move"])
                return_data["made_moves"] = self.game[go_id].convert_gtp_readable([[self.game[go_id].onturn,move]])
                self.game[go_id].make_move(move)
            elif "settings" in data:
                self.settings[go_id] = data["settings"]
                self.lookup_api[go_id].change_settings(self.settings[go_id])
            moves_with_hash = self.game[go_id].get_next_hashes()
            self.moves_with_data = self.lookup_api[go_id].lookup_moves(moves_with_hash)
            self.moves_with_data.sort(key=lambda x:-(x["white_wins"]+x["black_wins"]))
            cur_info = self.lookup_api[go_id].lookup_hash(self.game[go_id].do_hash(),with_games_tuples=True)
            print(self.game[go_id])
            return_data.update({
                "position": [x.tolist() for x in self.game[go_id].position],
                "moves": self.moves_with_data,
                "pos_info":cur_info,
                "onturn":self.game[go_id].onturn
            })
        return [json.dumps(return_data).encode()]

def application(environ, start_response):
    global handler
    try:  # This is disgusting!
        handler
    except:
        print("Creating the handler")
        handler = Stuff_handler()
    uri = environ["REQUEST_URI"]
    if environ["REQUEST_METHOD"] == "GET":
        out = handler.handle_get(uri)
    elif environ["REQUEST_METHOD"] == "POST":
        post_input = json.loads(environ['wsgi.input'].readline().decode())
        out = handler.handle_post(post_input)
    if out == "NOT FOUND":
        start_response('404 NOT FOUND', [('Content-Type',"text/html")])
        return [b"404 NOT FOUND"]
    start_response('200 OK', [('Content-Type',handler.ending_to_content_type[uri.split(".")[-1]])])
    return out