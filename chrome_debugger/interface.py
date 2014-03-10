import json
import simple_http
from chrome_debugger import protocol

def get_app_list(url): 
    if url.endswith("/"):
        url += "json"
    else:
        url += "/json"
    _, _, content = simple_http.get(url)
    return json.loads(content)

def console_clear_messages(context):
    protocol.send_text(context, json.dumps({
        "id": context["id"],
        "method": "Console.clearMessages"
        }))

def console_enable(context):
    protocol.send_text(context, json.dumps({
        "id": context["id"],
        "method": "Console.enable"
        }))

def console_disable(context):
    protocol.send_text(context, json.dumps({
        "id": context["id"],
        "method": "Console.disable"
        }))









