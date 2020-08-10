import sys
sys.path.append("..")
from go_game import Go_game,Rotater
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
        if self.path.endswith("go.html"):
            self.send_response(200)

            # Setting the header
            self.send_header("Content-type", "text/html")

            # Whenever using 'send_header', you also have to call 'end_headers'
            self.end_headers()
            with open("go.html","r") as f:
                my_content = f.read()
            self.wfile.write(my_content.encode())
        else:
            super().do_GET()

    def do_POST(self):
        # read the message and convert it into a python dictionary
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        if "move" in data:
            game.make_move(data["move"])
        
        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps(movevals).encode())

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
    game = Go_game(Rotater(9),np.load("../zobrist.npy"),size=9)
    open_browser()
    start_server()