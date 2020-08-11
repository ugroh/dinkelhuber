import sys
sys.path.append("..")
from go_game import Go_game,Rotater
from book_lookup import Book_lookupper
import pickle
import numpy as np
import webbrowser
import threading
import json
from urllib.parse import parse_qs

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
        with open("binfiles/book.pkl","rb") as f:
            self.book = pickle.load(f)
        self.game = Go_game(Rotater(9),np.load("binfiles/zobrist.npy"),size=9)
        self.book_handler = Book_lookupper(self.book,self.settings)

    def handle_get(self,uri):
        if uri=="/":
            uri = "/html/go.html"
        try:
            with open(uri[1:],"r") as f:
                my_content = f.read().encode()
        except FileNotFoundError:
            return False
        except UnicodeDecodeError as e:
            with open(uri[1:],"rb") as f:
                my_content = f.read()
        return [my_content]

    def handle_post(self,data):
        print(data)
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
            self.moves_with_data = self.book_handler.lookup_games(moves_with_hash)
            self.moves_with_data.sort(key=lambda x:-(x["white_wins"]+x["black_wins"]))
            print(self.game)
            return_data = {
                "position": [x.tolist() for x in self.game.position],
                "moves": self.moves_with_data
            }
        return [json.dumps(return_data).encode()]

def application(environ, start_response):
    #get_input = parse_qs(environ['QUERY_STRING'])
    uri = environ["REQUEST_URI"]
    if environ["REQUEST_METHOD"] == "GET":
        out = handler.handle_get(uri)
    elif environ["REQUEST_METHOD"] == "POST":
        post_input = json.loads(environ['wsgi.input'].readline().decode())
        out = handler.handle_post(post_input)
    if not out:
        start_response('404 NOT FOUND', [('Content-Type',"text/html")])
        return [b""]    
    start_response('200 OK', [('Content-Type',handler.ending_to_content_type[uri.split(".")[-1]])])
    return out

handler = Stuff_handler()