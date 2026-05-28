#!/usr/bin/env python3
"""
Dev AI - Multi-Theme Edition v3.0
Themes: ocean, hacker, amber, frost, nord, rose, dracula
Switch theme: theme <name>
"""

import os, sys, json, subprocess, tempfile, time, random, threading, requests, webbrowser, re, textwrap
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from groq import Groq
from ddgs import DDGS
from datetime import datetime

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    print("\033[1;31m\n  ERROR: GROQ_API_KEY not set!\033[0m")
    print("\033[1;33m  Run: export GROQ_API_KEY='your_key_here'\033[0m\n")
    sys.exit(1)

client = Groq(api_key=GROQ_API_KEY)

HISTORY_FILE = os.path.expanduser("~/.dev_history.json")
PERSONA_FILE = os.path.expanduser("~/.dev_persona.json")
TODO_FILE    = os.path.expanduser("~/.dev_todos.json")
CONFIG_FILE  = os.path.expanduser("~/.dev_config.json")

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

# ── All Themes ────────────────────────────────────────────────────────────────
THEMES = {
    "ocean": {
        "name":    "Ocean Dark",
        "primary": "\033[38;2;130;170;255m",
        "accent":  "\033[38;2;127;219;202m",
        "text":    "\033[38;2;238;255;255m",
        "muted":   "\033[38;2;99;119;119m",
        "dark":    "\033[38;2;29;51;84m",
        "success": "\033[38;2;195;232;141m",
        "warn":    "\033[38;2;255;203;107m",
        "error":   "\033[38;2;240;113;120m",
        "special": "\033[38;2;199;146;234m",
        "symbol":  "◈",
        "user_sym":"~",
        "sep":     "━",
        "box_tl":  "╭", "box_tr": "╮", "box_bl": "╰", "box_br": "╯",
        "box_h":   "─", "box_v":  "│",
        "bar":     "▎",
    },
    "hacker": {
        "name":    "Hacker Green",
        "primary": "\033[38;2;0;255;65m",
        "accent":  "\033[38;2;0;200;50m",
        "text":    "\033[38;2;180;255;180m",
        "muted":   "\033[38;2;0;100;20m",
        "dark":    "\033[38;2;0;50;10m",
        "success": "\033[38;2;0;255;65m",
        "warn":    "\033[38;2;180;255;100m",
        "error":   "\033[38;2;255;80;80m",
        "special": "\033[38;2;100;255;150m",
        "symbol":  "▶",
        "user_sym":"root@dev:~$",
        "sep":     "▓",
        "box_tl":  "┌", "box_tr": "┐", "box_bl": "└", "box_br": "┘",
        "box_h":   "─", "box_v":  "│",
        "bar":     "▎",
    },
    "amber": {
        "name":    "Amber Retro",
        "primary": "\033[38;2;255;140;0m",
        "accent":  "\033[38;2;204;102;0m",
        "text":    "\033[38;2;255;200;100m",
        "muted":   "\033[38;2;122;61;0m",
        "dark":    "\033[38;2;60;20;0m",
        "success": "\033[38;2;255;170;50m",
        "warn":    "\033[38;2;255;220;100m",
        "error":   "\033[38;2;255;80;30m",
        "special": "\033[38;2;255;160;80m",
        "symbol":  "◆",
        "user_sym":"❯",
        "sep":     "═",
        "box_tl":  "╔", "box_tr": "╗", "box_bl": "╚", "box_br": "╝",
        "box_h":   "═", "box_v":  "║",
        "bar":     "▎",
    },
    "frost": {
        "name":    "Frost White",
        "primary": "\033[38;2;59;130;246m",
        "accent":  "\033[38;2;51;112;212m",
        "text":    "\033[38;2;15;23;42m",
        "muted":   "\033[38;2;100;116;139m",
        "dark":    "\033[38;2;203;213;225m",
        "success": "\033[38;2;34;197;94m",
        "warn":    "\033[38;2;234;179;8m",
        "error":   "\033[38;2;239;68;68m",
        "special": "\033[38;2;139;92;246m",
        "symbol":  "›",
        "user_sym":"›",
        "sep":     "─",
        "box_tl":  "┌", "box_tr": "┐", "box_bl": "└", "box_br": "┘",
        "box_h":   "─", "box_v":  "│",
        "bar":     "│",
    },
    "nord": {
        "name":    "Nord Arctic",
        "primary": "\033[38;2;136;192;208m",
        "accent":  "\033[38;2;129;161;193m",
        "text":    "\033[38;2;236;239;244m",
        "muted":   "\033[38;2;76;86;106m",
        "dark":    "\033[38;2;59;66;82m",
        "success": "\033[38;2;163;190;140m",
        "warn":    "\033[38;2;235;203;139m",
        "error":   "\033[38;2;191;97;106m",
        "special": "\033[38;2;180;142;173m",
        "symbol":  "❄",
        "user_sym":"›",
        "sep":     "─",
        "box_tl":  "╭", "box_tr": "╮", "box_bl": "╰", "box_br": "╯",
        "box_h":   "─", "box_v":  "│",
        "bar":     "▎",
    },
    "rose": {
        "name":    "Rose Gold",
        "primary": "\033[38;2;255;107;157m",
        "accent":  "\033[38;2;255;215;0m",
        "text":    "\033[38;2;248;248;248m",
        "muted":   "\033[38;2;45;45;78m",
        "dark":    "\033[38;2;30;30;60m",
        "success": "\033[38;2;100;220;130m",
        "warn":    "\033[38;2;255;215;0m",
        "error":   "\033[38;2;255;80;80m",
        "special": "\033[38;2;200;150;255m",
        "symbol":  "✦",
        "user_sym":"›",
        "sep":     "━",
        "box_tl":  "╭", "box_tr": "╮", "box_bl": "╰", "box_br": "╯",
        "box_h":   "─", "box_v":  "│",
        "bar":     "▎",
    },
    "dracula": {
        "name":    "Dracula",
        "primary": "\033[38;2;189;147;249m",
        "accent":  "\033[38;2;255;121;198m",
        "text":    "\033[38;2;248;248;242m",
        "muted":   "\033[38;2;68;71;90m",
        "dark":    "\033[38;2;40;42;54m",
        "success": "\033[38;2;80;250;123m",
        "warn":    "\033[38;2;241;250;140m",
        "error":   "\033[38;2;255;85;85m",
        "special": "\033[38;2;255;184;108m",
        "symbol":  "⚡",
        "user_sym":"›",
        "sep":     "─",
        "box_tl":  "╭", "box_tr": "╮", "box_bl": "╰", "box_br": "╯",
        "box_h":   "─", "box_v":  "│",
        "bar":     "▎",
    },
}

