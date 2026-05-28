#!/usr/bin/env python3
"""
Dev AI - Termux Android Edition v6.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
New in v6.0:
  ✦ Email Drafter        (email)
  ✦ LinkedIn Post Writer (linkedin)
  ✦ Documentation Gen    (docgen)
  ✦ Secure Notes         (secu note)

Previous v5.0 features:
  ✦ Calculator           (calc <expr>)
  ✦ File Manager         (fm / files)
  ✦ Unit Converter       (convert <val> <from> <to>)
  ✦ Password Generator   (passgen <length>)
  ✦ Base64 encode/decode (b64 enc/dec <text>)
  ✦ IP / Network info    (myip / netinfo)
  ✦ Pomodoro timer       (pomodoro)
  ✦ Note-taking          (note / notes)
  ✦ Clipboard copy       (copy <text>)
  ✦ To-Do list           (todo)
  ✦ Git helper           (git)
  ✦ Web search           (search: x)
  ✦ Daily briefing       (briefing)
  ✦ System info          (sysinfo)

Themes: ocean hacker amber frost nord rose dracula
Switch : theme <name>

Install deps in Termux:
  pip install groq requests
  pkg install termux-api   (optional)
"""

import os, sys, json, subprocess, time, random, threading
import re, textwrap, math, base64, string, secrets, hashlib
import requests
from groq import Groq
from datetime import datetime, timedelta

# ── API Key ───────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    print("\033[1;31m\n  ✕ GROQ_API_KEY not set!\033[0m")
    print("\033[1;33m  export GROQ_API_KEY='your_key_here'\033[0m")
    print("\033[1;33m  Add to ~/.bashrc to make permanent.\033[0m\n")
    sys.exit(1)

client = Groq(api_key=GROQ_API_KEY)

HISTORY_FILE    = os.path.expanduser("~/.dev_history.json")
PERSONA_FILE    = os.path.expanduser("~/.dev_persona.json")
TODO_FILE       = os.path.expanduser("~/.dev_todos.json")
NOTES_FILE      = os.path.expanduser("~/.dev_notes.json")
CONFIG_FILE     = os.path.expanduser("~/.dev_config.json")
SECURE_NOTES_FILE = os.path.expanduser("~/.dev_secure_notes.json")

RESET = "\033[0m"
BOLD  = "\033[1m"
DIM   = "\033[2m"

VERSION = "6.0"
MODEL   = "llama-3.3-70b-versatile"

# ── Themes ────────────────────────────────────────────────────────────────────
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
        "code":    "\033[38;2;255;218;121m",
        "symbol":  "◈", "user_sym": "~",
        "sep": "━",
        "box_tl":"╭","box_tr":"╮","box_bl":"╰","box_br":"╯",
        "box_h":"─","box_v":"│","bar":"▎",
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
        "code":    "\033[38;2;200;255;180m",
        "symbol":  "▶", "user_sym": "$",
        "sep": "▓",
        "box_tl":"┌","box_tr":"┐","box_bl":"└","box_br":"┘",
        "box_h":"─","box_v":"│","bar":"▎",
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
        "code":    "\033[38;2;255;240;160m",
        "symbol":  "◆", "user_sym": "❯",
        "sep": "═",
        "box_tl":"╔","box_tr":"╗","box_bl":"╚","box_br":"╝",
        "box_h":"═","box_v":"║","bar":"▎",
    },
    "frost": {
        "name":    "Frost",
        "primary": "\033[38;2;59;130;246m",
        "accent":  "\033[38;2;51;112;212m",
        "text":    "\033[38;2;220;230;255m",
        "muted":   "\033[38;2;100;116;139m",
        "dark":    "\033[38;2;203;213;225m",
        "success": "\033[38;2;34;197;94m",
        "warn":    "\033[38;2;234;179;8m",
        "error":   "\033[38;2;239;68;68m",
        "special": "\033[38;2;139;92;246m",
        "code":    "\033[38;2;180;230;255m",
        "symbol":  "›", "user_sym": "›",
        "sep": "─",
        "box_tl":"┌","box_tr":"┐","box_bl":"└","box_br":"┘",
        "box_h":"─","box_v":"│","bar":"│",
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
        "code":    "\033[38;2;235;203;139m",
        "symbol":  "❄", "user_sym": "›",
        "sep": "─",
        "box_tl":"╭","box_tr":"╮","box_bl":"╰","box_br":"╯",
        "box_h":"─","box_v":"│","bar":"▎",
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
        "code":    "\033[38;2;255;200;220m",
        "symbol":  "✦", "user_sym": "›",
        "sep": "━",
        "box_tl":"╭","box_tr":"╮","box_bl":"╰","box_br":"╯",
        "box_h":"─","box_v":"│","bar":"▎",
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
        "code":    "\033[38;2;255;184;108m",
        "symbol":  "⚡", "user_sym": "›",
        "sep": "─",
        "box_tl":"╭","box_tr":"╮","box_bl":"╰","box_br":"╯",
        "box_h":"─","box_v":"│","bar":"▎",
    },
}

DANGEROUS = ["rm -rf /","rmdir /","mkfs","dd if=/dev/zero",
             "shutdown","reboot","chmod 777 /","sudo rm -rf"]

WRAP = 58
conversation_history = []

# ── Personas ──────────────────────────────────────────────────────────────────
PERSONAS = {
    "dev":    {"name":"Dev",    "desc":"Professional coder & problem solver",
               "prompt":"You are Dev, a professional AI in Termux terminal. Be concise and practical. Use code blocks for code. OPEN_URL: url — RUN_CMD: command (safe only)."},
    "mentor": {"name":"Mentor", "desc":"Patient teacher, explains everything",
               "prompt":"You are Mentor, a patient encouraging teacher. Explain with examples. OPEN_URL: url — RUN_CMD: command"},
    "buddy":  {"name":"Buddy",  "desc":"Friendly casual coding friend",
               "prompt":"You are Buddy, a fun friendly coding companion. Be casual. OPEN_URL: url — RUN_CMD: command"},
    "sage":   {"name":"Sage",   "desc":"Deep thinker, architecture & design",
               "prompt":"You are Sage, a wise software architect. Think deeply. OPEN_URL: url — RUN_CMD: command"},
    "turbo":  {"name":"Turbo",  "desc":"Ultra fast — shortest correct answer",
               "prompt":"You are Turbo. Give the shortest correct answer only. OPEN_URL: url — RUN_CMD: command"},
}

SITE_MAP = {
    "github":"https://github.com","youtube":"https://youtube.com",
    "google":"https://google.com","twitter":"https://twitter.com",
    "x":"https://x.com","linkedin":"https://linkedin.com",
    "stackoverflow":"https://stackoverflow.com","reddit":"https://reddit.com",
    "gmail":"https://mail.google.com","drive":"https://drive.google.com",
    "notion":"https://notion.so","vercel":"https://vercel.com",
    "netlify":"https://netlify.com","replit":"https://replit.com",
    "claude":"https://claude.ai","chatgpt":"https://chatgpt.com",
    "instagram":"https://instagram.com","whatsapp":"https://web.whatsapp.com",
    "pypi":"https://pypi.org","npm":"https://npmjs.com",
}

NEWS_CATEGORIES = {
    "1":("Technology","latest technology AI news today"),
    "2":("Finance",   "finance stock market news today"),
    "3":("Economy",   "economy economic news today"),
    "4":("World",     "world news today top stories"),
    "5":("India",     "India news today top stories"),
    "6":("Sports",    "sports cricket IPL news today India"),
}

UNITS = {
    "m":"m","metre":"m","metres":"m","meter":"m","meters":"m",
    "km":"km","kilometre":"km","kilometers":"km",
    "cm":"cm","centimetre":"cm","centimeters":"cm",
    "mm":"mm","millimetre":"mm","millimeters":"mm",
    "mi":"mi","mile":"mi","miles":"mi",
    "ft":"ft","foot":"ft","feet":"ft",
    "in":"in","inch":"in","inches":"in",
    "kg":"kg","kilogram":"kg","kilograms":"kg",
    "g":"g","gram":"g","grams":"g",
    "lb":"lb","pound":"lb","pounds":"lb",
    "oz":"oz","ounce":"oz","ounces":"oz",
    "c":"°C","celsius":"°C","°c":"°C",
    "f":"°F","fahrenheit":"°F","°f":"°F",
    "k":"K","kelvin":"K",
    "b":"B","byte":"B","bytes":"B",
    "kb":"KB","kilobyte":"KB","kilobytes":"KB",
    "mb":"MB","megabyte":"MB","megabytes":"MB",
    "gb":"GB","gigabyte":"GB","gigabytes":"GB",
    "tb":"TB","terabyte":"TB","terabytes":"TB",
}

