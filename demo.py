import pdb
import json
from pprint import pprint
from chrome_debugger import protocol
from chrome_debugger import interface
from chrome_debugger import websocket

context = protocol.connect("ws://localhost:9222/devtools/page/D08C4454-9122-6CC8-E492-93A22F9C9727")

header = websocket.parse_response(context["sock"].recv(4096)) 

interface.debugger_enable(context)

while True:
    pprint(protocol.recv(context))
    