DANGEROUS = ["rm -rf","rmdir","mkfs","dd if","shutdown","reboot","chmod 777","sudo rm"]
BOX  = 62
WRAP = 80
conversation_history = []

# ── TTS ───────────────────────────────────────────────────────────────────────
_tts_proc = None
_tts_lock = threading.Lock()

def speak(text, voice="Samantha"):
    global _tts_proc
    clean = " ".join(l for l in text.split("\n") if not l.startswith("```")).strip()
    if not clean: return
    with _tts_lock:
        if _tts_proc and _tts_proc.poll() is None:
            _tts_proc.kill(); _tts_proc.wait()
        try:
            _tts_proc = subprocess.Popen(["say","-v",voice,clean],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass

def speak_wait(text, voice="Samantha"):
    speak(text, voice)
    global _tts_proc
    if _tts_proc: _tts_proc.wait()

def stop_speaking():
    global _tts_proc
    with _tts_lock:
        if _tts_proc and _tts_proc.poll() is None:
            _tts_proc.kill(); _tts_proc.wait()

# ── Config ────────────────────────────────────────────────────────────────────
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f: return json.load(f)
        except: return {}
    return {}

def save_config(c):
    with open(CONFIG_FILE,"w") as f: json.dump(c,f,indent=2)

def get_user_name():
    cfg = load_config()
    if cfg.get("name"): return cfg["name"]
    os.system("clear")
    w = get_terminal_width()
    print()
    print("\033[1;36m" + "  Welcome to Dev AI!".center(w) + RESET)
    print("\033[0;37m" + "  Let's get you set up.".center(w) + RESET)
    print()
    while True:
        name = input("\033[1;36m  Your name: \033[0m").strip()
        if name:
            cfg["name"] = name; save_config(cfg)
            print(f"\n  Nice to meet you, {name}!\n")
            return name
        print("  Please enter your name.")

def get_city():
    cfg = load_config()
    if cfg.get("city"): return cfg["city"]
    try:
        r = requests.get("https://ipapi.co/city/", timeout=5)
        city = r.text.strip()
        if city and len(city) < 50:
            cfg["city"] = city; save_config(cfg); return city
    except: pass
    return "Chennai"

def get_theme_name():
    cfg = load_config()
    return cfg.get("theme", "ocean")

def save_theme(name):
    cfg = load_config()
    cfg["theme"] = name; save_config(cfg)

def set_city(new_city, T, voice):
    cfg = load_config(); cfg["city"] = new_city; save_config(cfg)
    print(T["success"] + f"\n  ◦ City updated to: {new_city}\n" + RESET)
    speak(f"City updated to {new_city}.", voice)

# ── Personas ──────────────────────────────────────────────────────────────────
PERSONAS = {
    "dev":    {"name":"Dev",    "voice":"Samantha","desc":"Professional coder & problem solver",
               "prompt":"You are Dev, a professional AI assistant in the Mac terminal. Be concise and practical. Use code blocks for code. When asked to open a URL respond ONLY: OPEN_URL: https://url.com — When asked to run a command respond ONLY: RUN_CMD: command — Safe read-only only."},
    "mentor": {"name":"Mentor", "voice":"Karen",   "desc":"Patient teacher who explains everything",
               "prompt":"You are Mentor, a patient encouraging teacher. Explain clearly with examples. OPEN_URL: url — RUN_CMD: command"},
    "buddy":  {"name":"Buddy",  "voice":"Daniel",  "desc":"Friendly & casual coding friend",
               "prompt":"You are Buddy, fun friendly coding companion. Be casual and helpful. OPEN_URL: url — RUN_CMD: command"},
    "sage":   {"name":"Sage",   "voice":"Alex",    "desc":"Deep thinker for architecture & design",
               "prompt":"You are Sage, a wise software architect. Think deeply. OPEN_URL: url — RUN_CMD: command"},
    "turbo":  {"name":"Turbo",  "voice":"Fred",    "desc":"Ultra fast, no fluff, just answers",
               "prompt":"You are Turbo, extremely fast and direct. Shortest correct answer. OPEN_URL: url — RUN_CMD: command"},
}

SITE_MAP = {
    "github":"https://github.com","youtube":"https://youtube.com","google":"https://google.com",
    "twitter":"https://twitter.com","x":"https://x.com","linkedin":"https://linkedin.com",
    "stackoverflow":"https://stackoverflow.com","reddit":"https://reddit.com",
    "gmail":"https://mail.google.com","drive":"https://drive.google.com",
    "notion":"https://notion.so","vercel":"https://vercel.com","netlify":"https://netlify.com",
    "replit":"https://replit.com","claude":"https://claude.ai","chatgpt":"https://chatgpt.com",
    "instagram":"https://instagram.com","whatsapp":"https://web.whatsapp.com",
}

NEWS_CATEGORIES = {
    "1":("Technology","latest technology AI news today"),
    "2":("Finance","finance stock market news today"),
    "3":("Economy","economy economic news today"),
    "4":("World","world news today top stories"),
    "5":("India","India news today top stories"),
    "6":("Sports","sports cricket IPL news today India"),
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def strip_ansi(t):
    return re.sub(r'\033\[[0-9;]*m|\033\[38;2;[0-9;]*m','',t)

def get_terminal_width():
    try: return os.get_terminal_size().columns
    except: return 100

def clear_screen(): os.system("clear")

def load_persona():
    if os.path.exists(PERSONA_FILE):
        try:
            with open(PERSONA_FILE) as f: return json.load(f).get("persona","dev")
        except: return "dev"
    return "dev"

def save_persona(n):
    with open(PERSONA_FILE,"w") as f: json.dump({"persona":n},f)

def get_greeting(user_name):
    h = datetime.now().hour
    tg = "Good morning" if 5<=h<12 else "Good afternoon" if 12<=h<17 else "Good evening" if 17<=h<21 else "Good night"
    return random.choice([
        f"{tg}, {user_name}! Ready to build something great?",
        f"Hey {user_name}! Great to see you again.",
        f"Welcome back, {user_name}! What are we creating today?",
        f"{tg}, {user_name}! I am here and ready.",
        f"Hello {user_name}! Let's make today productive.",
    ])

def get_farewell(user_name):
    return random.choice([
        f"Goodbye, {user_name}! Have a great day!",
        f"See you later, {user_name}! Take care.",
        f"Bye {user_name}! Come back anytime.",
        f"Catch you later, {user_name}!",
        f"Goodbye {user_name}! Stay awesome.",
    ])

def get_datetime_line():
    now = datetime.now()
    return f"{now.strftime('%A, %B %d, %Y')}  ◦  {now.strftime('%I:%M %p')}"

def type_out(text, color, delay=0.025):
    for ch in text:
        print(color+ch+RESET, end="", flush=True)
        time.sleep(delay)
    print()

# ── Box drawing ───────────────────────────────────────────────────────────────
def draw_box_line(content, T, bw):
    raw = strip_ansi(content)
    max_c = bw - 4
    if len(raw) > max_c:
        content = content[:max_c-3] + T["muted"] + "..." + RESET
        raw = strip_ansi(content)
    sp = bw - 2 - len(raw)
    return T["primary"] + T["box_v"] + RESET + content + " "*max(0,sp) + T["primary"] + T["box_v"] + RESET

def draw_box(lines, T, title=None, w=None):
    if w is None: w = get_terminal_width()
    bw  = min(w-4, BOX)
    pad = " "*max(0,(w-bw)//2)
    print()
    print(pad + T["primary"] + T["box_tl"] + T["box_h"]*(bw-2) + T["box_tr"] + RESET)
    if title:
        print(pad + draw_box_line(f"  {T['accent']}{title}{RESET}", T, bw))
        print(pad + T["primary"] + "├" + T["box_h"]*(bw-2) + "┤" + RESET)
    for line in lines:
        print(pad + draw_box_line(line, T, bw))
    print(pad + T["primary"] + T["box_bl"] + T["box_h"]*(bw-2) + T["box_br"] + RESET)
    print()

# ── Print reply (FIXED: full wrap, left border) ───────────────────────────────
def print_reply(text, T):
    """Print Dev reply with left border and proper 80-char word wrap. No mid-word breaks."""
    bar    = T["primary"] + "  " + T["bar"] + RESET
    tw     = min(WRAP, get_terminal_width() - 8)
    in_code = False
    print()
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
            print(bar + T["warn"] + " " + line + RESET)
            continue
        if in_code:
            print(bar + T["warn"] + " " + line + RESET)
            continue
        # word-wrap at tw chars
        wrapped = textwrap.wrap(line, width=tw) if line.strip() else [""]
        if not wrapped: wrapped = [""]
        for wl in wrapped:
            print(bar + T["accent"] + " " + wl + RESET)
    print()

def thinking_animation(stop_event, T):
    frames = [
        T["primary"] + f"  {T['symbol']} " + T["muted"] + "thinking   " + RESET,
        T["primary"] + f"  {T['symbol']} " + T["muted"] + "thinking ◦ " + RESET,
        T["primary"] + f"  {T['symbol']} " + T["muted"] + "thinking ◦◦" + RESET,
        T["primary"] + f"  {T['symbol']} " + T["muted"] + "thinking ◦◦◦"+RESET,
    ]
    i = 0
    while not stop_event.is_set():
        print(f"\r{frames[i%len(frames)]}", end="", flush=True)
        time.sleep(0.18)
        i += 1
    print("\r"+" "*35+"\r", end="", flush=True)

def status_bar(start_time, reply, persona_name, T):
    elapsed = int((time.time()-start_time)*1000)
    words   = len(reply.split())
    now     = datetime.now().strftime("%I:%M %p")
    w       = get_terminal_width()
    print(T["muted"] + "  " + T["sep"]*max(0,w-4) + RESET)
    print(f"  {T['primary']}{T['symbol']} {persona_name}{RESET}  {T['muted']}◦{RESET}  {T['muted']}{elapsed}ms{RESET}  {T['muted']}◦{RESET}  {T['muted']}{words} words{RESET}  {T['muted']}◦{RESET}  {T['muted']}{now}{RESET}")
    print(T["muted"] + "  " + T["sep"]*max(0,w-4) + RESET)
    print()

# ── Theme switcher UI ─────────────────────────────────────────────────────────
def show_themes(current_theme, T):
    lines = []
    for key, th in THEMES.items():
        active = T["success"]+" ✓"+RESET if key==current_theme else ""
        lines.append(f"  {T['warn']}{key:<12}{RESET}{T['text']}{th['name']}{RESET}{active}")
    draw_box(lines, T, title="Switch Theme")
    print(f"  {T['muted']}Type: theme ocean / theme hacker / theme amber / theme frost / theme nord / theme rose / theme dracula{RESET}\n")

# ── Splash Screen ─────────────────────────────────────────────────────────────
def splash_screen(T, returning=False, msg_count=0, current_persona="dev", user_name="Friend"):
    clear_screen()
    w  = get_terminal_width()
    p  = PERSONAS[current_persona]
    logo = [
        "██████╗ ███████╗██╗   ██╗",
        "██╔══██╗██╔════╝██║   ██║",
        "██║  ██║█████╗  ██║   ██║",
        "██║  ██║██╔══╝  ╚██╗ ██╔╝",
        "██████╔╝███████╗ ╚████╔╝ ",
        "╚═════╝ ╚══════╝  ╚═══╝  ",
    ]
    print()
    print(T["muted"] + T["sep"]*w + RESET)
    print()
    for line in logo:
        print(T["primary"] + line.center(w) + RESET)
    print()
    print(T["muted"] + "Professional AI Terminal Assistant".center(w) + RESET)
    print(T["muted"] + f"Powered by Groq  ◦  llama-3.3-70b  ◦  {T['name']}".center(w) + RESET)
    print()
    print(T["muted"] + T["sep"]*w + RESET)
    print()
    print(T["muted"] + get_datetime_line().center(w) + RESET)
    print()
    print(T["primary"] + f"{T['symbol']} {p['name']}  ◦  {p['desc']}".center(w) + RESET)
    print()
    print(T["muted"] + T["sep"]*w + RESET)
    print()
    greeting = get_greeting(user_name)
    type_out(" "*max(0,(w-len(greeting))//2)+greeting, T["accent"], 0.025)
    if returning:
        print(T["muted"] + f"  I remember {msg_count} past messages.".center(w) + RESET)
    print()
    print(T["muted"] + T["sep"]*w + RESET)
    print()
    items = [
        ("v","voice input"),("search: x","web search"),("open <site>","open website"),
        ("todo","to-do list"),("git <cmd>","git helper"),("persona","switch persona"),
        ("briefing","daily briefing"),("read <file>","read & explain file"),
        ("city <name>","change city"),("sysinfo","system monitor"),
        ("theme <name>","switch theme"),("history","past chats"),
        ("clear memory","forget everything"),("exit","quit"),
    ]
    mid   = (len(items)+1)//2
    left  = items[:mid]; right = items[mid:]
    col_w = 40
    pad   = " "*max(0,(w-col_w*2)//2)
    for i in range(max(len(left),len(right))):
        lc,ld = left[i]  if i<len(left)  else ("","")
        rc,rd = right[i] if i<len(right) else ("","")
        l = f"{T['warn']}{T['user_sym']} {lc:<16}{RESET}{T['muted']}{ld}{RESET}" if lc else ""
        r = f"{T['warn']}{T['user_sym']} {rc:<16}{RESET}{T['muted']}{rd}{RESET}" if rc else ""
        l_raw = f"{T['user_sym']} {lc:<16}{ld}" if lc else ""
        l_pad = " "*max(0,col_w-len(l_raw))
        print(pad+l+l_pad+r)
    print()
    print(T["muted"] + T["sep"]*w + RESET)
    print()
    for i in range(5):
        bar = T["primary"]+"◈"*i+T["muted"]+"◦"*(4-i)+RESET
        print(f"\r  {bar}  {T['muted']}loading...{RESET}", end="", flush=True)
        time.sleep(0.1)
    print(f"\r  {T['primary']}◈◈◈◈{RESET}  {T['accent']}ready!{RESET}          ")
    print()
    speak_wait(greeting, p["voice"])

def farewell_screen(T, user_name, voice):
    msg = get_farewell(user_name)
    w   = get_terminal_width()
    print()
    print(T["muted"] + T["sep"]*w + RESET)
    print()
    type_out(" "*max(0,(w-len(msg))//2)+msg, T["accent"], 0.035)
    print()
    print(T["muted"] + T["sep"]*w + RESET)
    speak_wait(msg, voice)
    print()

# ── Weather & News ────────────────────────────────────────────────────────────
def get_weather(city):
    try:
        r = requests.get(f"https://wttr.in/{city}?format=%C+%t+Humidity:%h+Wind:%w", timeout=6)
        return r.text.strip()
    except: return "Weather unavailable"

def get_top_news(query="top news India today"):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=4))
        if not results: return []
        return [{"title":r.get("title","")[:48],"body":r.get("body","")[:90],"source":r.get("source","")[:20]} for r in results]
    except: return []

def pick_news_category(T, voice):
    lines = []
    for key,(name,_) in NEWS_CATEGORIES.items():
        lines.append(f"  {T['warn']}{key}.{RESET}  {T['text']}{name}{RESET}")
    draw_box(lines, T, title="Pick your news category")
    speak("What type of news? Technology, Finance, Economy, World, India, or Sports?", voice)
    choice = input(T["primary"]+f"  {T['symbol']} Pick 1-6 (Enter for India): "+RESET+T["text"]).strip()
    print(RESET, end="")
    if choice in NEWS_CATEGORIES:
        name,query = NEWS_CATEGORIES[choice]
        speak(f"Getting {name} news.", voice)
        return name, query
    return "India","India top news today"

def morning_briefing(T, voice, user_name, city):
    w   = get_terminal_width()
    bw  = min(w-4, BOX)
    pad = " "*max(0,(w-bw)//2)
    now = datetime.now()

    category_name, news_query = pick_news_category(T, voice)
    weather = get_weather(city)
    news    = get_top_news(news_query)

    print()
    print(pad+T["primary"]+T["box_tl"]+T["box_h"]*(bw-2)+T["box_tr"]+RESET)
    print(pad+draw_box_line(f"  {T['accent']}Daily Briefing  {T['muted']}◦  {T['text']}{user_name}{RESET}", T, bw))
    print(pad+T["primary"]+"├"+T["box_h"]*(bw-2)+"┤"+RESET)
    print(pad+draw_box_line(f"  {T['muted']}Date{RESET}    {T['text']}{now.strftime('%A, %B %d, %Y')}{RESET}", T, bw))
    print(pad+draw_box_line(f"  {T['muted']}Time{RESET}    {T['text']}{now.strftime('%I:%M %p')}{RESET}", T, bw))
    print(pad+T["primary"]+"├"+T["box_h"]*(bw-2)+"┤"+RESET)
    print(pad+draw_box_line(f"  {T['accent']}Weather in {city}{RESET}", T, bw))
    print(pad+draw_box_line(f"  {T['text']}{weather}{RESET}", T, bw))
    print(pad+T["primary"]+"├"+T["box_h"]*(bw-2)+"┤"+RESET)
    print(pad+draw_box_line(f"  {T['accent']}Top {category_name} News{RESET}", T, bw))
    print(pad+T["primary"]+T["box_v"]+" "*(bw-2)+T["box_v"]+RESET)
    if news:
        for i,item in enumerate(news[:3],1):
            print(pad+draw_box_line(f"  {T['warn']}{i}.{RESET} {T['text']}{item['title']}{RESET}", T, bw))
            chunk_size = bw-10
            for j in range(0,len(item['body']),chunk_size):
                chunk = item['body'][j:j+chunk_size].strip()
                if chunk: print(pad+draw_box_line(f"     {T['muted']}{chunk}{RESET}", T, bw))
            print(pad+draw_box_line(f"     {T['dark']}◦ {item['source']}{RESET}", T, bw))
            if i<3: print(pad+T["primary"]+T["box_v"]+T["muted"]+"╌"*(bw-2)+RESET+T["primary"]+T["box_v"]+RESET)
    else:
        print(pad+draw_box_line(f"  {T['muted']}News unavailable right now.{RESET}", T, bw))
    print(pad+T["primary"]+T["box_bl"]+T["box_h"]*(bw-2)+T["box_br"]+RESET)
    print()
    speak_wait(f"Today is {now.strftime('%A %B %d')}. Weather: {weather}.", voice)
    if news: speak(f"Top {category_name} news: {news[0]['title']}.", voice)

# ── To-Do ─────────────────────────────────────────────────────────────────────
def load_todos():
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE) as f: return json.load(f)
        except: return []
    return []

def save_todos(t):
    with open(TODO_FILE,"w") as f: json.dump(t,f,indent=2)

def show_todos(T):
    todos = load_todos()
    lines = []
    if not todos:
        lines.append(f"  {T['muted']}No tasks yet.  Type: todo add <task>{RESET}")
    else:
        for i,t in enumerate(todos,1):
            status = T["success"]+"✓"+RESET if t["done"] else T["muted"]+"◦"+RESET
            date   = T["muted"]+f" ({t.get('date','')})" +RESET if t.get("date") else ""
            col    = T["muted"] if t["done"] else T["text"]
            lines.append(f"  {status} {i}. {col}{t['task'][:40]}{RESET}{date}")
    total    = len(todos)
    done     = sum(1 for t in todos if t["done"])
    bar_done = int(done/total*20) if total>0 else 0
    bar      = T["success"]+"█"*bar_done+T["dark"]+"░"*(20-bar_done)+RESET
    lines.append(f"  {bar}  {T['success']}{done}{RESET} done  {T['muted']}◦{RESET}  {T['warn']}{total-done}{RESET} left")
    draw_box(lines, T, title="To-Do List")

def handle_todo(cmd, T, voice):
    parts  = cmd.strip().split(" ",2)
    action = parts[1].lower() if len(parts)>1 else "list"
    todos  = load_todos()
    if action=="list" or len(parts)==1:
        show_todos(T)
    elif action=="add" and len(parts)==3:
        todos.append({"task":parts[2],"done":False,"date":datetime.now().strftime("%b %d")})
        save_todos(todos)
        print(T["success"]+f"\n  ✓ Added: {parts[2]}\n"+RESET)
        speak(f"Task added: {parts[2]}", voice)
        show_todos(T)
    elif action in ("done","undone","delete") and len(parts)==3:
        try:
            idx = int(parts[2])-1
            if 0<=idx<len(todos):
                if action=="done":
                    todos[idx]["done"]=True; save_todos(todos)
                    print(T["success"]+f"\n  ✓ Done: {todos[idx]['task']}\n"+RESET)
                    speak(f"Marked done: {todos[idx]['task']}", voice)
                elif action=="undone":
                    todos[idx]["done"]=False; save_todos(todos)
                    print(T["warn"]+f"\n  ◦ Unmarked: {todos[idx]['task']}\n"+RESET)
                elif action=="delete":
                    removed=todos.pop(idx); save_todos(todos)
                    print(T["error"]+f"\n  ✕ Deleted: {removed['task']}\n"+RESET)
                show_todos(T)
            else: print(T["error"]+f"  No task #{parts[2]}."+RESET)
        except ValueError: print(T["error"]+f"  Use: todo {action} <number>"+RESET)
    elif action=="clear":
        if input(T["warn"]+"  Clear all? (y/n): "+RESET).strip().lower()=="y":
            save_todos([]); print(T["accent"]+"  All cleared."+RESET)
    else:
        print(f"\n  {T['warn']}todo{RESET}               {T['muted']}◦ show list{RESET}")
        print(f"  {T['warn']}todo add <task>{RESET}    {T['muted']}◦ add task{RESET}")
        print(f"  {T['warn']}todo done <n>{RESET}      {T['muted']}◦ mark done{RESET}")
        print(f"  {T['warn']}todo undone <n>{RESET}    {T['muted']}◦ unmark{RESET}")
        print(f"  {T['warn']}todo delete <n>{RESET}    {T['muted']}◦ delete{RESET}")
        print(f"  {T['warn']}todo clear{RESET}         {T['muted']}◦ clear all{RESET}\n")

# ── Git ───────────────────────────────────────────────────────────────────────
def git_helper(cmd, T, voice, persona_key):
    parts  = cmd.strip().split(" ",1)
    action = parts[1].lower() if len(parts)>1 else "help"
    if action=="status":
        r = subprocess.run("git status --short",shell=True,capture_output=True,text=True)
        print(); print(T["warn"]+"  ◦ Git Status"+RESET)
        print(T["muted"]+"  "+"─"*44+RESET)
        for line in (r.stdout.strip() or "Nothing to commit.").split("\n"):
            print(f"  {T['text']}{line}{RESET}")
        print()
    elif action=="log":
        r = subprocess.run("git log --oneline -5",shell=True,capture_output=True,text=True)
        print(); print(T["warn"]+"  ◦ Recent Commits"+RESET)
        print(T["muted"]+"  "+"─"*44+RESET)
        for line in (r.stdout.strip() or "No commits yet.").split("\n"):
            print(f"  {T['text']}{line}{RESET}")
        print()
    elif action=="commit":
        r = subprocess.run("git status --short",shell=True,capture_output=True,text=True)
        status = r.stdout.strip()
        if not status: print(T["accent"]+"  ◦ Nothing to commit."+RESET); return
        print(T["muted"]+"\n  ◦ Generating commit message...\n"+RESET)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":f"Write a short git commit message using conventional commits. Only output the message.\n\nGit status:\n{status}"}],
            max_tokens=60)
        msg = response.choices[0].message.content.strip().strip('"')
        print(T["primary"]+f"  {T['symbol']} Suggested: {T['text']}{msg}{RESET}")
        confirm = input(T["accent"]+"\n  ◦ Use this? (y/n/edit): "+RESET+T["text"]).strip().lower()
        print(RESET,end="")
        if confirm=="y":
            subprocess.run(f'git add -A && git commit -m "{msg}"',shell=True)
            print(T["success"]+"  ✓ Committed!"+RESET); speak(f"Committed: {msg}", voice)
        elif confirm=="edit":
            custom = input(T["accent"]+"  ◦ Your message: "+RESET+T["text"]).strip()
            print(RESET,end="")
            if custom:
                subprocess.run(f'git add -A && git commit -m "{custom}"',shell=True)
                print(T["success"]+"  ✓ Committed!"+RESET)
        else: print(T["muted"]+"  Cancelled."+RESET)
    elif action=="push":
        r = subprocess.run("git push",shell=True,capture_output=True,text=True)
        print(T["text"]+(r.stdout or r.stderr).strip()+RESET); speak("Push complete.", voice)
    elif action=="pull":
        r = subprocess.run("git pull",shell=True,capture_output=True,text=True)
        print(T["text"]+(r.stdout or r.stderr).strip()+RESET); speak("Pull complete.", voice)
    elif action.startswith("explain "):
        git_cmd = action[8:].strip()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":f"Explain 'git {git_cmd}' in 2 simple sentences. No markdown."}],
            max_tokens=100)
        explanation = response.choices[0].message.content.strip()
        print(); print(T["muted"]+"  "+"─"*50+RESET)
        print(f"  {T['text']}{explanation}{RESET}")
        print(T["muted"]+"  "+"─"*50+RESET); print()
        speak(explanation, voice)
    else:
        print(f"\n  {T['warn']}git status{RESET}          {T['muted']}◦ changed files{RESET}")
        print(f"  {T['warn']}git log{RESET}             {T['muted']}◦ recent commits{RESET}")
        print(f"  {T['warn']}git commit{RESET}          {T['muted']}◦ AI commit message{RESET}")
        print(f"  {T['warn']}git push / pull{RESET}     {T['muted']}◦ push or pull{RESET}")
        print(f"  {T['warn']}git explain <cmd>{RESET}   {T['muted']}◦ explain command{RESET}\n")

# ── Persona Menu ──────────────────────────────────────────────────────────────
def show_personas(current, T, user_name):
    keys  = list(PERSONAS.keys())
    lines = []
    for i,key in enumerate(keys,1):
        p      = PERSONAS[key]
        active = T["success"]+" ✓"+RESET if key==current else ""
        lines.append(f"  {T['warn']}{i}. {p['name']:<10}{RESET}{T['muted']}{p['desc']:<28}{RESET}{T['dark']}{p['voice']:<10}{RESET}{active}")
    draw_box(lines, T, title="Switch AI Persona")
    while True:
        choice = input(T["primary"]+f"  {T['symbol']} Pick 1-{len(keys)} or Enter to cancel: "+RESET+T["text"]).strip()
        print(RESET,end="")
        if choice=="": return current
        if choice.isdigit() and 1<=int(choice)<=len(keys):
            chosen = keys[int(choice)-1]; p = PERSONAS[chosen]
            print(T["primary"]+f"\n  {T['symbol']} Switched to {p['name']} — {p['desc']}"+RESET)
            print(T["muted"]+f"  ◦ Voice: {p['voice']}\n"+RESET)
            speak(f"Hi {user_name}! I am {p['name']}. {p['desc']}.", p["voice"])
            return chosen
        print(T["error"]+f"  Invalid. Enter 1-{len(keys)}."+RESET)

# ── Open URL ──────────────────────────────────────────────────────────────────
def open_url(url_or_name, T, voice):
    name = url_or_name.lower().strip().replace("https://","").replace("http://","").replace("www.","")
    for key,url in SITE_MAP.items():
        if key in name:
            print(T["success"]+f"\n  ◦ Opening {key.capitalize()}...\n"+RESET)
            webbrowser.open(url); return f"Opened {key.capitalize()}"
    url = url_or_name if url_or_name.startswith("http") else (f"https://{name}" if "." in name else f"https://www.google.com/search?q={name}")
    print(T["success"]+f"\n  ◦ Opening {url}...\n"+RESET)
    webbrowser.open(url); return f"Opened {url}"

# ── Sysinfo ───────────────────────────────────────────────────────────────────
def show_sysinfo(T):
    lines = []
    try:
        cpu  = subprocess.run("top -l 1 | grep 'CPU usage' | awk '{print $3}'",shell=True,capture_output=True,text=True).stdout.strip()
        mem  = subprocess.run("vm_stat | grep 'Pages active' | awk '{print $3}'",shell=True,capture_output=True,text=True).stdout.strip()
        mem_mb = int(mem.replace(".",""))*4096//1024//1024 if mem else 0
        disk = subprocess.run("df -h / | tail -1 | awk '{print $3\"/\"$2\" used (\"$5\")\"}'",shell=True,capture_output=True,text=True).stdout.strip()
        batt = subprocess.run("pmset -g batt | grep -o '[0-9]*%'",shell=True,capture_output=True,text=True).stdout.strip()
        chg  = subprocess.run("pmset -g batt | grep -o 'charging\\|discharging\\|charged'",shell=True,capture_output=True,text=True).stdout.strip()
        upt  = subprocess.run("uptime | awk -F',' '{print $1}' | awk -F'up' '{print $2}'",shell=True,capture_output=True,text=True).stdout.strip()
        lines = [
            f"  {T['muted']}CPU    {RESET}{T['text']}{cpu or 'N/A'}{RESET}",
            f"  {T['muted']}Memory {RESET}{T['text']}{mem_mb} MB active{RESET}",
            f"  {T['muted']}Disk   {RESET}{T['text']}{disk or 'N/A'}{RESET}",
            f"  {T['muted']}Battery{RESET}{T['text']}{batt or 'N/A'} {chg}{RESET}",
            f"  {T['muted']}Uptime {RESET}{T['text']}{upt or 'N/A'}{RESET}",
        ]
    except Exception as e:
        lines = [f"  {T['error']}Error: {e}{RESET}"]
    draw_box(lines, T, title="System Monitor")

# ── History ───────────────────────────────────────────────────────────────────
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f: return json.load(f)
        except: return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE,"w") as f: json.dump(history,f,indent=2)
    except: pass

def show_history(T):
    history = load_history()
    if not history: print(T["accent"]+"  ◦ No history yet."+RESET); return
    w = get_terminal_width()
    print(); print(T["muted"]+"  "+"─"*(w-4)+RESET)
    print(T["accent"]+f"  {T['symbol']} Last {min(10,len(history))} messages"+RESET)
    print(T["muted"]+"  "+"─"*(w-4)+RESET)
    for msg in history[-10:]:
        t=msg.get("time",""); role=msg.get("role",""); content=msg.get("content","")[:80]
        if role=="user": print(T["success"]+f"  {T['user_sym']} [{t}] You: "+T["text"]+f"{content}..."+RESET)
        else:            print(T["primary"]+f"  {T['symbol']} [{t}] AI:  "+T["muted"]+f"{content}..."+RESET)
    print(T["muted"]+"  "+"─"*(w-4)+RESET); print()

def clear_history():
    if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
    conversation_history.clear()
    print("\033[1;36m  ◦ Memory cleared.\033[0m")

# ── File Reader ───────────────────────────────────────────────────────────────
def handle_file_read(cmd, T, voice, persona_key):
    parts = cmd.strip().split(" ",1)
    if len(parts)<2: print(T["accent"]+"  Usage: read <filename>"+RESET); return
    filepath = os.path.expanduser(parts[1].strip())
    if not os.path.exists(filepath):
        local = os.path.join(os.getcwd(), parts[1].strip())
        if os.path.exists(local): filepath = local
        else: print(T["error"]+f"  ✕ File not found: {parts[1]}"+RESET); return
    size = os.path.getsize(filepath)
    w    = get_terminal_width()
    print(); print(T["muted"]+"  "+"─"*(w-4)+RESET)
    print(T["primary"]+f"  {T['symbol']} Reading: {T['text']}{os.path.basename(filepath)}{RESET}  {T['muted']}◦  {size} bytes{RESET}")
    print(T["muted"]+"  "+"─"*(w-4)+RESET); print()
    try:
        with open(filepath,"r",encoding="utf-8",errors="ignore") as f:
            lines = f.readlines()
        total_lines = len(lines)
        print(T["warn"]+f"  ◦ Preview — first {min(20,total_lines)} lines"+RESET)
        print(T["muted"]+"  "+"─"*40+RESET)
        for i,line in enumerate(lines[:20],1):
            print(T["muted"]+f"  {i:3} "+RESET+T["text"]+line.rstrip()+RESET)
        if total_lines>20: print(T["muted"]+f"  ... {total_lines-20} more lines"+RESET)
        print()
        stop_event = threading.Event()
        anim = threading.Thread(target=thinking_animation, args=(stop_event,T))
        anim.daemon=True; anim.start()
        file_content = "".join(lines[:200])
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role":"system","content":PERSONAS[persona_key]["prompt"]},
                    {"role":"user","content":f"Analyze this file:\n1. What it does\n2. Key functions\n3. Issues\n\nFile: {os.path.basename(filepath)}\n\n{file_content}"}
                ],
                max_tokens=1024)
        finally:
            stop_event.set(); anim.join()
        reply = response.choices[0].message.content
        print_reply(reply, T)
        speak("Analysis complete.", voice)
    except Exception as e:
        print(T["error"]+f"  ✕ Error: {e}"+RESET)

# ── Web Search ────────────────────────────────────────────────────────────────
def web_search(query, T):
    print(T["muted"]+f"  ◦ Searching: {query}"+RESET)
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))
        if not results: return "No results found."
        return "".join(f"- {r['title']}\n  {r['body']}\n  Source: {r['href']}\n\n" for r in results)
    except Exception as e: return f"Search failed: {e}"