LENGTH_TO_M  = {"m":1,"km":1000,"cm":0.01,"mm":0.001,"mi":1609.344,"ft":0.3048,"in":0.0254}
WEIGHT_TO_KG = {"kg":1,"g":0.001,"lb":0.453592,"oz":0.0283495}
DATA_TO_B    = {"B":1,"KB":1024,"MB":1024**2,"GB":1024**3,"TB":1024**4}

# ── Helpers ───────────────────────────────────────────────────────────────────
def strip_ansi(t):
    return re.sub(r'\033\[[0-9;]*m|\033\[38;2;[0-9;]*m','',t)

def get_terminal_width():
    try:    return os.get_terminal_size().columns
    except: return 70

def clear_screen(): os.system("clear")

def divider(T, w=None):
    if w is None: w = get_terminal_width()
    print(T["muted"] + "  " + T["sep"] * max(0, w-4) + RESET)

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
    clear_screen()
    print()
    print("\033[1;36m  Welcome to Dev AI for Termux!\033[0m")
    print("\033[0;37m  Android Edition v" + VERSION + "\033[0m\n")
    while True:
        name = input("\033[1;36m  Your name: \033[0m").strip()
        if name:
            cfg["name"] = name; save_config(cfg); return name
        print("  Please enter a name.")

def get_city():
    cfg = load_config()
    if cfg.get("city"): return cfg["city"]
    try:
        r    = requests.get("https://ipapi.co/city/", timeout=5)
        city = r.text.strip()
        if city and len(city) < 50:
            cfg["city"] = city; save_config(cfg); return city
    except: pass
    return "Chennai"

def get_theme_name():
    return load_config().get("theme","ocean")

def save_theme(name):
    cfg = load_config(); cfg["theme"] = name; save_config(cfg)

def set_city(new_city, T):
    cfg = load_config(); cfg["city"] = new_city; save_config(cfg)
    print(T["success"] + f"\n  ◦ City → {new_city}\n" + RESET)

def load_persona():
    if os.path.exists(PERSONA_FILE):
        try:
            with open(PERSONA_FILE) as f: return json.load(f).get("persona","dev")
        except: return "dev"
    return "dev"

def save_persona(n):
    with open(PERSONA_FILE,"w") as f: json.dump({"persona":n},f)

