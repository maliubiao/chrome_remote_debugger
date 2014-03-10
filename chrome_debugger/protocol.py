import socket
import json
import pdb
import simple_http
import urlparse 
from chrome_debugger import websocket


def connect(wsurl):
    context = websocket.gen_handshake(wsurl) 
    host = "localhost"
    port = 9222
    netloc = context["components"].netloc
    if ":" in netloc:
        host, port = netloc.split(":") 
        port = int(port) 
    sock = socket.create_connection((host, port))
    sock.send(context["header"]) 
    context["sock"] = sock
    context["id"] = 0
    return context 

def send_text(context, data): 
    gen = websocket.gen_frame(True, websocket.TEXT, data)
    context["sock"].send(gen)
    context["id"] += 1

def send_binary(context, data): 
    gen = websocket.gen_frame(True, websocket.BINARY, data)
    context["sock"].send(gen)
    context["id"] += 1

def close(context, status, message):
    gen = websockeet.gen_frame(True, websocket.CLOSE,
            struct.pack("!H", status) + message)
    context["sock"].send(gen)

def recv(context):
    parser = websocket.parse_context.copy()
    while True: 
        websocket.parse_frame(parser, context["sock"].recv(4096))        
        if not parser["expect"]:
            return parser["frames"] 