def should_search(user_input):
    keywords = ["search","look up","latest","news","today","current","price of","weather",
                "2024","2025","2026","what is","who is","when is","how much"]
    return any(k in user_input.lower() for k in keywords)

def run_command(cmd, T):
    if any(d in cmd for d in DANGEROUS):
        return T["error"]+"  ✕ Blocked: too dangerous."+RESET
    print(T["muted"]+f"  ◦ Running: {cmd}"+RESET)
    try:
        result = subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=15)
        return T["warn"]+(result.stdout or result.stderr or "(no output)").strip()+RESET
    except subprocess.TimeoutExpired: return T["error"]+"  ✕ Timed out."+RESET
    except Exception as e: return T["error"]+f"  ✕ Error: {e}"+RESET

def extract_command(reply, prefix):
    for line in reply.splitlines():
        s = line.strip()
        if s.startswith(prefix+":"):
            v = s[len(prefix)+1:].strip()
            if v: return v
    return None

# ── Chat (FIXED: collect full reply then print wrapped) ───────────────────────
def do_chat(user_input, persona_key, T, voice):
    stop_event = threading.Event()
    start_time = time.time()

    anim = threading.Thread(target=thinking_animation, args=(stop_event,T))
    anim.daemon=True; anim.start()

    reply = ""
    try:
        extra = ""
        if should_search(user_input):
            results = web_search(user_input, T)
            extra   = f"\n\nWeb search results:\n{results}\n\nUse these to answer."

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conversation_history.append({"role":"user","content":user_input+extra})
        saved = load_history()
        saved.append({"role":"user","content":user_input,"time":now})

        # collect full reply (no streaming — fixes wrapping)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":PERSONAS[persona_key]["prompt"]}]+conversation_history,
            max_tokens=1024
        )
        reply = response.choices[0].message.content

        stop_event.set(); anim.join()
        print("\r"+" "*35+"\r", end="", flush=True)

        conversation_history.append({"role":"assistant","content":reply})
        saved.append({"role":"assistant","content":reply,"time":now})
        save_history(saved)

        # print with proper wrap
        print_reply(reply, T)
        speak(reply, voice)

    except Exception as e:
        stop_event.set(); anim.join()
        print("\r"+" "*35+"\r", end="", flush=True)
        print(T["error"]+f"  ✕ Error: {e}"+RESET)

    return reply, start_time

