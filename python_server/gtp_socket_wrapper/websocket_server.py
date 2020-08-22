from subprocess import Popen, PIPE, STDOUT
import sys
import pexpect
import threading
import time
import socket
from websock.WebSocketServer import WebSocketServer

p = pexpect.spawn('./katago/katago gtp')
p.expect("GTP ready.*")
p.sendline("boardsize 9")
p.expect("=.*")
p.sendline("komi 5.5")
p.expect("=.*")
p.timeout = 1e4

t = None

def read_analysis(p,client,server):
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        line = p.readline()
        print(line)
        server.send(client,str(line))
    p.sendline("stop")
    print("stop reading output")

def on_connection_open(client):
    global t
    print("Connected")
    t = threading.Thread(target=read_analysis, args=(p,client,server))
    t.do_run = True
    t.start()

def on_connection_close(client):
    print("closed")
    t.do_run = False
    p.sendline("stop")
    t.join()

def on_data_receive(client, data):
    p.sendline(data)

server = WebSocketServer(ip="127.0.0.1", port=8030,
                         on_data_receive=on_data_receive,
                         on_connection_open=on_connection_open,
                         on_connection_close = on_connection_close)
server.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_thread = threading.Thread(target=server.serve_forever(), args=(), daemon=True)
server_thread.start()