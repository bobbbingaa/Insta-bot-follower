# panel.py
import asyncio, random, string, httpx, json, os, time, threading, sys
from datetime import datetime
from rich.console import Console; from rich.table import Table; from rich.prompt import IntPrompt, Prompt
console = Console()

CONFIG = {"target": "", "bots_wanted": 0, "delay": (2, 5), "proxy_file": "proxies.txt"}
PROXIES = open(CONFIG["proxy_file"]).read().splitlines() if os.path.exists(CONFIG["proxy_file"]) else []

class InstaBot:
    API = "https://www.instagram.com/api/v1/web"
    HEADERS = {
        "X-IG-App-ID": "936619743392459",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    def __init__(self, user, passw, proxy=None):
        self.s = httpx.Client(proxies={"all://": proxy} if proxy else None, timeout=15)
        self.user, self.passw = user, passw
        self.csrf = None
    def login(self):
        try:
            self.s.get("https://www.instagram.com/accounts/login/")
            self.csrf = self.s.cookies.get("csrftoken", "")
            payload = {
                "username": self.user,
                "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{self.passw}",
                "queryParams": "{}",
                "optIntoOneTap": "false"
            }
            r = self.s.post("https://www.instagram.com/api/v1/web/accounts/login/ajax/",
                            data=payload, headers={**self.HEADERS, "X-CSRFToken": self.csrf})
            return r.status_code == 200 and r.json().get("authenticated")
        except: return False
    def follow(self, target_id):
        try:
            url = f"{self.API}/friendships/{target_id}/follow/"
            r = self.s.post(url, headers={**self.HEADERS, "X-CSRFToken": self.csrf})
            return r.status_code == 200
        except: return False
    def get_id(self, username):
        try:
            r = self.s.get(f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
                           headers=self.HEADERS)
            return r.json()["data"]["user"]["id"]
        except: return None

def gen_creds(): return ''.join(random.choices(string.ascii_lowercase+string.digits, k=10))

def worker(idx):
    proxy = random.choice(PROXIES) if PROXIES else None
    bot = InstaBot(*[gen_creds() for _ in range(2)], proxy)
    if not bot.login():
        console.print(f"[red]Bot{idx} login fail"); return
    tid = bot.get_id(CONFIG["target"])
    if not tid:
        console.print(f"[red]Bot{idx} cannot resolve {CONFIG['target']}"); return
    if bot.follow(tid):
        console.print(f"[green]Bot{idx} followed {CONFIG['target']}")
    else:
        console.print(f"[yellow]Bot{idx} follow error")
    time.sleep(random.uniform(*CONFIG["delay"]))

def panel():
    console.rule("Instagram Bot Follower Panel")
    CONFIG["target"] = Prompt.ask("Target username (sans @)")
    CONFIG["bots_wanted"] = IntPrompt.ask("Combien de bots ?", default=50)
    table = Table(show_header=False, title="Resume")
    table.add_row("Target", CONFIG["target"])
    table.add_row("Bots", str(CONFIG["bots_wanted"]))
    console.print(table)
    if Prompt.ask("Lancer ? y/n") != "y": return
    threads = []
    for i in range(1, CONFIG["bots_wanted"]+1):
        t = threading.Thread(target=worker, args=(i,))
        t.start(); threads.append(t)
        time.sleep(0.2)
    for t in threads: t.join()
    console.print("[bold green]Done.")

if __name__ == "__main__":
    panel()