def get_greeting(user_name):
    h  = datetime.now().hour
    tg = ("Good morning" if 5<=h<12 else
          "Good afternoon" if 12<=h<17 else
          "Good evening"   if 17<=h<21 else "Good night")
    return random.choice([
        f"{tg}, {user_name}! Ready to build something?",
        f"Hey {user_name}! Great to see you.",
        f"Welcome back, {user_name}! What are we creating?",
        f"{tg}, {user_name}! Here and ready.",
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
    n = datetime.now()
    return f"{n.strftime('%a %b %d %Y')}  ◦  {n.strftime('%I:%M %p')}"

# ── Box drawing ───────────────────────────────────────────────────────────────
def box_line(content, T, bw):
    raw   = strip_ansi(content)
    max_c = bw - 4
    if len(raw) > max_c:
        content = content[:max_c-3] + T["muted"] + "..." + RESET
    raw = strip_ansi(content)
    sp  = bw - 2 - len(raw)
    return (T["primary"] + T["box_v"] + RESET +
            content + " " * max(0,sp) +
            T["primary"] + T["box_v"] + RESET)

def draw_box(lines, T, title=None, w=None):
    if w is None: w = get_terminal_width()
    bw  = min(w-2, 60)
    pad = " " * max(0,(w-bw)//2)
    print()
    print(pad + T["primary"] + T["box_tl"] + T["box_h"]*(bw-2) + T["box_tr"] + RESET)
    if title:
        print(pad + box_line(f"  {T['accent']}{BOLD}{title}{RESET}", T, bw))
        print(pad + T["primary"] + "├" + T["box_h"]*(bw-2) + "┤" + RESET)
    for line in lines:
        print(pad + box_line(line, T, bw))
    print(pad + T["primary"] + T["box_bl"] + T["box_h"]*(bw-2) + T["box_br"] + RESET)
    print()

# ── Reply printer ─────────────────────────────────────────────────────────────
def print_reply(text, T):
    bar     = T["primary"] + "  " + T["bar"] + RESET
    tw      = min(WRAP, get_terminal_width() - 6)
    in_code = False
    lang    = ""
    print()
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            lang    = stripped[3:].strip() if in_code else ""
            fence   = f"  {'─'*min(tw,40)}"
            if in_code:
                print(bar + T["muted"] + fence + RESET)
                if lang:
                    print(bar + T["muted"] + f"  {lang}" + RESET)
            else:
                print(bar + T["muted"] + fence + RESET)
            continue
        if in_code:
            print(bar + T["code"] + " " + line + RESET)
            continue
        if stripped.startswith("## "):
            print(bar + BOLD + T["accent"] + " " + stripped[3:] + RESET)
            continue
        if stripped.startswith("# "):
            print(bar + BOLD + T["primary"] + " " + stripped[2:] + RESET)
            continue
        if stripped.startswith(("- ","• ","* ")):
            content = stripped[2:]
            wrapped = textwrap.wrap(content, width=tw-4) or [""]
            print(bar + T["accent"] + "  • " + T["text"] + wrapped[0] + RESET)
            for wl in wrapped[1:]:
                print(bar + T["text"] + "    " + wl + RESET)
            continue
        m = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if m:
            content = m.group(2)
            wrapped = textwrap.wrap(content, width=tw-4) or [""]
            print(bar + T["warn"] + f"  {m.group(1)}. " + T["text"] + wrapped[0] + RESET)
            for wl in wrapped[1:]:
                print(bar + T["text"] + "     " + wl + RESET)
            continue
        wrapped = textwrap.wrap(line, width=tw) if line.strip() else [""]
        if not wrapped: wrapped = [""]
        for wl in wrapped:
            print(bar + T["text"] + " " + wl + RESET)
    print()

# ── Thinking animation ────────────────────────────────────────────────────────
def thinking_animation(stop_event, T):
    frames = [
        T["primary"] + f"  {T['symbol']} " + T["muted"] + "thinking    " + RESET,
        T["primary"] + f"  {T['symbol']} " + T["muted"] + "thinking ◦  " + RESET,
        T["primary"] + f"  {T['symbol']} " + T["muted"] + "thinking ◦◦ " + RESET,
        T["primary"] + f"  {T['symbol']} " + T["muted"] + "thinking ◦◦◦" + RESET,
    ]
    i = 0
    while not stop_event.is_set():
        print(f"\r{frames[i%len(frames)]}", end="", flush=True)
        time.sleep(0.2); i += 1
    print("\r"+" "*36+"\r", end="", flush=True)

def status_bar(start_time, reply, persona_name, T):
    elapsed = int((time.time()-start_time)*1000)
    words   = len(reply.split())
    now     = datetime.now().strftime("%I:%M %p")
    w       = get_terminal_width()
    divider(T, w)
    print(f"  {T['primary']}{T['symbol']} {persona_name}{RESET}  "
          f"{T['muted']}◦  {elapsed}ms  ◦  {words}w  ◦  {MODEL}  ◦  {now}{RESET}")
    divider(T, w)
    print()

# ── Splash ────────────────────────────────────────────────────────────────────
def splash_screen(T, returning=False, msg_count=0, current_persona="dev", user_name="Friend"):
    clear_screen()
    w = get_terminal_width()
    p = PERSONAS[current_persona]

    logo = [
        "  ██████╗ ███████╗██╗   ██╗",
        "  ██╔══██╗██╔════╝██║   ██║",
        "  ██║  ██║█████╗  ██║   ██║",
        "  ██║  ██║██╔══╝  ╚██╗ ██╔╝",
        "  ██████╔╝███████╗ ╚████╔╝ ",
        "  ╚═════╝ ╚══════╝  ╚═══╝  ",
    ]
    print()
    divider(T, w)
    print()
    for line in logo: print(T["primary"] + line + RESET)
    print()
    print(T["muted"] + f"  Android Edition v{VERSION}  ◦  Termux" + RESET)
    print(T["muted"] + f"  Groq  ◦  {MODEL}" + RESET)
    print(T["accent"] + f"  {T['name']}" + RESET)
    print()
    divider(T, w)
    print(T["muted"] + f"  {get_datetime_line()}" + RESET)
    print(T["primary"] + f"  {T['symbol']} {p['name']}  ◦  {p['desc']}" + RESET)
    divider(T, w)
    print()

    greeting = get_greeting(user_name)
    print(T["accent"] + f"  {greeting}" + RESET)
    if returning:
        print(T["muted"] + f"  ◦ {msg_count} messages remembered." + RESET)
    print()
    divider(T, w)
    print()

    sections = [
        ("AI & Search",  [
            ("search: x",      "web search"),
            ("persona",        "switch AI persona"),
            ("history",        "past chats"),
            ("clear memory",   "forget all"),
        ]),
        ("✦ New v6.0",   [
            ("email",          "AI email drafter"),
            ("linkedin",       "LinkedIn post writer"),
            ("docgen",         "documentation generator"),
            ("secu note",      "encrypted secure notes"),
        ]),
        ("Tools",        [
            ("calc <expr>",    "calculator"),
            ("convert",        "unit converter"),
            ("passgen <n>",    "password generator"),
            ("b64 enc/dec",    "base64 encode/decode"),
            ("myip",           "show IP address"),
            ("netinfo",        "network info"),
            ("pomodoro",       "focus timer"),
        ]),
        ("Files",        [
            ("fm / files",     "file manager"),
            ("open <site>",    "open website"),
            ("read <file>",    "read & explain file"),
            ("copy <text>",    "copy to clipboard"),
        ]),
        ("Productivity", [
            ("todo",           "to-do list"),
            ("note",           "quick notes"),
            ("git <cmd>",      "git helper"),
            ("briefing",       "daily briefing"),
            ("sysinfo",        "system info"),
        ]),
        ("Settings",     [
            ("theme <name>",   "switch theme"),
            ("city <name>",    "change city"),
            ("exit",           "quit"),
        ]),
    ]
    for section_name, cmds in sections:
        if section_name.startswith("✦"):
            print(T["success"] + f"  {section_name}" + RESET)
        else:
            print(T["special"] + f"  {section_name}" + RESET)
        for cmd, desc in cmds:
            print(f"  {T['warn']}{T['user_sym']} {cmd:<20}{RESET}{T['muted']}{desc}{RESET}")
        print()

    divider(T, w)
    print(T["accent"] + "  ready!" + RESET + "  " +
          T["muted"] + f"theme: {T['name']}" + RESET)
    print()

def farewell_screen(T, user_name):
    msg = get_farewell(user_name)
    w   = get_terminal_width()
    print(); divider(T, w)
    print(T["accent"] + f"  {msg}" + RESET)
    divider(T, w); print()

# ── Theme menu ────────────────────────────────────────────────────────────────
def show_themes(current_theme, T):
    lines = []
    for key, th in THEMES.items():
        active = T["success"]+" ✓"+RESET if key==current_theme else ""
        lines.append(f"  {T['warn']}{key:<12}{RESET}{T['text']}{th['name']}{RESET}{active}")
    draw_box(lines, T, title=f"Switch Theme  (current: {T['name']})")
    print(f"  {T['muted']}Type: theme <name>{RESET}\n")

# ── Weather & News ────────────────────────────────────────────────────────────
def get_weather(city):
    try:
        r = requests.get(f"https://wttr.in/{city}?format=%C+%t+Humidity:%h+Wind:%w",timeout=6)
        return r.text.strip()
    except: return "Weather unavailable"

def get_top_news(query="top news India today"):
    try:
        url = f"https://news.google.com/rss/search?q={query.replace(' ','+')}&hl=en-IN&gl=IN&ceid=IN:en"
        r   = requests.get(url, timeout=8)
        items = re.findall(r'<title>(.*?)</title>', r.text)[1:5]
        return [{"title": re.sub('<.*?>','',t)[:60], "body":"", "source":"Google News"} for t in items]
    except: return []

def pick_news_category(T):
    lines = [f"  {T['warn']}{k}.{RESET}  {T['text']}{n}{RESET}"
             for k,(n,_) in NEWS_CATEGORIES.items()]
    draw_box(lines, T, title="News Category")
    choice = input(T["primary"]+f"  {T['symbol']} Pick 1-6 (Enter=India): "+RESET+T["text"]).strip()
    print(RESET,end="")
    if choice in NEWS_CATEGORIES:
        name,query = NEWS_CATEGORIES[choice]; return name,query
    return "India","India top news today"

def morning_briefing(T, user_name, city):
    w   = get_terminal_width()
    bw  = min(w-2, 60)
    pad = " "*max(0,(w-bw)//2)
    now = datetime.now()
    category_name, news_query = pick_news_category(T)
    weather = get_weather(city)
    news    = get_top_news(news_query)
    print()
    print(pad+T["primary"]+T["box_tl"]+T["box_h"]*(bw-2)+T["box_tr"]+RESET)
    print(pad+box_line(f"  {T['accent']}{BOLD}Daily Briefing  {RESET}{T['muted']}◦  {T['text']}{user_name}",T,bw))
    print(pad+T["primary"]+"├"+T["box_h"]*(bw-2)+"┤"+RESET)
    print(pad+box_line(f"  {T['muted']}Date{RESET}  {T['text']}{now.strftime('%A, %B %d, %Y')}{RESET}",T,bw))
    print(pad+box_line(f"  {T['muted']}Time{RESET}  {T['text']}{now.strftime('%I:%M %p')}{RESET}",T,bw))
    print(pad+T["primary"]+"├"+T["box_h"]*(bw-2)+"┤"+RESET)
    print(pad+box_line(f"  {T['accent']}Weather — {city}{RESET}",T,bw))
    print(pad+box_line(f"  {T['text']}{weather}{RESET}",T,bw))
    print(pad+T["primary"]+"├"+T["box_h"]*(bw-2)+"┤"+RESET)
    print(pad+box_line(f"  {T['accent']}Top {category_name} News{RESET}",T,bw))
    print(pad+T["primary"]+T["box_v"]+" "*(bw-2)+T["box_v"]+RESET)
    if news:
        for i,item in enumerate(news[:4],1):
            print(pad+box_line(f"  {T['warn']}{i}.{RESET} {T['text']}{item['title']}{RESET}",T,bw))
    else:
        print(pad+box_line(f"  {T['muted']}News unavailable.{RESET}",T,bw))
    print(pad+T["primary"]+T["box_bl"]+T["box_h"]*(bw-2)+T["box_br"]+RESET)
    print()

# ── Calculator ────────────────────────────────────────────────────────────────
def handle_calc(cmd, T):
    expr = cmd[4:].strip()
    if not expr:
        print(f"\n  {T['muted']}Usage: calc <expression>{RESET}\n")
        return
    safe_globals = {k:getattr(math,k) for k in dir(math) if not k.startswith("_")}
    safe_globals.update({"__builtins__":{},"abs":abs,"round":round,"pow":pow,"int":int,"float":float})
    try:
        result = eval(expr, safe_globals)
        draw_box([
            f"  {T['muted']}expr{RESET}   {T['text']}{expr}{RESET}",
            f"  {T['muted']}result{RESET} {T['success']}{BOLD}{result}{RESET}",
        ], T, title="Calculator")
    except ZeroDivisionError:
        print(T["error"]+"  ✕ Division by zero\n"+RESET)
    except Exception as e:
        print(T["error"]+f"  ✕ Error: {e}\n"+RESET)

# ── Unit Converter ────────────────────────────────────────────────────────────
def handle_convert(cmd, T):
    parts = cmd.strip().split()
    if len(parts) < 4:
        print(f"\n  {T['muted']}Usage: convert <value> <from> <to>{RESET}\n")
        return
    try:
        val  = float(parts[1])
        fr   = UNITS.get(parts[2].lower())
        to   = UNITS.get(parts[3].lower())
        if not fr or not to:
            print(T["error"]+f"  ✕ Unknown unit.\n"+RESET); return
        temps = {"°C","°F","K"}
        if fr in temps or to in temps:
            result = _convert_temp(val, fr, to)
        elif fr in LENGTH_TO_M and to in LENGTH_TO_M:
            result = val * LENGTH_TO_M[fr] / LENGTH_TO_M[to]
        elif fr in WEIGHT_TO_KG and to in WEIGHT_TO_KG:
            result = val * WEIGHT_TO_KG[fr] / WEIGHT_TO_KG[to]
        elif fr in DATA_TO_B and to in DATA_TO_B:
            result = val * DATA_TO_B[fr] / DATA_TO_B[to]
        else:
            print(T["error"]+"  ✕ Cannot convert these units.\n"+RESET); return
        draw_box([
            f"  {T['text']}{val} {fr}  →  {T['success']}{BOLD}{round(result,6)} {to}{RESET}",
        ], T, title="Unit Converter")
    except ValueError:
        print(T["error"]+f"  ✕ Invalid value.\n"+RESET)

def _convert_temp(val, fr, to):
    if fr=="°C":   c=val
    elif fr=="°F": c=(val-32)*5/9
    elif fr=="K":  c=val-273.15
    if to=="°C":   return c
    elif to=="°F": return c*9/5+32
    elif to=="K":  return c+273.15
    return val

# ── Password Generator ────────────────────────────────────────────────────────
def handle_passgen(cmd, T):
    parts = cmd.strip().split()
    length = 16
    if len(parts) >= 2:
        try: length = max(4, min(128, int(parts[1])))
        except: pass
    use_symbols = "--no-symbols" not in cmd
    alphabet = string.ascii_letters + string.digits
    if use_symbols: alphabet += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    password = "".join(secrets.choice(alphabet) for _ in range(length))
    strength = ("Weak" if length < 8 else "Fair" if length < 12 else
                "Strong" if length < 20 else "Very Strong")
    draw_box([
        f"  {T['success']}{BOLD}{password}{RESET}",
        f"  {T['muted']}Length:   {RESET}{T['text']}{length}{RESET}",
        f"  {T['muted']}Strength: {RESET}{T['warn']}{strength}{RESET}",
    ], T, title="Password Generator")
    _try_clipboard(password, T)

def _try_clipboard(text, T):
    try:
        r = subprocess.run(["termux-clipboard-set", text], capture_output=True, timeout=3)
        if r.returncode == 0:
            print(T["success"]+"  ✓ Copied to clipboard!\n"+RESET)
    except: pass

# ── Base64 ────────────────────────────────────────────────────────────────────
def handle_b64(cmd, T):
    parts = cmd.strip().split(" ", 2)
    if len(parts) < 3:
        print(f"\n  {T['muted']}Usage: b64 enc <text>  |  b64 dec <text>{RESET}\n")
        return
    action, text = parts[1].lower(), parts[2]
    try:
        if action in ("enc","encode"):
            result = base64.b64encode(text.encode()).decode()
            draw_box([f"  {T['success']}{result}{RESET}"], T, title="Base64 Encoded")
        elif action in ("dec","decode"):
            result = base64.b64decode(text.encode()).decode()
            draw_box([f"  {T['success']}{result}{RESET}"], T, title="Base64 Decoded")
        else:
            print(T["error"]+"  ✕ Use enc or dec\n"+RESET); return
        _try_clipboard(result, T)
    except Exception as e:
        print(T["error"]+f"  ✕ Error: {e}\n"+RESET)

# ── IP / Network Info ─────────────────────────────────────────────────────────
def handle_myip(T):
    try:
        r    = requests.get("https://ipapi.co/json/", timeout=6)
        data = r.json()
        draw_box([
            f"  {T['muted']}IP      {RESET}{T['success']}{data.get('ip','N/A')}{RESET}",
            f"  {T['muted']}City    {RESET}{T['text']}{data.get('city','N/A')}{RESET}",
            f"  {T['muted']}Region  {RESET}{T['text']}{data.get('region','N/A')}{RESET}",
            f"  {T['muted']}Country {RESET}{T['text']}{data.get('country_name','N/A')}{RESET}",
            f"  {T['muted']}ISP     {RESET}{T['text']}{data.get('org','N/A')}{RESET}",
            f"  {T['muted']}Timezone{RESET}{T['text']}{data.get('timezone','N/A')}{RESET}",
        ], T, title="My IP & Location")
    except Exception as e:
        print(T["error"]+f"  ✕ {e}\n"+RESET)

def handle_netinfo(T):
    lines = []
    cmds = [
        ("Hostname", "hostname"),
        ("Ping (google)", "ping -c 1 -W 2 8.8.8.8 2>/dev/null | tail -1 | awk -F'/' '{print $5\" ms\"}' || echo timeout"),
    ]
    for label, cmd in cmds:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        val = r.stdout.strip() or "N/A"
        lines.append(f"  {T['muted']}{label:<16}{RESET}{T['text']}{val}{RESET}")
    draw_box(lines, T, title="Network Info")

# ── Pomodoro Timer ────────────────────────────────────────────────────────────
def handle_pomodoro(T):
    print(f"\n  {T['accent']}Pomodoro Timer{RESET}")
    print(f"  {T['muted']}Work 25 min → Break 5 min{RESET}")
    confirm = input(T["primary"]+"  Start? (y/n): "+RESET+T["text"]).strip().lower()
    print(RESET,end="")
    if confirm != "y": print(T["muted"]+"  Cancelled.\n"+RESET); return

    def countdown(label, minutes, color):
        total = minutes * 60
        for remaining in range(total, -1, -1):
            m, s = divmod(remaining, 60)
            bar_len = 20
            filled  = int((total-remaining)/total*bar_len) if total>0 else bar_len
            bar     = color+"█"*filled+T["muted"]+"░"*(bar_len-filled)+RESET
            print(f"\r  {color}{label}{RESET}  {bar}  {color}{m:02d}:{s:02d}{RESET}  ", end="", flush=True)
            if remaining > 0: time.sleep(1)
        print()

    try:
        countdown("FOCUS  ", 25, T["success"])
        print(T["success"]+"\n  ✓ Work session done!\n"+RESET)
        input(T["accent"]+"  Press Enter to start break..."+RESET+T["text"])
        print(RESET,end="")
        countdown("BREAK  ", 5, T["accent"])
        print(T["primary"]+"\n  ✓ Break over. Back to work!\n"+RESET)
    except KeyboardInterrupt:
        print(T["warn"]+"\n\n  ◦ Timer stopped.\n"+RESET)

# ── Notes ─────────────────────────────────────────────────────────────────────
def load_notes():
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE) as f: return json.load(f)
        except: return []
    return []

def save_notes(n):
    with open(NOTES_FILE,"w") as f: json.dump(n,f,indent=2)

def handle_notes(cmd, T):
    parts  = cmd.strip().split(" ", 2)
    action = parts[1].lower() if len(parts) > 1 else "list"
    notes  = load_notes()
    if action == "list" or len(parts) == 1:
        if not notes:
            print(T["muted"]+"\n  No notes yet. Use: note add <text>\n"+RESET); return
        lines = [f"  {T['warn']}{i}.{RESET} {T['text']}{n['text'][:50]}{RESET}  {T['muted']}{n.get('date','')}{RESET}"
                 for i,n in enumerate(notes,1)]
        draw_box(lines, T, title=f"Notes ({len(notes)})")
    elif action == "add" and len(parts) == 3:
        notes.append({"text":parts[2],"date":datetime.now().strftime("%b %d %H:%M")})
        save_notes(notes)
        print(T["success"]+f"\n  ✓ Note saved.\n"+RESET)
    elif action in ("delete","del") and len(parts) == 3:
        try:
            idx = int(parts[2])-1
            if 0<=idx<len(notes):
                removed = notes.pop(idx); save_notes(notes)
                print(T["error"]+f"\n  ✕ Deleted: {removed['text'][:40]}\n"+RESET)
            else: print(T["error"]+"  ✕ Invalid number.\n"+RESET)
        except ValueError: print(T["error"]+"  ✕ Use: note delete <number>\n"+RESET)
    elif action == "clear":
        if input(T["warn"]+"  Clear all notes? (y/n): "+RESET).strip().lower()=="y":
            save_notes([]); print(T["accent"]+"  All notes cleared.\n"+RESET)
    else:
        print(f"\n  {T['warn']}note{RESET}              {T['muted']}list{RESET}")
        print(f"  {T['warn']}note add <text>{RESET}   {T['muted']}add{RESET}")
        print(f"  {T['warn']}note delete <n>{RESET}   {T['muted']}delete{RESET}")
        print(f"  {T['warn']}note clear{RESET}        {T['muted']}clear all{RESET}\n")

# ── File Manager ──────────────────────────────────────────────────────────────
def handle_fm(T):
    current = os.getcwd()
    while True:
        entries = sorted(os.scandir(current), key=lambda e: (not e.is_dir(), e.name.lower()))
        lines   = [f"  {T['muted']}◦ {current}{RESET}"]
        if current != "/":
            lines.append(f"  {T['accent']}  [0] ..{RESET}  {T['muted']}(parent){RESET}")
        for i, e in enumerate(entries, 1):
            if e.is_dir():
                lines.append(f"  {T['primary']}{i:>3}  📁 {e.name}/{RESET}")
            else:
                size = e.stat().st_size
                size_str = (f"{size}B" if size<1024 else
                            f"{size//1024}K" if size<1024**2 else f"{size//1024**2}M")
                lines.append(f"  {T['text']}{i:>3}  📄 {e.name}  {T['muted']}{size_str}{RESET}")
        draw_box(lines, T, title="File Manager")
        print(f"  {T['muted']}Enter number  |  q to quit  |  new <name> to create{RESET}\n")
        try:
            choice = input(T["primary"]+f"  {T['symbol']} fm> "+RESET+T["text"]).strip()
            print(RESET,end="")
        except KeyboardInterrupt:
            print(); break
        if choice.lower() in ("q","quit","exit"): break
        if choice == "0":
            current = os.path.dirname(current); continue
        if choice.lower().startswith("new "):
            fname = choice[4:].strip()
            open(os.path.join(current, fname),"a").close()
            print(T["success"]+f"  ✓ Created: {fname}\n"+RESET); continue
        if choice.isdigit():
            idx = int(choice)-1
            if 0 <= idx < len(entries):
                e = entries[idx]
                if e.is_dir():
                    current = e.path
                else:
                    try:
                        with open(e.path,"r",encoding="utf-8",errors="ignore") as f:
                            preview = f.readlines()[:20]
                        print()
                        for j,l in enumerate(preview,1):
                            print(T["muted"]+f"  {j:3} "+RESET+T["text"]+l.rstrip()+RESET)
                        print()
                    except Exception as ex:
                        print(T["error"]+f"  ✕ Cannot read: {ex}\n"+RESET)
            else:
                print(T["error"]+"  ✕ Invalid choice.\n"+RESET)

# ── Clipboard ─────────────────────────────────────────────────────────────────
def handle_copy(cmd, T):
    text = cmd[5:].strip()
    if not text:
        print(T["muted"]+"\n  Usage: copy <text>\n"+RESET); return
    _try_clipboard(text, T)

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
        lines.append(f"  {T['muted']}No tasks yet. Use: todo add <task>{RESET}")
    else:
        for i,t in enumerate(todos,1):
            status = T["success"]+"✓"+RESET if t["done"] else T["muted"]+"◦"+RESET
            date   = T["muted"]+f" ({t.get('date','')})" +RESET if t.get("date") else ""
            col    = T["muted"] if t["done"] else T["text"]
            lines.append(f"  {status} {i}. {col}{t['task'][:38]}{RESET}{date}")
    total    = len(todos)
    done     = sum(1 for t in todos if t["done"])
    bar_done = int(done/total*16) if total>0 else 0
    bar      = T["success"]+"█"*bar_done+T["dark"]+"░"*(16-bar_done)+RESET
    lines.append(f"  {bar}  {T['success']}{done}{RESET} done  {T['warn']}{total-done}{RESET} left")
    draw_box(lines, T, title="To-Do List")

def handle_todo(cmd, T):
    parts  = cmd.strip().split(" ",2)
    action = parts[1].lower() if len(parts)>1 else "list"
    todos  = load_todos()
    if action=="list" or len(parts)==1:
        show_todos(T)
    elif action=="add" and len(parts)==3:
        todos.append({"task":parts[2],"done":False,"date":datetime.now().strftime("%b %d")})
        save_todos(todos); print(T["success"]+f"\n  ✓ Added.\n"+RESET); show_todos(T)
    elif action in ("done","undone","delete") and len(parts)==3:
        try:
            idx = int(parts[2])-1
            if 0<=idx<len(todos):
                if action=="done":    todos[idx]["done"]=True
                elif action=="undone":todos[idx]["done"]=False
                elif action=="delete":todos.pop(idx)
                save_todos(todos); show_todos(T)
            else: print(T["error"]+f"  ✕ No task #{parts[2]}.\n"+RESET)
        except ValueError: print(T["error"]+f"  Use: todo {action} <number>\n"+RESET)
    elif action=="clear":
        if input(T["warn"]+"  Clear all? (y/n): "+RESET).strip().lower()=="y":
            save_todos([]); print(T["accent"]+"  All cleared.\n"+RESET)

# ── Git ───────────────────────────────────────────────────────────────────────
def git_helper(cmd, T, persona_key):
    parts  = cmd.strip().split(" ",1)
    action = parts[1].lower() if len(parts)>1 else "help"
    if action=="status":
        r = subprocess.run("git status --short",shell=True,capture_output=True,text=True)
        print(T["warn"]+"\n  ◦ Git Status"+RESET); divider(T)
        for line in (r.stdout.strip() or "Nothing to commit.").split("\n"):
            print(f"  {T['text']}{line}{RESET}")
        print()
    elif action=="log":
        r = subprocess.run("git log --oneline -7",shell=True,capture_output=True,text=True)
        print(T["warn"]+"\n  ◦ Recent Commits"+RESET); divider(T)
        for line in (r.stdout.strip() or "No commits yet.").split("\n"):
            print(f"  {T['text']}{line}{RESET}")
        print()
    elif action=="commit":
        r = subprocess.run("git status --short",shell=True,capture_output=True,text=True)
        status = r.stdout.strip()
        if not status: print(T["accent"]+"  ◦ Nothing to commit.\n"+RESET); return
        print(T["muted"]+"\n  ◦ Generating commit message...\n"+RESET)
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role":"user","content":
                    f"Write a short git commit message (conventional commits). Output the message only.\n\nGit status:\n{status}"}],
                max_tokens=60)
            msg = response.choices[0].message.content.strip().strip('"')
        except Exception as e:
            print(T["error"]+f"  ✕ AI error: {e}\n"+RESET); return
        print(T["primary"]+f"  {T['symbol']} Suggested: {T['text']}{msg}{RESET}")
        confirm = input(T["accent"]+"\n  Use this? (y/n/edit): "+RESET+T["text"]).strip().lower()
        print(RESET,end="")
        if confirm=="y":
            subprocess.run(f'git add -A && git commit -m "{msg}"',shell=True)
            print(T["success"]+"  ✓ Committed!\n"+RESET)
        elif confirm=="edit":
            custom = input(T["accent"]+"  Your message: "+RESET+T["text"]).strip()
            print(RESET,end="")
            if custom:
                subprocess.run(f'git add -A && git commit -m "{custom}"',shell=True)
                print(T["success"]+"  ✓ Committed!\n"+RESET)
        else: print(T["muted"]+"  Cancelled.\n"+RESET)
    elif action=="push":
        r = subprocess.run("git push",shell=True,capture_output=True,text=True)
        print(T["text"]+(r.stdout or r.stderr).strip()+RESET+"\n")
    elif action=="pull":
        r = subprocess.run("git pull",shell=True,capture_output=True,text=True)
        print(T["text"]+(r.stdout or r.stderr).strip()+RESET+"\n")
    else:
        print(f"\n  {T['warn']}git status{RESET}    {T['muted']}changed files{RESET}")
        print(f"  {T['warn']}git log{RESET}       {T['muted']}recent commits{RESET}")
        print(f"  {T['warn']}git commit{RESET}    {T['muted']}AI commit message{RESET}")
        print(f"  {T['warn']}git push/pull{RESET} {T['muted']}push or pull{RESET}\n")

