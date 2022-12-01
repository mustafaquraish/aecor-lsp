import socket
import json
import subprocess
import re

class Server:
    def __init__(self, conn):
        self.conn = conn

    def recv_line(self):
        line = b''
        while True:
            c = self.conn.recv(1)
            line += c
            if c == b'\n':
                break
        return line.decode()

    def get_req(self):
        content_len = 0
        while True:
            line = self.recv_line().strip("\r\n")
            if line == "":
                break
            if line.startswith("Content-Length:"):
                content_len = int(line.split(":")[1])

        print("[+] Content-Length:", content_len)
        content = self.conn.recv(content_len)
        return json.loads(content.decode())

    def get_find_response(self, file, line, col):
        if file.startswith("file://"):
            file = file[7:]
        # LSP indexed are 0-based, but we are 1-based
        command = ["./find", file, str(line + 1), str(col + 1)]
        print("    [+] Running:", " ".join(command))
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        out, _ = proc.communicate()
        print("----")
        print(out.decode())
        print("----")
        return out.decode()

    def send_message(self, request, data):
        if "id" not in request:
            return
        base_req = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": data
        }
        text = json.dumps(base_req)
        resp = (
            "Content-Type: application/vscode-jsonrpc; charset=utf-8\r\n"
            f"Content-Length: {len(text)}\r\n"
            "\r\n"
            f"{text}"
        )
        self.conn.send(resp.encode())

    def handle_initialize(self, request):
        print("[+] LSP Initialize")
        self.send_message(request, {
            "serverInfo": {
                "name": "aecor lsp server",
                "version": "0.1",
            },
            "capabilities": {
                "hoverProvider": True,
                "definitionProvider": True,
            }
        })
        return True

    def handle_initialized(self, request):
        print("[+] LSP Initialized")
        self.send_message(request, None)
        return True

    def handle_hover(self, request):
        print("[+] LSP Hover")
        file = request["params"]["textDocument"]["uri"]
        line = request["params"]["position"]["line"]
        col = request["params"]["position"]["character"]
        print(f"    [+] {file}:{line}:{col}")

        # txt = json.dumps(request["params"]["position"])
        # self.send_message(request, {
        #     "contents": txt 
        # })
        # return True

        out = self.get_find_response(file, line, col)
        if "Found usage:" in out:
            typ = re.search("- type: (.*)\\n", out).group(1)
            typ = typ.replace("<", "[").replace(">", "]")
            self.send_message(request, {
                "contents": {
                    "value": typ,
                    "language": "aecor"
                }
            })

        else:
            self.send_message(request, None)
        return True
    
    def handle_definition(self, request):
        print("[+] LSP Definition")
        file = request["params"]["textDocument"]["uri"]
        line = request["params"]["position"]["line"]
        col = request["params"]["position"]["character"]
        print(f"    [+] {file}:{line}:{col}")

        # txt = json.dumps(request["params"]["position"])
        # self.send_message(request, {
        #     "contents": txt 
        # })
        # return True

        out = self.get_find_response(file, line, col)
        if "Found usage:" in out:
            loc = re.search("- loc: (.*)\\n", out).group(1)

            file, line, col = loc.split(":")

            self.send_message(request, {
                "uri": f'file://{file}',
                "range": {
                    "start": { "line": int(line) - 1, "character": int(col) - 1 },
                    "end": { "line": int(line) - 1, "character": int(col) - 1 },
                }
            })

        else:
            self.send_message(request, None)
        return True

    def handle_did_open(self, request):
        print("[+] LSP Did Open")
        file = request["params"]["textDocument"]["uri"]
        print("    [+] File:", file)
        self.send_message(request, None)
        return True

    def handle_completion(self, request):
        print("[+] LSP Completion")
        file = request["params"]["textDocument"]["uri"]
        line = request["params"]["position"]["line"]
        col = request["params"]["position"]["character"]
        print(f"    [+] {file}:{line}:{col}")

        out = self.get_find_response(file, line, col)
        if "Found usage:" in out:
            res = re.search("- type: (.*)\\n", out)
            typ = res.group(1)
            res = re.search("- loc: (.*)\\n", out)
            loc = res.group(1)
            print(f"    [+] type: '{typ}'   loc: '{loc}'")

        self.send_message(request, {
            "isIncomplete": False,
            "items": [
                {
                    "label": "foo",
                    "detail": "foo",
                },
                {
                    "label": "bar",
                    "detail": "bar",
                }
            ]
        })
        return True

    def handle_shutdown(self, request):
        print("[+] LSP Shutdown")
        self.send_message(request, None)
        return False

    def handle_exit(self, request):
        print("[+] LSP Exit")
        self.send_message(request, None)
        return False


    def run(self):
        print("[+] Server started")
        running = True
        while running:
            request = self.get_req()
            method = request["method"]
            match method:
                case "initialize":
                    running = self.handle_initialize(request)
                case "initialized":
                    running = self.handle_initialized(request)
                case "textDocument/hover":
                    running = self.handle_hover(request)
                case "textDocument/didOpen":
                    running = self.handle_did_open(request)
                case "textDocument/completion":
                    running = self.handle_completion(request)
                case "textDocument/definition":
                    running = self.handle_definition(request)
                case "shutdown":
                    running = self.handle_shutdown(request)
                case "exit":
                    running = self.handle_exit(request)
                case _:
                    if method.startswith("$/"):
                        print("[+] Ignoring unhandle notification ", method)
                    else:
                        print("[+] Unhandle request ", method, ", exiting")
                        running = False


HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 3333  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        Server(conn).run()
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)