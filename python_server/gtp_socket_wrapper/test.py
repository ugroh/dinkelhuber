import time
import threading
from websock.WebSocketServer import WebSocketServer

def sendobert(client,server):
    while 1:
        server.send(client,"wuff")
        server.send(client,"tuff")
        print("sended")
        time.sleep(1)

def on_connection_open(client):
    """
    Called by the WebSocket server when a new connection is opened.
    """
    print("Connected")
    t = threading.Thread(target=sendobert, args=(client,server))
    t.start()

def on_connection_close(client):
    print("closed")


def on_data_receive(client, data):
    """
    Called by the WebSocket server when data is received.
    """
    print(data)

server = WebSocketServer(ip="127.0.0.1", port=8030,
                         on_data_receive=on_data_receive,
                         on_connection_open=on_connection_open,
                         on_connection_close = on_connection_close)
server_thread = threading.Thread(target=server.serve_forever(), args=(), daemon=True)
server_thread.start()