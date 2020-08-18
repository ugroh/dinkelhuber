import sys
sys.path.append("..")
from go_game import Go_game,Rotater
from sqlitedict import SqliteDict
from book_lookup import Book_lookupper
import pickle
import numpy as np
import webbrowser
import threading
import json
import os,sys
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
        self.settings = [["dan","kyu"],["lower","5.5","higher"],["Japanese"]]
        self.game = Go_game(Rotater(9),np.load("binfiles/zobrist.npy"),size=9)
        self.book_handler = Book_lookupper(self.settings)
        self.password = sys.argv[1] if len(sys.argv) > 1 else ""

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

    def handle_post(self,data):
        print(data)
        if (not "password" in data) or data["password"]!=self.password:
            return_data = {"password":"wrong"}
        else:
            if "request" in data:
                if data["request"] == "settings":
                    return_data = {"settings":self.settings}
            else:
                if "revert" in data:
                    self.game.revert_move(data["revert"])
                elif "forward" in data:
                    success = self.game.forward(data["forward"])
                    if not success:
                        self.game.make_move(tuple(self.moves_with_data[0]["move"]))
                elif "move" in data:
                    self.game.make_move(tuple(data["move"]))
                if "settings" in data:
                    self.settings = data["settings"]
                    self.book_handler.change_settings(self.settings)
                moves_with_hash = self.game.get_next_hashes()
                print("looking up games")
                self.moves_with_data = self.book_handler.lookup_moves(moves_with_hash)
                print("looked up games")
                self.moves_with_data.sort(key=lambda x:-(x["white_wins"]+x["black_wins"]))
                cur_info = self.book_handler.lookup_hash(self.game.do_hash(),with_games_tuples=True)
                print(self.game)
                return_data = {
                    "position": [x.tolist() for x in self.game.position],
                    "moves": self.moves_with_data,
                    "pos_info":cur_info
                }
        return [json.dumps(return_data).encode()]

def application(environ, start_response):
    #get_input = parse_qs(environ['QUERY_STRING'])
    if handler is None:
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

handler = None