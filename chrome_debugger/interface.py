import json
import simple_http
from chrome_debugger import protocol

def get_app_list(url): 
    if url.endswith("/"):
        url += "json"
    else:
        url += "/json"
    _, _, data = simple_http.get(url)
    return json.loads(data)

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

def debugger_cansetscriptsource(context):    
    protocol.send_text(context, json.dumps({
        "id": context["id"],
        "method": "Debugger.canSetScriptSource"
        }))

def debugger_disable(context):
    protocol.send_text(context, json.dumps({
        "id": context["id"],
        "method": "Debugger.disable"
        }))

def debugger_enable(context):
    protocol.send_text(context, json.dumps({
        "id": context["id"],
        "method": "Debugger.enable"
        }))

def debugger_pause(context):
    protocol.send_text(context, json.dumps({
        "id": context["id"],
        "method": "Debugger.pause"
        }))

def debugger_resume(context):
    protocol.send_text(context, json.dumps({
        "id": context["id"],
        "method": "Debugger.resume"
        }))

def debugger_get_backtrace(context):
    protocol.send_text(context, json.dumps({
        "id": context["id"],
        "method": "Debugger.getBacktrace"
        }))

def debugger_get_source(context, id):
    protocol.send_text(context, json.dumps({ 
        "id": context["id"],
        "method": "Debugger.getScriptSource",
        "params": {
            "scriptId": id
            }
        }))

def tracing_start(context):
    protocol.send_text(context, json.dumps({
        "id": context["id"],
        "method": "Tracing.start",
        "categories": ""
        }))

def tracing_end(context): 
    protocol.send_text(context, json.dumps({
        "id": context["id"],
        "method": "Tracing.end"
        }))




