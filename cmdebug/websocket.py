import socket
import os
import pdb
import cStringIO
import hashlib
import urlparse 
import struct
import array
import base64

def test(url, host):
    buf = cStringIO.StringIO()
    buf.write("GET /chat HTTP/1.1\x0d\x0a")
    buf.write("Host: %s\x0d\x0a" % host)
    buf.write("Upgrade: websocket\x0d\x0a")
    buf.write("Connection: Upgrade\x0d\x0a")
    buf.write("Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\x0d\x0a")
    buf.write("Sec-WebSocket-Protocol: chat, superchart\x0d\x0a")
    buf.write("Sec-WebSocket-Version: 13\x0d\x0a")
    buf.write("\x0d\x0a")
    final = buf.getvalue()

server_required_key = {
        "Host": None,
        "Sec-WebSocket-Key": None, 
        "Sec-WebSocket-Version": 13
        }

both_required_value = {
        "Connection": "Upgrade",
        "Upgrade": "websocket"
        } 

client_required_key = {
        "Sec-WebSocket-Accept": None
        }

#a continuation frame
CONT = 0x0
#a text frame
TEXT = 0x1
#a binary frame
BINARY = 0x2
#a connection close
CLOSE = 0x8
#a ping
PING = 0x9
#a pong
PONG = 0xa 


def gen_key():
    return base64.b64encode(os.urandom(16))

def gen_response_key(key):
    sha1 = hashlib.sha1()
    sha1.update(key) 
    sha1.update(b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11")
    return base64.b64encode(sha1.digest())

def server_header(header): 
    for k in client_required_key:
        if k not in header:
            raise KeyError("%s required in server header" % k)
    for k in both_required_value:
        if k not in header and header[k] != both_required_value[k]: 
            raise ValueError("Missing/Invalid WebSocket headers: %s" % k) 
    return "\x0d\x0a".join(["%s: %s" % (k, v) for k, v in header.items()])

def client_header(header):
    for k in server_required_key:
        if k not in header:
            raise KeyError("%s required in client header" % k)
    for k in both_required_value:
        if k not in header and header[k] != both_required_value[k]: 
            raise ValueError("Missing/Invalid WebSocket headers: %s" % k) 
    return "\x0d\x0a".join(["%s: %s" % (k, v) for k, v in header.items()])

def gen_handshake(url, header = {}): 
    components = urlparse.urlparse(url)
    if components.scheme != "ws":
        raise ValueError("websocket url only") 
    header.update(both_required_value)
    key = gen_key()
    header["Sec-WebSocket-Key"] = key
    header["Sec-WebSocket-Version"] = 13
    header["Host"] = components.netloc
    #send handshake 
    status = "GET %s HTTP/1.1\x0d\x0a" % components.path  
    context = {} 
    context["key"] = key
    context["header"] = "".join((status,
        client_header(header), "\x0d\x0a\x0d\x0a"))
    context["components"] = components
    return context

def parse_response(data): 
    status_mark = data.find("\x0d\x0a")
    if status_mark < 0:
        raise ValueError("Not a http header")
    _status = data[:status_mark].split(" ")
    data = data[status_mark+2:]
    if _status[0] != "HTTP/1.1":
        raise ValueError("HTTP 1.1 only")
    status = int(_status[1])
    if status != 101:
        raise ValueError("Websocket connect failed, 13/%d" % status) 
    header = {}
    header["status"] = status
    mark = data.find("\x0d\x0a\x0d\x0a") 
    if mark < 0:
        raise ValueError("Not a response header") 
    headers = data[:mark] 
    last = None

    for line in headers.splitlines():            
        if not line:
            continue 
        if line[0].isspace(): 
            #continuation of a multi-line header
            header[last] += " " + line.lstrip()
        else:
            name, value = line.split(":", 1)
            last = name
            header[name] = value.strip()
    return header       

def mask_data(mask, data):
    mask = array.array("B", mask)
    unmasked = array.array("B", data)
    for i in range(len(data)):
        unmasked[i] = unmasked[i] ^ mask[i % 4]
    return unmasked.tostring()   

def gen_frame(fin, opcode, data, mask=True):
    if fin:
        finbit = 0x80
    else:
        finbit = 0
    frame = struct.pack("B", finbit | opcode)
    l = len(data)
    if mask:
        mask_bit = 0x80
    else:
        mask_bit = 0
    if l < 126:
        frame += struct.pack("B", l | mask_bit)
    elif l <= 0xFFFF:
        frame += struct.pack("!BH", 126 | mask_bit, l)
    else:
        frame += struct.pack("!BQ", 127 | mask_bit, l)
    if mask:
        mask = os.urandom(4)
        data = mask + mask_data(mask, data) 
    return frame + data


parse_context = {
        "expect": 0, 
        "final_frame": 0,
        "frame_opcode": 0,
        "frame_is_control": 0,
        "frame_length": 0,
        "masking_key": 0,
        "this_chunk_len": 0,
        "frames": None
        }


def parse_frame(context, data): 
    if not isinstance(context["frames"], list):
        context["frames"] = []

    context["this_chunk_len"] = len(data)

    frame_buffer = cStringIO.StringIO(data) 

    if context["expect"]:
        if context["this_chunk_len"] > context["expect"]:
            if context["masked_frame"]:
                masked_data = mask_data(context["mask"],
                        frame_buffer.read(context["expect"]))
            else:
                masked_data = frame_buffer.read(context["expect"])
            context["frames"][-1] += masked_data
        else:
            if context["masked_frame"]:
                masked_data = mask_data(context["mask"],
                        frame_buffer.read())
            else:
                masked_data = frame_buffer.read()
            context["frames"][-1] += masked_data
            context["expect"] -= context["this_chunk_len"]
            frame_buffer.close()
            return

    #new frames in buffer
    while True: 
        header, payloadlen = struct.unpack("BB", frame_buffer.read(2)) 
        context["final_frame"] = header & 0x80
        context["reserved"] = header & 0x70
        context["frame_opcode"] = header & 0xf
        context["frame_is_control"] = context["frame_opcode"] & 0x8 

        if context["reserved"]: 
            raise ValueError("yet-undefined extensions") 
        context["masked_frame"] = bool(payloadlen & 0x80) 

        payloadlen = payloadlen & 0x7f 

        if context["frame_is_control"] and payloadlen >= 126:
            raise ValueError("control frames must have payload < 126") 
        context["frame_length"] = payloadlen 

        if payloadlen < 126:         
            pass 
        if payloadlen == 126:
            payloadlen = struct.unpack("!H", frame_buffer.read(2))[0]
        elif payloadlen == 127:
            payloadlen = struct.unpack("!Q", frame_buffer.read(8))[0]
        elif payloadlen > 127:
            raise Exception("Illegal payloadlen") 

        if context["masked_frame"]:
            context["mask"] = frame_buffer.read(4) 
        data_len = context["this_chunk_len"] - frame_buffer.tell()
        if data_len <= payloadlen: 
            context["expect"] = payloadlen - data_len
            if context["masked_frame"]: 
                data = mask_data(context["mask"], frame_buffer.read())
            else:
                data = frame_buffer.read()
            context["frames"].append(data)
            break
        else: 
            if context["masked_frame"]: 
                data = mask_data(context["mask"],
                        frame_buffer.read(payloadlen))
            else:
                data = frame_buffer.read(payloadlen)
            context["frames"].append(data) 
    frame_buffer.close()         
