import sys
import json
import pdb

from cmdebug import websocket 
from cmdebug import protocol 
from cmdebug import interface


def main():
    content = interface.get_app_list(sys.argv[1]) 
    for page in content: 
        print "============"
        print "title:", page["title"]
        print "url:", page["url"]
        print "debug:", page["webSocketDebuggerUrl"]
if __name__ == "__main__":
    main()