# ── Voice Input ───────────────────────────────────────────────────────────────
def listen(T, voice):
    print(T["accent"]+"  ◦ Listening for 6 seconds... speak now!"+RESET)
    try:
        sample_rate = 16000
        recording   = sd.rec(int(6*sample_rate),samplerate=sample_rate,channels=1,dtype="int16")
        sd.wait()
    except Exception as e:
        print(T["error"]+f"  ✕ Mic error: {e}"+RESET); return ""
    print(T["muted"]+"  ◦ Transcribing..."+RESET)
    with tempfile.NamedTemporaryFile(suffix=".wav",delete=False) as f:
        tmp_path = f.name
        wav.write(tmp_path, sample_rate, recording)
    try:
        with open(tmp_path,"rb") as af:
            t = client.audio.transcriptions.create(model="whisper-large-v3",file=af)
        os.unlink(tmp_path)
        return t.text.strip()
    except Exception as e:
        print(T["error"]+f"  ✕ Transcription error: {e}"+RESET)
        if os.path.exists(tmp_path): os.unlink(tmp_path)
        return ""

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global conversation_history

    user_name       = get_user_name()
    current_persona = load_persona()
    current_theme   = get_theme_name()
    city            = get_city()
    saved           = load_history()

    T = THEMES[current_theme]

    if saved:
        conversation_history = [{"role":m["role"],"content":m["content"]} for m in saved[-20:]]
        splash_screen(T,returning=True,msg_count=len(conversation_history),
                      current_persona=current_persona,user_name=user_name)
    else:
        splash_screen(T,returning=False,current_persona=current_persona,user_name=user_name)

    p = PERSONAS[current_persona]
    morning_briefing(T, p["voice"], user_name, city)

    while True:
        try:
            p     = PERSONAS[current_persona]
            voice = p["voice"]
            T     = THEMES[current_theme]
            w     = get_terminal_width()

            user_input = input(T["accent"]+f"  {T['user_sym']} "+RESET+T["text"]).strip()
            print(RESET, end="")

            if not user_input: continue

            stop_speaking()

            if user_input.lower() in ["exit","quit","bye"]:
                farewell_screen(T, user_name, voice); break

            if user_input.lower()=="history":
                show_history(T); continue

            if user_input.lower()=="clear memory":
                clear_history(); continue

            if user_input.lower()=="briefing":
                morning_briefing(T, voice, user_name, city); continue

            if user_input.lower().startswith("city "):
                new_city = user_input[5:].strip()
                set_city(new_city, T, voice); city=new_city; continue

            if user_input.lower()=="sysinfo":
                show_sysinfo(T); continue

            if user_input.lower().startswith("todo"):
                handle_todo(user_input, T, voice); continue

            if user_input.lower().startswith("git "):
                git_helper(user_input, T, voice, current_persona); continue

            if user_input.lower()=="persona":
                current_persona = show_personas(current_persona, T, user_name)
                save_persona(current_persona); continue

            if user_input.lower().startswith("persona "):
                new_p = user_input[8:].strip().lower()
                if new_p in PERSONAS:
                    current_persona=new_p; save_persona(current_persona)
                    p2=PERSONAS[current_persona]
                    print(T["primary"]+f"\n  {T['symbol']} Switched to {p2['name']}"+RESET)
                    speak(f"Hi {user_name}! I am {p2['name']}.",p2["voice"])
                else:
                    print(T["error"]+f"  Unknown persona. Try: {', '.join(PERSONAS.keys())}"+RESET)
                continue

            # Theme switching
            if user_input.lower()=="theme":
                show_themes(current_theme, T); continue

            if user_input.lower().startswith("theme "):
                new_t = user_input[6:].strip().lower()
                if new_t in THEMES:
                    current_theme = new_t; save_theme(current_theme)
                    T = THEMES[current_theme]
                    print(T["primary"]+f"\n  {T['symbol']} Theme switched to {T['name']}!\n"+RESET)
                    speak(f"Theme changed to {T['name']}.", voice)
                else:
                    print(T["error"]+f"  Unknown theme. Try: {', '.join(THEMES.keys())}"+RESET)
                continue

            if user_input.lower().startswith("open "):
                result = open_url(user_input[5:].strip(), T, voice)
                speak(result, voice); continue

            if user_input.lower().startswith("read "):
                handle_file_read(user_input, T, voice, current_persona); continue

            if user_input.lower()=="v":
                spoken = listen(T, voice)
                if not spoken:
                    print(T["muted"]+"  ◦ Nothing heard."+RESET); continue
                print(T["success"]+f"  {T['user_sym']} You (voice): {T['text']}{spoken}{RESET}")
                user_input = spoken

            if user_input.lower().startswith("search:"):
                query   = user_input[7:].strip()
                results = web_search(query, T)
                conversation_history.append({"role":"user","content":f"Summarize:\n{results}"})
                stop_event = threading.Event()
                anim = threading.Thread(target=thinking_animation,args=(stop_event,T))
                anim.daemon=True; anim.start()
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"system","content":p["prompt"]}]+conversation_history,
                    max_tokens=1024)
                stop_event.set(); anim.join()
                print("\r"+" "*35+"\r", end="", flush=True)
                reply = response.choices[0].message.content
                conversation_history.append({"role":"assistant","content":reply})
                print(); print(T["muted"]+"  "+"─"*(w-4)+RESET)
                print(T["primary"]+f"  {T['symbol']} {p['name']}:"+RESET)
                print(T["muted"]+"  "+"─"*(w-4)+RESET)
                print_reply(reply, T)
                status_bar(time.time(), reply, p["name"], T)
                speak(reply, voice); continue

            print(); print(T["muted"]+"  "+"─"*(w-4)+RESET)
            print(T["primary"]+f"  {T['symbol']} {p['name']}:"+RESET)
            print(T["muted"]+"  "+"─"*(w-4)+RESET)

            reply, start_time = do_chat(user_input, current_persona, T, voice)

            open_line = extract_command(reply, "OPEN_URL")
            run_line  = extract_command(reply, "RUN_CMD")

            if open_line:
                stop_speaking()
                result = open_url(open_line, T, voice)
                print(T["success"]+f"  ◦ {result}"+RESET); speak(result, voice)
            elif run_line:
                stop_speaking()
                confirm = input(T["warn"]+f"\n  ◦ Run this? '{run_line}' (y/n): "+RESET+T["text"]).strip()
                print(RESET,end="")
                if confirm=="y":
                    print(run_command(run_line, T)); speak("Done.", voice)
                else:
                    print(T["muted"]+"  Cancelled."+RESET)
            else:
                status_bar(start_time, reply, p["name"], T)

        except KeyboardInterrupt:
            stop_speaking()
            farewell_screen(T, user_name, voice)
            sys.exit(0)

if __name__=="__main__":
    main()
