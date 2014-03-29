import pdb
import json
import sys
import os.path
import base64
from pprint import pprint
from cmdebug import protocol
from cmdebug import interface
from cmdebug import websocket

def get_scripts(context, params):
        if "url" not in params: 
            return 
        if params["url"].startswith("http"): 
            interface.debugger_get_source(context, params["scriptId"]) 
            path =  os.path.basename(str(params["url"]))
            if not path: 
                path = os.urandom(2).encode("hex")+ ".js"
            f = open(path, "w")
            content = "".join(protocol.recv(context)) 
            try:
                f.write(json.loads(content)["result"]["scriptSource"].encode("utf-8")) 
            except:
                pdb.set_trace()
            f.close() 
            print "done: ", params["url"]
    
def main(): 
    context = protocol.connect(sys.argv[1]) 
    interface.debugger_enable(context) 
    while True:
        frames = protocol.recv(context) 
        if not frames: 
            break
        for frame in frames: 
            o = json.loads(frame)
            if "params" not in o:
                continue 
            params = o["params"] 
            if "method" not in o: 
                continue 
            if o["method"] == "Debugger.scriptParsed":
                get_scripts(context, params)
    print "done"
if __name__ == "__main__":
    main()