# ── Persona menu ──────────────────────────────────────────────────────────────
def show_personas(current, T, user_name):
    keys  = list(PERSONAS.keys())
    lines = [
        f"  {T['warn']}{i}. {p['name']:<10}{RESET}{T['muted']}{p['desc'][:30]}{RESET}"
        + (T["success"]+" ✓"+RESET if key==current else "")
        for i,(key,p) in enumerate(PERSONAS.items(),1)
    ]
    draw_box(lines, T, title="Switch AI Persona")
    while True:
        choice = input(T["primary"]+f"  {T['symbol']} Pick 1-{len(keys)} or Enter to cancel: "+RESET+T["text"]).strip()
        print(RESET,end="")
        if choice=="": return current
        if choice.isdigit() and 1<=int(choice)<=len(keys):
            chosen = keys[int(choice)-1]; p = PERSONAS[chosen]
            print(T["primary"]+f"\n  {T['symbol']} → {p['name']}\n"+RESET)
            return chosen
        print(T["error"]+f"  ✕ Enter 1-{len(keys)}.\n"+RESET)

# ── Open URL ──────────────────────────────────────────────────────────────────
def open_url(url_or_name, T):
    name = url_or_name.lower().strip().replace("https://","").replace("http://","").replace("www.","")
    for key, url in SITE_MAP.items():
        if key in name:
            print(T["success"]+f"\n  ◦ Opening {key.capitalize()}...\n"+RESET)
            _open_url_termux(url, T); return
    url = (url_or_name if url_or_name.startswith("http") else
           (f"https://{name}" if "." in name else f"https://www.google.com/search?q={name}"))
    print(T["success"]+f"\n  ◦ Opening {url}...\n"+RESET)
    _open_url_termux(url, T)

