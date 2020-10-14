import sys,os
import json
go_path = "."
qango_path = "."
sys.path.append(go_path)
sys.path.append(qango_path)
from go_handler import Go_handler
from qango_handler import Qango_handler
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
        self.go_handler = Go_handler()
        self.qango_handler = Qango_handler()

    def handle_get(self,uri,query):
        print("Received get request")
        if uri=="/":
            uri = "/html/go.html"
        elif uri.startswith("/qango"):
            return self.qango_handler(uri,query)
        path = os.path.join(go_path,uri[1:])
        try:
            if not path_is_parent(go_path,path):
                return "NOT FOUND"
            with open(path,"r") as f:
                my_content = f.read().encode()
        except FileNotFoundError:
            return "NOT FOUND"
        except UnicodeDecodeError as e:
            with open(path,"rb") as f:
                my_content = f.read()
        return [my_content]

    def handle_post(self,data):
        return self.go_handler.handle_post(data)

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
    if uri.split(".")[-1] in handler.ending_to_content_type:
        ct = handler.ending_to_content_type[uri.split(".")[-1]]
    else:
        ct = "text/plain"
    start_response('200 OK', [('Content-Type',ct)])
    return out