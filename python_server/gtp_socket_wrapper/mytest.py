from subprocess import Popen, PIPE, STDOUT
import sys
import pexpect
import threading
import time
import socket
from websock.WebSocketServer import WebSocketServer

p = pexpect.spawn('katago gtp')
p.expect("GTP ready.*")
p.sendline("boardsize 9")
p.expect("=.*")
p.sendline("komi 5.5")
p.expect("=.*")
p.timeout = 1e4