def _open_url_termux(url, T):
    try:
        r = subprocess.run(["termux-open-url", url], capture_output=True, timeout=5)
        if r.returncode != 0:
            subprocess.Popen(["xdg-open",url],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except: print(T["warn"]+f"  Copy URL: {url}\n"+RESET)

# ── Sysinfo ───────────────────────────────────────────────────────────────────
def show_sysinfo(T):
    try:
        cpu  = subprocess.run("cat /proc/loadavg | awk '{print $1\" (1min)\"}'",
                              shell=True,capture_output=True,text=True).stdout.strip()
        mem  = subprocess.run("free -m | awk 'NR==2{printf \"%s/%s MB\", $3,$2}'",
                              shell=True,capture_output=True,text=True).stdout.strip()
        upt  = subprocess.run("uptime -p",shell=True,capture_output=True,text=True).stdout.strip()
        batt = "N/A"
        try:
            br = subprocess.run("termux-battery-status",shell=True,capture_output=True,text=True,timeout=3)
            if br.stdout:
                bd   = json.loads(br.stdout)
                batt = f"{bd.get('percentage','?')}%  {bd.get('status','?')}"
        except: pass
        draw_box([
            f"  {T['muted']}CPU Load {RESET}{T['text']}{cpu or 'N/A'}{RESET}",
            f"  {T['muted']}Memory   {RESET}{T['text']}{mem or 'N/A'}{RESET}",
            f"  {T['muted']}Battery  {RESET}{T['text']}{batt}{RESET}",
            f"  {T['muted']}Uptime   {RESET}{T['text']}{upt or 'N/A'}{RESET}",
        ], T, title="System Info")
    except Exception as e:
        print(T["error"]+f"  ✕ {e}\n"+RESET)

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
    if not history: print(T["accent"]+"  ◦ No history yet.\n"+RESET); return
    w = get_terminal_width()
    print(); divider(T,w)
    print(T["accent"]+f"  {T['symbol']} Last {min(10,len(history))} messages"+RESET)
    divider(T,w)
    for msg in history[-10:]:
        t       = msg.get("time","")
        role    = msg.get("role","")
        content = msg.get("content","")[:65]
        if role=="user":
            print(T["success"]+f"  You [{t}]: "+T["text"]+f"{content}..."+RESET)
        else:
            print(T["primary"]+f"  AI  [{t}]: "+T["muted"]+f"{content}..."+RESET)
    divider(T,w); print()

def clear_history():
    if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
    conversation_history.clear()
    print("\033[1;36m  ◦ Memory cleared.\033[0m\n")

# ── File reader ───────────────────────────────────────────────────────────────
def handle_file_read(cmd, T, persona_key):
    parts = cmd.strip().split(" ",1)
    if len(parts)<2: print(T["accent"]+"  Usage: read <filename>\n"+RESET); return
    filepath = os.path.expanduser(parts[1].strip())
    if not os.path.exists(filepath):
        local = os.path.join(os.getcwd(),parts[1].strip())
        if os.path.exists(local): filepath=local
        else: print(T["error"]+f"  ✕ File not found.\n"+RESET); return
    try:
        with open(filepath,"r",encoding="utf-8",errors="ignore") as f:
            lines = f.readlines()
        print(T["warn"]+f"\n  ◦ Preview (15 lines)"+RESET)
        for i,line in enumerate(lines[:15],1):
            print(T["muted"]+f"  {i:3} "+RESET+T["text"]+line.rstrip()+RESET)
        print()
        stop_event = threading.Event()
        anim = threading.Thread(target=thinking_animation,args=(stop_event,T))
        anim.daemon=True; anim.start()
        file_content = "".join(lines[:200])
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role":"system","content":PERSONAS[persona_key]["prompt"]},
                    {"role":"user","content":
                        f"Analyse this file briefly:\n1. What it does\n2. Key parts\n3. Any issues\n\n{file_content}"}
                ], max_tokens=1024)
        finally:
            stop_event.set(); anim.join()
        print_reply(response.choices[0].message.content, T)
    except Exception as e:
        print(T["error"]+f"  ✕ Error: {e}\n"+RESET)

