import sys
go_path = "."
qango_path = "."
sys.path.append(go_path)
sys.path.append(qango_path)
from go_handler import Go_handler
from qango_handler import Qango_handler
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
        self.go_handler = Go_handler()
        self.qango_handler = Qango_handler()

    def handle_get(self,uri,query):
        print("Received get request")
        if uri=="/":
            uri = "/html/go.html"
        elif uri.startswith("/qango"):
            return self.qango_handler(uri,query)
        try:
            if not path_is_parent(go_path,uri[1:]):
                return "NOT FOUND"
            with open(os.path.join(go_path,uri[1:]),"r") as f:
                my_content = f.read().encode()
        except FileNotFoundError:
            return "NOT FOUND"
        except UnicodeDecodeError as e:
            with open(os.path.join(go_path,uri[1:]),"rb") as f:
                my_content = f.read()
        return [my_content]

    def handle_post(self,data):
        self.go_handler.handle_post(data)

def application(environ, start_response):
    global handler
    try:  # This is disgusting!
        handler
    except:
        print("Creating the handler")
        handler = Stuff_handler()
    uri = environ["REQUEST_URI"]
    if environ["REQUEST_METHOD"] == "GET":
        d = parse_qs(environ['QUERY_STRING'])
        out = handler.handle_get(uri,d)
    elif environ["REQUEST_METHOD"] == "POST":
        post_input = json.loads(environ['wsgi.input'].readline().decode())
        out = handler.handle_post(post_input)
    if out == "NOT FOUND":
        start_response('404 NOT FOUND', [('Content-Type',"text/html")])
        return [b"404 NOT FOUND"]
    start_response('200 OK', [('Content-Type',handler.ending_to_content_type[uri.split(".")[-1]])])
    return out