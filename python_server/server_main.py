import sys
sys.path.append("..")
from go_game import Go_game,Rotater
from book_lookup import Book_lookupper
import pickle
import numpy as np
import webbrowser
import threading
import json
from http.server import HTTPServer,SimpleHTTPRequestHandler

class Post_handler(SimpleHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if self.path.endswith("html/go.html"):
            self.send_response(200)

            # Setting the header
            self.send_header("Content-type", "text/html")

            # Whenever using 'send_header', you also have to call 'end_headers'
            self.end_headers()
            with open("html/go.html","r") as f:
                my_content = f.read()
            self.wfile.write(my_content.encode())
        else:
            super().do_GET()

    def do_POST(self):
        # read the message and convert it into a python dictionary
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        print(data)
        if "revert" in data:
            print("before_revert",len(game.history))
            game.revert_move(data["revert"])
            print("after_revert",len(game.history))
        elif "forward" in data:
            game.forward(data["forward"])
        elif "move" in data:
            print("before_move",len(game.history))
            game.make_move(tuple(data["move"]))
            print("after_move",len(game.history))
        moves_with_hash = game.get_next_hashes()
        moves_with_data = book_handler.lookup_games(moves_with_hash)
        moves_with_data.sort(key=lambda x:-(x["white_wins"]+x["black_wins"]))
        print(game)
        return_data = {
            "position": [x.tolist() for x in game.position],
            "moves": moves_with_data
        }
        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps(return_data).encode())

def open_browser():
    """Start a browser after waiting for half a second."""
    def _open_browser():
        webbrowser.open('http://localhost:%s/%s' % (PORT, FILE))
    thread = threading.Timer(0.5, _open_browser)
    thread.start()

def start_server():
    """Start the server."""
    server_address = ("", PORT)
    server = HTTPServer(server_address, Post_handler)
    server.serve_forever()

if __name__ == '__main__':
    FILE = "html/go.html"
    PORT = 8080
    settings = [["dan","kyu"],["lower","5.5","higher"],["Japanese","Chinese"]]
    with open("../book.pkl","rb") as f:
        book = pickle.load(f)
    game = Go_game(Rotater(9),np.load("../zobrist.npy"),size=9)
    book_handler = Book_lookupper(book,settings)
    open_browser()
    start_server()