# ── Web search (no DDGS) ──────────────────────────────────────────────────────
def web_search(query, T):
    print(T["muted"]+f"  ◦ Searching: {query}"+RESET)
    try:
        url     = f"https://news.google.com/rss/search?q={query.replace(' ','+')}&hl=en&gl=IN"
        r       = requests.get(url, timeout=8)
        titles  = re.findall(r'<title>(.*?)</title>', r.text)[1:5]
        descs   = re.findall(r'<description>(.*?)</description>', r.text)[1:5]
        results = []
        for t,d in zip(titles,descs):
            results.append(f"- {re.sub('<.*?>','',t)}\n  {re.sub('<.*?>','',d)[:100]}\n")
        return "\n".join(results) if results else "No results found."
    except Exception as e: return f"Search failed: {e}"

def should_search(user_input):
    keywords = ["search","look up","latest","news","today","current","price",
                "weather","2024","2025","2026","what is","who is","when is","how much"]
    return any(k in user_input.lower() for k in keywords)

def run_command(cmd, T):
    if any(d in cmd for d in DANGEROUS):
        return T["error"]+"  ✕ Blocked: too dangerous."+RESET
    print(T["muted"]+f"  ◦ Running: {cmd}"+RESET)
    try:
        result = subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=15)
        return T["warn"]+(result.stdout or result.stderr or "(no output)").strip()+RESET
    except subprocess.TimeoutExpired: return T["error"]+"  ✕ Timed out."+RESET
    except Exception as e:            return T["error"]+f"  ✕ Error: {e}"+RESET

def extract_command(reply, prefix):
    for line in reply.splitlines():
        s = line.strip()
        if s.startswith(prefix+":"):
            v = s[len(prefix)+1:].strip()
            if v: return v
    return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✦ NEW v6.0 FEATURES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ── ✦ 1. Email Drafter ────────────────────────────────────────────────────────
def handle_email(T):
    print()
    divider(T)
    print(T["accent"] + f"  {T['symbol']} Email Drafter" + RESET)
    divider(T)
    print(T["muted"] + "  Fill in the details below.\n" + RESET)

    to      = input(T["warn"] + "  To (name/role): " + RESET + T["text"]).strip(); print(RESET,end="")
    subject = input(T["warn"] + "  Subject:        " + RESET + T["text"]).strip(); print(RESET,end="")
    purpose = input(T["warn"] + "  Purpose:        " + RESET + T["text"]).strip(); print(RESET,end="")
    tone_opts = ["1. Professional", "2. Friendly", "3. Formal", "4. Apologetic", "5. Follow-up"]
    print(T["muted"] + "\n  Tone options:" + RESET)
    for opt in tone_opts:
        print(T["text"] + f"    {opt}" + RESET)
    tone_pick = input(T["warn"] + "  Pick tone (1-5): " + RESET + T["text"]).strip(); print(RESET,end="")
    tone_map  = {"1":"professional","2":"friendly","3":"formal","4":"apologetic","5":"follow-up"}
    tone      = tone_map.get(tone_pick, "professional")

    print()
    stop_event = threading.Event()
    anim = threading.Thread(target=thinking_animation, args=(stop_event, T))
    anim.daemon = True; anim.start()

    prompt = f"""Write a {tone} email with these details:
To: {to}
Subject: {subject}
Purpose: {purpose}

Format:
Subject: <subject line>
---
<email body>

Keep it concise and professional. Use appropriate greeting and sign-off."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role":"user","content":prompt}],
            max_tokens=600)
        stop_event.set(); anim.join()
        email_text = response.choices[0].message.content.strip()
        print("\r"+" "*36+"\r",end="",flush=True)
        print()
        divider(T)
        print(T["success"] + f"  {T['symbol']} Generated Email" + RESET)
        divider(T)
        print_reply(email_text, T)

        # Save option
        save_it = input(T["accent"] + "  Save this email? (y/n): " + RESET + T["text"]).strip().lower()
        print(RESET,end="")
        if save_it == "y":
            fname = os.path.expanduser(f"~/email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(fname, "w") as f:
                f.write(email_text)
            print(T["success"] + f"  ✓ Saved to {fname}\n" + RESET)
        _try_clipboard(email_text, T)

    except Exception as e:
        stop_event.set(); anim.join()
        print(T["error"] + f"\n  ✕ Error: {e}\n" + RESET)


# ── ✦ 2. LinkedIn Post Writer ─────────────────────────────────────────────────
def handle_linkedin(T):
    print()
    divider(T)
    print(T["accent"] + f"  {T['symbol']} LinkedIn Post Writer" + RESET)
    divider(T)
    print(T["muted"] + "  Create a professional LinkedIn post.\n" + RESET)

    topic   = input(T["warn"] + "  Topic/Achievement:  " + RESET + T["text"]).strip(); print(RESET,end="")
    details = input(T["warn"] + "  Key details:        " + RESET + T["text"]).strip(); print(RESET,end="")

    style_opts = ["1. Achievement/Win", "2. Lesson Learned", "3. Industry Insight",
                  "4. Job Announcement", "5. Motivational", "6. Product/Project Launch"]
    print(T["muted"] + "\n  Post style:" + RESET)
    for opt in style_opts:
        print(T["text"] + f"    {opt}" + RESET)
    style_pick = input(T["warn"] + "  Pick style (1-6): " + RESET + T["text"]).strip(); print(RESET,end="")
    style_map  = {
        "1":"achievement/win post with impact numbers",
        "2":"lesson learned with actionable takeaway",
        "3":"industry insight with unique perspective",
        "4":"job announcement with excitement",
        "5":"motivational post with story",
        "6":"product or project launch post"
    }
    style = style_map.get(style_pick, "professional post")

    print()
    stop_event = threading.Event()
    anim = threading.Thread(target=thinking_animation, args=(stop_event, T))
    anim.daemon = True; anim.start()

    prompt = f"""Write a LinkedIn {style} about:
Topic: {topic}
Details: {details}

Rules:
- Start with a strong hook (first line grabs attention)
- Use short paragraphs (1-2 sentences each)
- Add 3-5 relevant emojis naturally
- End with a call to action or question
- Add 5 relevant hashtags at the end
- Keep it under 250 words
- Make it authentic and engaging"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role":"user","content":prompt}],
            max_tokens=500)
        stop_event.set(); anim.join()
        post_text = response.choices[0].message.content.strip()
        print("\r"+" "*36+"\r",end="",flush=True)
        print()
        divider(T)
        print(T["success"] + f"  {T['symbol']} LinkedIn Post" + RESET)
        divider(T)
        print_reply(post_text, T)

        save_it = input(T["accent"] + "  Save this post? (y/n): " + RESET + T["text"]).strip().lower()
        print(RESET,end="")
        if save_it == "y":
            fname = os.path.expanduser(f"~/linkedin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(fname, "w") as f:
                f.write(post_text)
            print(T["success"] + f"  ✓ Saved to {fname}\n" + RESET)
        _try_clipboard(post_text, T)

    except Exception as e:
        stop_event.set(); anim.join()
        print(T["error"] + f"\n  ✕ Error: {e}\n" + RESET)


# ── ✦ 3. Documentation Generator ─────────────────────────────────────────────
def handle_docgen(T, persona_key):
    print()
    divider(T)
    print(T["accent"] + f"  {T['symbol']} Documentation Generator" + RESET)
    divider(T)
    print(T["muted"] + "  Generate docs for your code.\n" + RESET)

    doc_types = ["1. README.md", "2. Function/Code docs", "3. API docs",
                 "4. Setup/Install guide", "5. Changelog"]
    for opt in doc_types:
        print(T["text"] + f"    {opt}" + RESET)
    doc_pick = input(T["warn"] + "\n  Pick type (1-5): " + RESET + T["text"]).strip(); print(RESET,end="")
    doc_map  = {
        "1":"a professional README.md",
        "2":"inline code documentation with docstrings",
        "3":"API documentation",
        "4":"a setup and installation guide",
        "5":"a changelog"
    }
    doc_type = doc_map.get(doc_pick, "documentation")

    print(T["muted"] + "\n  Paste your code or describe your project." + RESET)
    print(T["muted"] + "  Type END on a new line when done.\n" + RESET)

    lines = []
    while True:
        try:
            line = input(T["text"])
            print(RESET, end="")
            if line.strip().upper() == "END": break
            lines.append(line)
        except KeyboardInterrupt:
            print(); break

    content = "\n".join(lines)
    if not content.strip():
        print(T["warn"] + "  Nothing entered.\n" + RESET); return

    print()
    stop_event = threading.Event()
    anim = threading.Thread(target=thinking_animation, args=(stop_event, T))
    anim.daemon = True; anim.start()

    prompt = f"""Generate {doc_type} for the following:

{content}

Make it professional, clear, and well-structured.
Use proper markdown formatting.
Include all important sections."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role":"system","content":PERSONAS[persona_key]["prompt"]},
                {"role":"user","content":prompt}
            ],
            max_tokens=1200)
        stop_event.set(); anim.join()
        doc_text = response.choices[0].message.content.strip()
        print("\r"+" "*36+"\r",end="",flush=True)
        print()
        divider(T)
        print(T["success"] + f"  {T['symbol']} Generated Documentation" + RESET)
        divider(T)
        print_reply(doc_text, T)

        # Auto-save as .md file
        fname = os.path.expanduser(f"~/docs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(fname, "w") as f:
            f.write(doc_text)
        print(T["success"] + f"  ✓ Auto-saved to {fname}\n" + RESET)
        _try_clipboard(doc_text, T)

    except Exception as e:
        stop_event.set(); anim.join()
        print(T["error"] + f"\n  ✕ Error: {e}\n" + RESET)


# ── ✦ 4. Secure Notes ─────────────────────────────────────────────────────────
def _hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def _load_secure_notes():
    if os.path.exists(SECURE_NOTES_FILE):
        try:
            with open(SECURE_NOTES_FILE) as f: return json.load(f)
        except: return {"pin_hash": None, "notes": []}
    return {"pin_hash": None, "notes": []}

def _save_secure_notes(data):
    with open(SECURE_NOTES_FILE, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(SECURE_NOTES_FILE, 0o600)  # owner read/write only

def _encrypt_text(text, pin):
    key = (pin * 8)[:32]
    result = []
    for i, ch in enumerate(text):
        result.append(chr(ord(ch) ^ ord(key[i % len(key)])))
    return base64.b64encode("".join(result).encode("latin-1")).decode()

def _decrypt_text(enc_text, pin):
    key = (pin * 8)[:32]
    decoded = base64.b64decode(enc_text.encode()).decode("latin-1")
    result = []
    for i, ch in enumerate(decoded):
        result.append(chr(ord(ch) ^ ord(key[i % len(key)])))
    return "".join(result)

def handle_secure_notes(cmd, T):
    data   = _load_secure_notes()
    parts  = cmd.strip().split(" ", 2)
    action = parts[1].lower() if len(parts) > 1 else "list"

    # Setup PIN on first use
    if data["pin_hash"] is None:
        print(T["warn"] + "\n  ◦ First time setup — create a PIN\n" + RESET)
        pin1 = input(T["accent"] + "  Create PIN (4-8 digits): " + RESET + T["text"]).strip()
        print(RESET, end="")
        pin2 = input(T["accent"] + "  Confirm PIN:            " + RESET + T["text"]).strip()
        print(RESET, end="")
        if pin1 != pin2:
            print(T["error"] + "  ✕ PINs do not match.\n" + RESET); return
        if not pin1.isdigit() or not (4 <= len(pin1) <= 8):
            print(T["error"] + "  ✕ PIN must be 4-8 digits.\n" + RESET); return
        data["pin_hash"] = _hash_pin(pin1)
        _save_secure_notes(data)
        print(T["success"] + "  ✓ PIN created! Secure notes ready.\n" + RESET)
        return

    # Verify PIN
    pin = input(T["warn"] + "\n  Enter PIN: " + RESET + T["text"]).strip()
    print(RESET, end="")
    if _hash_pin(pin) != data["pin_hash"]:
        print(T["error"] + "  ✕ Wrong PIN!\n" + RESET); return

    notes = data.get("notes", [])

    if action == "list" or len(parts) == 1:
        if not notes:
            print(T["muted"] + "\n  No secure notes. Use: secu note add <text>\n" + RESET)
            return
        lines = []
        for i, n in enumerate(notes, 1):
            try:
                decrypted = _decrypt_text(n["text"], pin)
                preview   = decrypted[:40] + "..." if len(decrypted) > 40 else decrypted
            except:
                preview = "[decryption error]"
            lines.append(f"  {T['warn']}{i}.{RESET} {T['text']}{preview}{RESET}  {T['muted']}{n.get('date','')}{RESET}")
        draw_box(lines, T, title=f"🔒 Secure Notes ({len(notes)})")

    elif action == "add" and len(parts) == 3:
        encrypted = _encrypt_text(parts[2], pin)
        notes.append({"text": encrypted, "date": datetime.now().strftime("%b %d %H:%M")})
        data["notes"] = notes
        _save_secure_notes(data)
        print(T["success"] + "\n  ✓ Secure note saved & encrypted.\n" + RESET)

    elif action in ("view", "show") and len(parts) == 3:
        try:
            idx = int(parts[2]) - 1
            if 0 <= idx < len(notes):
                decrypted = _decrypt_text(notes[idx]["text"], pin)
                draw_box([
                    f"  {T['muted']}Note #{idx+1}  {notes[idx].get('date','')}{RESET}",
                    f"  {T['text']}{decrypted}{RESET}",
                ], T, title="🔒 Secure Note")
            else:
                print(T["error"] + "  ✕ Invalid number.\n" + RESET)
        except ValueError:
            print(T["error"] + "  ✕ Use: secu note view <number>\n" + RESET)

    elif action in ("delete", "del") and len(parts) == 3:
        try:
            idx = int(parts[2]) - 1
            if 0 <= idx < len(notes):
                notes.pop(idx)
                data["notes"] = notes
                _save_secure_notes(data)
                print(T["error"] + "\n  ✕ Secure note deleted.\n" + RESET)
            else:
                print(T["error"] + "  ✕ Invalid number.\n" + RESET)
        except ValueError:
            print(T["error"] + "  ✕ Use: secu note delete <number>\n" + RESET)

    elif action == "clear":
        confirm = input(T["warn"] + "  Delete ALL secure notes? (y/n): " + RESET).strip().lower()
        if confirm == "y":
            data["notes"] = []
            _save_secure_notes(data)
            print(T["accent"] + "  All secure notes cleared.\n" + RESET)

    elif action == "pin":
        new1 = input(T["accent"] + "  New PIN: " + RESET + T["text"]).strip(); print(RESET,end="")
        new2 = input(T["accent"] + "  Confirm: " + RESET + T["text"]).strip(); print(RESET,end="")
        if new1 != new2:
            print(T["error"] + "  ✕ PINs do not match.\n" + RESET); return
        # Re-encrypt all notes with new PIN
        for n in notes:
            try:
                plain      = _decrypt_text(n["text"], pin)
                n["text"]  = _encrypt_text(plain, new1)
            except: pass
        data["pin_hash"] = _hash_pin(new1)
        data["notes"]    = notes
        _save_secure_notes(data)
        print(T["success"] + "  ✓ PIN changed & notes re-encrypted.\n" + RESET)

    else:
        print(f"\n  {T['success']}secu note{RESET}               {T['muted']}list notes{RESET}")
        print(f"  {T['success']}secu note add <text>{RESET}    {T['muted']}add encrypted note{RESET}")
        print(f"  {T['success']}secu note view <n>{RESET}      {T['muted']}view a note{RESET}")
        print(f"  {T['success']}secu note delete <n>{RESET}    {T['muted']}delete a note{RESET}")
        print(f"  {T['success']}secu note clear{RESET}         {T['muted']}clear all{RESET}")
        print(f"  {T['success']}secu note pin{RESET}           {T['muted']}change PIN{RESET}\n")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ── Chat ──────────────────────────────────────────────────────────────────────
def do_chat(user_input, persona_key, T):
    stop_event = threading.Event()
    start_time = time.time()
    anim = threading.Thread(target=thinking_animation,args=(stop_event,T))
    anim.daemon=True; anim.start()
    reply = ""
    retries = 2
    for attempt in range(retries+1):
        try:
            extra = ""
            if should_search(user_input):
                extra = f"\n\nWeb results:\n{web_search(user_input,T)}\n\nUse above to answer."
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            conversation_history.append({"role":"user","content":user_input+extra})
            saved = load_history()
            saved.append({"role":"user","content":user_input,"time":now})
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role":"system","content":PERSONAS[persona_key]["prompt"]}]
                         + conversation_history[-20:],
                max_tokens=1024)
            reply = response.choices[0].message.content
            stop_event.set(); anim.join()
            print("\r"+" "*36+"\r",end="",flush=True)
            conversation_history.append({"role":"assistant","content":reply})
            saved.append({"role":"assistant","content":reply,"time":now})
            save_history(saved)
            print_reply(reply, T)
            break
        except Exception as e:
            if attempt < retries:
                print(T["warn"]+f"\r  ◦ Retrying ({attempt+1}/{retries})..."+RESET,end="",flush=True)
                time.sleep(2)
            else:
                stop_event.set(); anim.join()
                print("\r"+" "*36+"\r",end="",flush=True)
                print(T["error"]+f"  ✕ Error: {e}\n"+RESET)
    return reply, start_time

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global conversation_history
    user_name       = get_user_name()
    current_persona = load_persona()
    current_theme   = get_theme_name()
    city            = get_city()
    saved           = load_history()
    T               = THEMES[current_theme]

    if saved:
        conversation_history = [{"role":m["role"],"content":m["content"]} for m in saved[-20:]]
        splash_screen(T,returning=True,msg_count=len(conversation_history),
                      current_persona=current_persona,user_name=user_name)
    else:
        splash_screen(T,returning=False,current_persona=current_persona,user_name=user_name)

    morning_briefing(T, user_name, city)

    while True:
        try:
            p = PERSONAS[current_persona]
            T = THEMES[current_theme]
            w = get_terminal_width()

            user_input = input(T["accent"]+f"  {T['user_sym']} "+RESET+T["text"]).strip()
            print(RESET,end="")
            if not user_input: continue

            lo = user_input.lower()

            if lo in ("exit","quit","bye"):
                farewell_screen(T,user_name); break

            elif lo=="history":            show_history(T)
            elif lo=="clear memory":       clear_history()
            elif lo=="briefing":           morning_briefing(T,user_name,city)
            elif lo=="sysinfo":            show_sysinfo(T)
            elif lo in ("fm","files"):     handle_fm(T)
            elif lo=="myip":               handle_myip(T)
            elif lo=="netinfo":            handle_netinfo(T)
            elif lo=="pomodoro":           handle_pomodoro(T)
            elif lo=="theme":              show_themes(current_theme,T)
            elif lo=="persona":
                current_persona = show_personas(current_persona,T,user_name)
                save_persona(current_persona)

            # ✦ New v6.0 commands
            elif lo=="email":              handle_email(T)
            elif lo=="linkedin":           handle_linkedin(T)
            elif lo=="docgen":             handle_docgen(T, current_persona)
            elif lo.startswith("secu note"): handle_secure_notes(user_input, T)

            elif lo.startswith("city "):
                new_city = user_input[5:].strip()
                set_city(new_city,T); city=new_city

            elif lo.startswith("calc "):   handle_calc(user_input,T)
            elif lo.startswith("convert "): handle_convert(user_input,T)
            elif lo.startswith("passgen"): handle_passgen(user_input,T)
            elif lo.startswith("b64 "):    handle_b64(user_input,T)
            elif lo.startswith("copy "):   handle_copy(user_input,T)
            elif lo.startswith("todo"):    handle_todo(user_input,T)
            elif lo.startswith("note"):    handle_notes(user_input,T)
            elif lo.startswith("git "):    git_helper(user_input,T,current_persona)
            elif lo.startswith("open "):   open_url(user_input[5:].strip(),T)
            elif lo.startswith("read "):   handle_file_read(user_input,T,current_persona)

            elif lo.startswith("theme "):
                new_t = user_input[6:].strip().lower()
                if new_t in THEMES:
                    current_theme=new_t; save_theme(current_theme)
                    T=THEMES[current_theme]
                    print(T["primary"]+f"\n  {T['symbol']} Theme → {T['name']}\n"+RESET)
                else:
                    print(T["error"]+f"  ✕ Unknown theme. Try: {', '.join(THEMES.keys())}\n"+RESET)

            elif lo.startswith("persona "):
                new_p = user_input[8:].strip().lower()
                if new_p in PERSONAS:
                    current_persona=new_p; save_persona(current_persona)
                    p2=PERSONAS[current_persona]
                    print(T["primary"]+f"\n  {T['symbol']} → {p2['name']}\n"+RESET)
                else:
                    print(T["error"]+f"  ✕ Unknown. Try: {', '.join(PERSONAS.keys())}\n"+RESET)

            elif lo.startswith("search:"):
                query   = user_input[7:].strip()
                results = web_search(query,T)
                conversation_history.append({"role":"user","content":f"Summarize:\n{results}"})
                stop_event = threading.Event()
                anim = threading.Thread(target=thinking_animation,args=(stop_event,T))
                anim.daemon=True; anim.start()
                try:
                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=[{"role":"system","content":p["prompt"]}]+conversation_history[-20:],
                        max_tokens=1024)
                    stop_event.set(); anim.join()
                    print("\r"+" "*36+"\r",end="",flush=True)
                    reply = response.choices[0].message.content
                    conversation_history.append({"role":"assistant","content":reply})
                    print(); divider(T,w)
                    print(T["primary"]+f"  {T['symbol']} {p['name']}:"+RESET)
                    divider(T,w)
                    print_reply(reply,T)
                    status_bar(time.time(),reply,p["name"],T)
                except Exception as e:
                    stop_event.set(); anim.join()
                    print(T["error"]+f"\n  ✕ {e}\n"+RESET)

            else:
                print(); divider(T,w)
                print(T["primary"]+f"  {T['symbol']} {p['name']}:"+RESET)
                divider(T,w)
                reply, start_time = do_chat(user_input,current_persona,T)
                open_line = extract_command(reply,"OPEN_URL")
                run_line  = extract_command(reply,"RUN_CMD")
                if open_line:
                    open_url(open_line,T)
                elif run_line:
                    confirm = input(T["warn"]+f"\n  ◦ Run '{run_line}'? (y/n): "+RESET+T["text"]).strip()
                    print(RESET,end="")
                    if confirm=="y": print(run_command(run_line,T)+"\n")
                    else: print(T["muted"]+"  Cancelled.\n"+RESET)
                else:
                    status_bar(start_time,reply,p["name"],T)

        except KeyboardInterrupt:
            farewell_screen(T,user_name); sys.exit(0)

if __name__ == "__main__":
    main()
