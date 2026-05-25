#!/usr/bin/env python3
"""
Dev AI - Ocean Dark Edition
GitHub: https://github.com/Prathap2349/dev-Ai
"""

import os, sys, json, subprocess, tempfile, time, random, threading, requests, webbrowser
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

# ── Ocean Dark Color Palette ──────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"

# Ocean Dark specific colors
NAVY    = "\033[38;2;1;22;39m"       # #011627 deep navy
BLUE    = "\033[38;2;130;170;255m"   # #82aaff blue purple
TEAL    = "\033[38;2;127;219;202m"   # #7fdbca teal
WHITE   = "\033[38;2;238;255;255m"   # #eeffff near white
MUTED   = "\033[38;2;99;119;119m"    # #637777 muted
DARK    = "\033[38;2;29;51;84m"      # #1d3354 dark separator
YELLOW  = "\033[38;2;255;203;107m"   # #ffcb6b warm yellow
GREEN   = "\033[38;2;195;232;141m"   # #c3e48d soft green
CORAL   = "\033[38;2;240;113;120m"   # #f07178 coral red
PURPLE  = "\033[38;2;199;146;234m"   # #c792ea purple

# aliases for compatibility
CYAN    = TEAL
RED     = CORAL
GRAY    = MUTED

DANGEROUS = ["rm -rf","rmdir","mkfs","dd if","shutdown","reboot","chmod 777","sudo rm"]
BOX = 58
conversation_history = []

# ── TTS ───────────────────────────────────────────────────────────────────────
_tts_proc = None
_tts_lock = threading.Lock()

def speak(text, voice="Samantha"):
    global _tts_proc
    clean_lines = []
    in_code = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            clean_lines.append(line)
    clean = " ".join(clean_lines).strip()
    if not clean:
        return
    with _tts_lock:
        if _tts_proc and _tts_proc.poll() is None:
            _tts_proc.kill()
            _tts_proc.wait()
        try:
            _tts_proc = subprocess.Popen(
                ["say", "-v", voice, clean],
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
            _tts_proc.kill()
            _tts_proc.wait()

# ── Config ────────────────────────────────────────────────────────────────────
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f: return json.load(f)
        except: return {}
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f: json.dump(config, f, indent=2)

def get_user_name():
    config = load_config()
    if config.get("name"): return config["name"]
    os.system("clear")
    w = get_terminal_width()
    print()
    print(BLUE + "◈" * w + RESET)
    print()
    print(TEAL + "  Welcome to Dev AI — Ocean Dark Edition".center(w) + RESET)
    print(MUTED + "  Let's get you set up.".center(w) + RESET)
    print()
    while True:
        name = input(TEAL + "  ◈ Your name: " + RESET + WHITE).strip()
        print(RESET, end="")
        if name:
            config["name"] = name
            save_config(config)
            print(BLUE + f"\n  Nice to meet you, {name}!\n" + RESET)
            return name
        print(CORAL + "  Please enter your name." + RESET)

def get_city():
    config = load_config()
    if config.get("city"): return config["city"]
    try:
        r = requests.get("https://ipapi.co/city/", timeout=5)
        city = r.text.strip()
        if city and len(city) < 50:
            config["city"] = city
            save_config(config)
            return city
    except: pass
    return "Chennai"

def set_city(new_city, voice):
    config = load_config()
    config["city"] = new_city
    save_config(config)
    print(GREEN + f"\n  ◦ City updated to: {new_city}\n" + RESET)
    speak(f"City updated to {new_city}.", voice)

# ── Personas ──────────────────────────────────────────────────────────────────
PERSONAS = {
    "dev": {
        "name": "Dev", "emoji": "◈", "color": BLUE, "voice": "Samantha",
        "desc": "Professional coder & problem solver",
        "accent": BLUE,
        "prompt": """You are Dev, a professional AI assistant in the terminal on a Mac.
Be concise, accurate, and practical. Use code blocks for code.
When user asks to open a website respond ONLY with: OPEN_URL: https://url.com
When asked to run a command respond ONLY with: RUN_CMD: the command
Only safe read-only commands. Never destructive."""
    },
    "mentor": {
        "name": "Mentor", "emoji": "◈", "color": TEAL, "voice": "Karen",
        "desc": "Patient teacher who explains everything",
        "accent": TEAL,
        "prompt": """You are Mentor, a patient encouraging teacher. Explain clearly with examples.
When asked to open URLs: OPEN_URL: https://url.com
When asked to run commands: RUN_CMD: command"""
    },
    "buddy": {
        "name": "Buddy", "emoji": "◈", "color": GREEN, "voice": "Daniel",
        "desc": "Friendly & casual coding friend",
        "accent": GREEN,
        "prompt": """You are Buddy, a fun friendly coding companion. Be casual, helpful, encouraging.
When asked to open URLs: OPEN_URL: https://url.com
When asked to run commands: RUN_CMD: command"""
    },
    "sage": {
        "name": "Sage", "emoji": "◈", "color": PURPLE, "voice": "Alex",
        "desc": "Deep thinker for architecture & design",
        "accent": PURPLE,
        "prompt": """You are Sage, a wise software architect. Think deeply about design and best practices.
When asked to open URLs: OPEN_URL: https://url.com
When asked to run commands: RUN_CMD: command"""
    },
    "turbo": {
        "name": "Turbo", "emoji": "◈", "color": YELLOW, "voice": "Fred",
        "desc": "Ultra fast, no fluff, just answers",
        "accent": YELLOW,
        "prompt": """You are Turbo, extremely fast and direct. Shortest correct answer only.
When asked to open URLs: OPEN_URL: https://url.com
When asked to run commands: RUN_CMD: command"""
    },
}

SITE_MAP = {
    "github":"https://github.com","youtube":"https://youtube.com","google":"https://google.com",
    "twitter":"https://twitter.com","x":"https://x.com","linkedin":"https://linkedin.com",
    "stackoverflow":"https://stackoverflow.com","reddit":"https://reddit.com",
    "gmail":"https://mail.google.com","drive":"https://drive.google.com",
    "notion":"https://notion.so","vercel":"https://vercel.com","netlify":"https://netlify.com",
    "replit":"https://replit.com","claude":"https://claude.ai","chatgpt":"https://chatgpt.com",
}

NEWS_CATEGORIES = {
    "1": ("Technology", "latest technology AI news today"),
    "2": ("Finance",    "finance stock market news today"),
    "3": ("Economy",    "economy economic news today"),
    "4": ("World",      "world news today top stories"),
    "5": ("India",      "India news today top stories"),
    "6": ("Sports",     "sports cricket IPL news today India"),
}

# ── Ocean Dark UI Helpers ─────────────────────────────────────────────────────
def strip_ansi(text):
    import re
    return re.sub(r'\033\[[0-9;]*m|\033\[38;2;[0-9;]*m', '', text)

def get_terminal_width():
    try: return os.get_terminal_size().columns
    except: return 100

def clear_screen(): os.system("clear")

def sep(w=None, char="━"):
    """Ocean Dark em-dash style separator"""
    if w is None: w = get_terminal_width()
    return DARK + char * w + RESET

def thin_sep(w=None):
    if w is None: w = get_terminal_width()
    return DARK + "─" * w + RESET

def ocean_box(lines, accent=None, w=None):
    """Draw an Ocean Dark styled box"""
    if accent is None: accent = BLUE
    if w is None: w = get_terminal_width()
    bw = min(w - 4, 64)
    pad = " " * max(0, (w - bw) // 2)
    print()
    print(pad + accent + "╭" + "─" * (bw - 2) + "╮" + RESET)
    for line in lines:
        raw = strip_ansi(line)
        space = bw - 2 - len(raw)
        print(pad + accent + "│" + RESET + line + " " * max(0, space) + accent + "│" + RESET)
    print(pad + accent + "╰" + "─" * (bw - 2) + "╯" + RESET)
    print()

def type_out(text, color=TEAL, delay=0.025):
    for ch in text:
        print(color + ch + RESET, end="", flush=True)
        time.sleep(delay)
    print()

def thinking_animation(stop_event):
    frames = [
        BLUE + "  ◈ " + MUTED + "thinking   " + RESET,
        BLUE + "  ◈ " + MUTED + "thinking ◦ " + RESET,
        BLUE + "  ◈ " + MUTED + "thinking ◦◦" + RESET,
        BLUE + "  ◈ " + MUTED + "thinking ◦◦◦"+RESET,
    ]
    i = 0
    while not stop_event.is_set():
        print(f"\r{frames[i % len(frames)]}", end="", flush=True)
        time.sleep(0.18)
        i += 1
    print("\r" + " " * 30 + "\r", end="", flush=True)

# ── Greetings ─────────────────────────────────────────────────────────────────
def get_greeting(user_name):
    h = datetime.now().hour
    tg = "Good morning" if 5<=h<12 else "Good afternoon" if 12<=h<17 else "Good evening" if 17<=h<21 else "Good night"
    return random.choice([
        f"{tg}, {user_name}! Ready to build something great?",
        f"Hey {user_name}! Great to see you again.",
        f"Welcome back, {user_name}! What are we creating today?",
        f"{tg}, {user_name}! I am here and ready.",
        f"Hello {user_name}! Let's make today productive.",
        f"{tg}, {user_name}! What can I help you with?",
    ])

def get_farewell(user_name):
    return random.choice([
        f"Goodbye, {user_name}! Have a great day!",
        f"See you later, {user_name}! Take care.",
        f"Bye {user_name}! Come back anytime.",
        f"Catch you later, {user_name}!",
        f"Goodbye {user_name}! Stay awesome.",
        f"Take care, {user_name}! Until next time.",
    ])

def get_datetime_line():
    now = datetime.now()
    return f"{now.strftime('%A, %B %d, %Y')}  ◦  {now.strftime('%I:%M %p')}"

# ── Persona helpers ───────────────────────────────────────────────────────────
def load_persona():
    if os.path.exists(PERSONA_FILE):
        try:
            with open(PERSONA_FILE) as f: return json.load(f).get("persona", "dev")
        except: return "dev"
    return "dev"

def save_persona(name):
    with open(PERSONA_FILE, "w") as f: json.dump({"persona": name}, f)

# ── Splash Screen ─────────────────────────────────────────────────────────────
def splash_screen(returning=False, msg_count=0, current_persona="dev", user_name="Friend"):
    clear_screen()
    w  = get_terminal_width()
    p  = PERSONAS[current_persona]
    ac = p["accent"]

    # top separator
    print()
    print(DARK + "━" * w + RESET)
    print()

    # logo
    logo = [
        "██████╗ ███████╗██╗   ██╗",
        "██╔══██╗██╔════╝██║   ██║",
        "██║  ██║█████╗  ██║   ██║",
        "██║  ██║██╔══╝  ╚██╗ ██╔╝",
        "██████╔╝███████╗ ╚████╔╝ ",
        "╚═════╝ ╚══════╝  ╚═══╝  ",
    ]
    for line in logo:
        print(ac + line.center(w) + RESET)

    print()
    print(MUTED + f"{'Professional AI Terminal Assistant'.center(w)}" + RESET)
    print(MUTED + f"{'Powered by Groq  ◦  llama-3.3-70b'.center(w)}" + RESET)
    print()
    print(DARK + "━" * w + RESET)
    print()

    # datetime + persona
    print(MUTED + get_datetime_line().center(w) + RESET)
    print()
    persona_line = f"{p['emoji']} {p['name']}  ◦  {p['desc']}"
    print(ac + persona_line.center(w) + RESET)
    print()
    print(DARK + "━" * w + RESET)
    print()

    # greeting
    greeting = get_greeting(user_name)
    g_pad = " " * max(0, (w - len(greeting)) // 2)
    type_out(g_pad + greeting, TEAL, 0.025)

    if returning:
        print(MUTED + f"  I remember {msg_count} past messages.".center(w) + RESET)

    print()
    print(DARK + "━" * w + RESET)
    print()

    # command menu — two columns
    items = [
        ("~  v",              "voice input"),
        ("~  search: x",      "web search"),
        ("~  open <site>",    "open website"),
        ("~  todo",           "to-do list"),
        ("~  git <cmd>",      "git helper"),
        ("~  persona",        "switch persona"),
        ("~  briefing",       "daily briefing"),
        ("~  read <file>",    "read & explain file"),
        ("~  city <name>",    "change city"),
        ("~  history",        "past chats"),
        ("~  clear memory",   "forget everything"),
        ("~  exit",           "quit"),
    ]
    col_w = max(len(strip_ansi(f"  {c}")) for c, _ in items) + 4
    mid   = len(items) // 2
    left  = items[:mid]
    right = items[mid:]
    pad   = " " * max(0, (w - col_w * 2 - 4) // 2)

    for i in range(max(len(left), len(right))):
        l_cmd, l_desc = left[i]  if i < len(left)  else ("", "")
        r_cmd, r_desc = right[i] if i < len(right) else ("", "")
        l = f"  {YELLOW}{l_cmd:<18}{RESET}{MUTED}{l_desc}{RESET}" if l_cmd else ""
        r = f"  {YELLOW}{r_cmd:<18}{RESET}{MUTED}{r_desc}{RESET}" if r_cmd else ""
        l_raw = f"  {l_cmd:<18}{l_desc}" if l_cmd else ""
        r_raw = f"  {r_cmd:<18}{r_desc}" if r_cmd else ""
        l_pad = " " * max(0, col_w - len(l_raw))
        print(pad + l + l_pad + r)

    print()
    print(DARK + "━" * w + RESET)
    print()

    # loading
    for i in range(5):
        bar = BLUE + "◈" * i + MUTED + "◦" * (4-i) + RESET
        print(f"\r  {bar}  {MUTED}loading...{RESET}", end="", flush=True)
        time.sleep(0.12)
    print(f"\r  {BLUE}◈◈◈◈{RESET}  {TEAL}ready!{RESET}          ")
    print()

    speak_wait(greeting, p["voice"])

# ── Farewell ──────────────────────────────────────────────────────────────────
def farewell(user_name, voice):
    msg = get_farewell(user_name)
    w   = get_terminal_width()
    print()
    print(DARK + "━" * w + RESET)
    print()
    type_out(" " * max(0, (w - len(msg)) // 2) + msg, TEAL, 0.035)
    print()
    print(DARK + "━" * w + RESET)
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
        return [{"title": r.get("title","")[:55], "body": r.get("body","")[:100], "source": r.get("source","")} for r in results]
    except: return []

def pick_news_category(voice):
    w   = get_terminal_width()
    ac  = BLUE
    bw  = min(w - 4, 62)
    pad = " " * max(0, (w - bw) // 2)
    print()
    print(pad + ac + "╭" + "─" * (bw-2) + "╮" + RESET)
    print(pad + ac + "│" + TEAL + "  Pick your news category".center(bw-2) + RESET + ac + "│" + RESET)
    print(pad + ac + "├" + "─" * (bw-2) + "┤" + RESET)
    for key, (name, _) in NEWS_CATEGORIES.items():
        row = f"  {YELLOW}{key}.{RESET}  {WHITE}{name}{RESET}"
        raw = f"  {key}.  {name}"
        sp  = bw - 2 - len(raw)
        print(pad + ac + "│" + RESET + row + " " * max(0, sp) + ac + "│" + RESET)
    print(pad + ac + "╰" + "─" * (bw-2) + "╯" + RESET)
    print()
    speak("What type of news would you like? Technology, Finance, Economy, World, India, or Sports?", voice)
    choice = input(BLUE + "  ◈ Pick 1-6 (Enter for India): " + RESET + WHITE).strip()
    print(RESET, end="")
    if choice in NEWS_CATEGORIES:
        name, query = NEWS_CATEGORIES[choice]
        speak(f"Getting {name} news.", voice)
        return name, query
    return "India", "India top news today"

def morning_briefing(voice, user_name, city, accent=BLUE):
    w   = get_terminal_width()
    ac  = accent
    bw  = min(w - 4, 64)
    pad = " " * max(0, (w - bw) // 2)
    now = datetime.now()

    category_name, news_query = pick_news_category(voice)

    weather = get_weather(city)
    news    = get_top_news(news_query)

    print()
    print(pad + ac + "╭" + "─" * (bw-2) + "╮" + RESET)

    def bline(content, a=ac, bwidth=bw):
        raw = strip_ansi(content)
        sp  = bwidth - 2 - len(raw)
        return pad + a + "│" + RESET + content + " " * max(0, sp) + a + "│" + RESET

    print(bline(f"  {TEAL}Daily Briefing{RESET}  {MUTED}◦{RESET}  {WHITE}{user_name}{RESET}"))
    print(pad + ac + "├" + "─" * (bw-2) + "┤" + RESET)
    print(bline(f"  {MUTED}Date{RESET}   {WHITE}{now.strftime('%A, %B %d, %Y')}{RESET}"))
    print(bline(f"  {MUTED}Time{RESET}   {WHITE}{now.strftime('%I:%M %p')}{RESET}"))
    print(pad + ac + "├" + "─" * (bw-2) + "┤" + RESET)
    print(bline(f"  {TEAL}Weather in {city}{RESET}"))
    print(bline(f"  {WHITE}{weather}{RESET}"))
    print(pad + ac + "├" + "─" * (bw-2) + "┤" + RESET)
    print(bline(f"  {TEAL}Top {category_name} News{RESET}"))
    print(pad + ac + "│" + " " * (bw-2) + "│" + RESET)

    if news:
        for i, item in enumerate(news[:3], 1):
            print(bline(f"  {YELLOW}{i}.{RESET} {WHITE}{item['title']}{RESET}"))
            for chunk in [item['body'][j:j+52] for j in range(0, len(item['body']), 52)]:
                print(bline(f"     {MUTED}{chunk.strip()}{RESET}"))
            print(bline(f"     {DARK}◦ {item['source']}{RESET}"))
            if i < 3:
                print(pad + ac + "│" + DARK + "╌" * (bw-2) + RESET + ac + "│" + RESET)
    else:
        print(bline(f"  {MUTED}News unavailable right now.{RESET}"))

    print(pad + ac + "╰" + "─" * (bw-2) + "╯" + RESET)
    print()

    speak_wait(f"Here is your briefing. Today is {now.strftime('%A %B %d')}. Weather in {city}: {weather}.", voice)
    if news:
        speak(f"Top {category_name} news: {news[0]['title']}.", voice)

# ── To-Do List ────────────────────────────────────────────────────────────────
def load_todos():
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE) as f: return json.load(f)
        except: return []
    return []

def save_todos(todos):
    with open(TODO_FILE, "w") as f: json.dump(todos, f, indent=2)

def show_todos(accent=BLUE):
    todos = load_todos()
    w     = get_terminal_width()
    ac    = accent
    bw    = min(w - 4, 62)
    pad   = " " * max(0, (w - bw) // 2)

    def bline(content):
        raw = strip_ansi(content)
        sp  = bw - 2 - len(raw)
        return pad + ac + "│" + RESET + content + " " * max(0, sp) + ac + "│" + RESET

    print()
    print(pad + ac + "╭" + "─" * (bw-2) + "╮" + RESET)
    print(bline(f"  {TEAL}To-Do List{RESET}"))
    print(pad + ac + "├" + "─" * (bw-2) + "┤" + RESET)

    if not todos:
        print(bline(f"  {MUTED}No tasks yet.  Type: todo add <task>{RESET}"))
    else:
        for i, t in enumerate(todos, 1):
            status = GREEN + "✓" + RESET if t["done"] else MUTED + "◦" + RESET
            date   = MUTED + f" ({t.get('date','')})" + RESET if t.get("date") else ""
            task   = (WHITE if not t["done"] else MUTED) + t['task'][:44] + RESET
            print(bline(f"  {status} {i}. {task}{date}"))

    print(pad + ac + "├" + "─" * (bw-2) + "┤" + RESET)
    done  = sum(1 for t in todos if t["done"])
    total = len(todos)
    bar_done = int((done / total * 20) if total else 0)
    bar  = GREEN + "█" * bar_done + DARK + "░" * (20 - bar_done) + RESET
    print(bline(f"  {bar}  {GREEN}{done}{RESET} done  {MUTED}◦{RESET}  {YELLOW}{total-done}{RESET} left"))
    print(pad + ac + "╰" + "─" * (bw-2) + "╯" + RESET)
    print()

def handle_todo(cmd, accent, voice):
    parts  = cmd.strip().split(" ", 2)
    action = parts[1].lower() if len(parts) > 1 else "list"
    todos  = load_todos()

    if action == "list" or len(parts) == 1:
        show_todos(accent)
    elif action == "add" and len(parts) == 3:
        task = parts[2]
        date = datetime.now().strftime("%b %d")
        todos.append({"task": task, "done": False, "date": date})
        save_todos(todos)
        print(GREEN + f"\n  ◦ Added: {task}\n" + RESET)
        speak(f"Task added: {task}", voice)
        show_todos(accent)
    elif action in ("done", "undone", "delete") and len(parts) == 3:
        try:
            idx = int(parts[2]) - 1
            if 0 <= idx < len(todos):
                if action == "done":
                    todos[idx]["done"] = True
                    save_todos(todos)
                    print(GREEN + f"\n  ✓ Done: {todos[idx]['task']}\n" + RESET)
                    speak(f"Marked done: {todos[idx]['task']}", voice)
                elif action == "undone":
                    todos[idx]["done"] = False
                    save_todos(todos)
                    print(YELLOW + f"\n  ◦ Unmarked: {todos[idx]['task']}\n" + RESET)
                elif action == "delete":
                    removed = todos.pop(idx)
                    save_todos(todos)
                    print(CORAL + f"\n  ✕ Deleted: {removed['task']}\n" + RESET)
                show_todos(accent)
            else:
                print(CORAL + f"  No task #{parts[2]}." + RESET)
        except ValueError:
            print(CORAL + f"  Use: todo {action} <number>" + RESET)
    elif action == "clear":
        confirm = input(YELLOW + "  Clear all tasks? (y/n): " + RESET).strip().lower()
        if confirm == "y":
            save_todos([])
            print(TEAL + "  All tasks cleared." + RESET)
    else:
        print()
        print(f"  {YELLOW}todo{RESET}               {MUTED}◦ show list{RESET}")
        print(f"  {YELLOW}todo add <task>{RESET}    {MUTED}◦ add task{RESET}")
        print(f"  {YELLOW}todo done <n>{RESET}      {MUTED}◦ mark done{RESET}")
        print(f"  {YELLOW}todo undone <n>{RESET}    {MUTED}◦ unmark done{RESET}")
        print(f"  {YELLOW}todo delete <n>{RESET}    {MUTED}◦ delete task{RESET}")
        print(f"  {YELLOW}todo clear{RESET}         {MUTED}◦ clear all{RESET}")
        print()

# ── Git Helper ────────────────────────────────────────────────────────────────
def git_helper(cmd, accent, voice, persona_key):
    parts  = cmd.strip().split(" ", 1)
    action = parts[1].lower() if len(parts) > 1 else "help"

    if action == "status":
        r = subprocess.run("git status --short", shell=True, capture_output=True, text=True)
        print()
        print(YELLOW + "  ◦ Git Status" + RESET)
        print(DARK + "  " + "─" * 40 + RESET)
        for line in (r.stdout.strip() or "Nothing to commit.").split("\n"):
            print(f"  {WHITE}{line}{RESET}")
        print()
    elif action == "log":
        r = subprocess.run("git log --oneline -5", shell=True, capture_output=True, text=True)
        print()
        print(YELLOW + "  ◦ Recent Commits" + RESET)
        print(DARK + "  " + "─" * 40 + RESET)
        for line in (r.stdout.strip() or "No commits yet.").split("\n"):
            print(f"  {WHITE}{line}{RESET}")
        print()
    elif action == "commit":
        r = subprocess.run("git status --short", shell=True, capture_output=True, text=True)
        status = r.stdout.strip()
        if not status:
            print(TEAL + "  ◦ Nothing to commit." + RESET); return
        print(MUTED + "\n  ◦ Generating commit message...\n" + RESET)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Write a short git commit message using conventional commits. Only output the message.\n\nGit status:\n{status}"}],
            max_tokens=60)
        msg = response.choices[0].message.content.strip().strip('"')
        print(BLUE + f"  ◈ Suggested: {WHITE}{msg}{RESET}")
        confirm = input(TEAL + f"\n  ◦ Use this? (y/n/edit): " + RESET + WHITE).strip().lower()
        print(RESET, end="")
        if confirm == "y":
            subprocess.run(f'git add -A && git commit -m "{msg}"', shell=True)
            print(GREEN + "  ✓ Committed!" + RESET)
            speak(f"Committed: {msg}", voice)
        elif confirm == "edit":
            custom = input(TEAL + "  ◦ Your message: " + RESET + WHITE).strip()
            print(RESET, end="")
            if custom:
                subprocess.run(f'git add -A && git commit -m "{custom}"', shell=True)
                print(GREEN + "  ✓ Committed!" + RESET)
        else:
            print(MUTED + "  Cancelled." + RESET)
    elif action == "push":
        r = subprocess.run("git push", shell=True, capture_output=True, text=True)
        print(WHITE + (r.stdout or r.stderr).strip() + RESET)
        speak("Push complete.", voice)
    elif action == "pull":
        r = subprocess.run("git pull", shell=True, capture_output=True, text=True)
        print(WHITE + (r.stdout or r.stderr).strip() + RESET)
        speak("Pull complete.", voice)
    elif action.startswith("explain "):
        git_cmd = action[8:].strip()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Explain 'git {git_cmd}' in 2 simple sentences. No markdown."}],
            max_tokens=100)
        explanation = response.choices[0].message.content.strip()
        print()
        print(DARK + "  " + "─" * 50 + RESET)
        print(f"  {WHITE}{explanation}{RESET}")
        print(DARK + "  " + "─" * 50 + RESET)
        print()
        speak(explanation, voice)
    else:
        print()
        print(f"  {YELLOW}git status{RESET}          {MUTED}◦ changed files{RESET}")
        print(f"  {YELLOW}git log{RESET}             {MUTED}◦ recent commits{RESET}")
        print(f"  {YELLOW}git commit{RESET}          {MUTED}◦ AI commit message{RESET}")
        print(f"  {YELLOW}git push / pull{RESET}     {MUTED}◦ push or pull{RESET}")
        print(f"  {YELLOW}git explain <cmd>{RESET}   {MUTED}◦ explain command{RESET}")
        print()

# ── Persona Menu ──────────────────────────────────────────────────────────────
def show_personas(current, user_name):
    keys = list(PERSONAS.keys())
    w    = get_terminal_width()
    bw   = min(w - 4, 62)
    pad  = " " * max(0, (w - bw) // 2)

    def bline(content, a=BLUE):
        raw = strip_ansi(content)
        sp  = bw - 2 - len(raw)
        return pad + a + "│" + RESET + content + " " * max(0, sp) + a + "│" + RESET

    print()
    print(pad + BLUE + "╭" + "─" * (bw-2) + "╮" + RESET)
    print(bline(f"  {TEAL}Switch AI Persona{RESET}"))
    print(pad + BLUE + "├" + "─" * (bw-2) + "┤" + RESET)

    for i, key in enumerate(keys, 1):
        p      = PERSONAS[key]
        active = GREEN + " ✓" + RESET if key == current else ""
        row    = f"  {p['accent']}{i}. {p['emoji']} {p['name']:<10}{RESET}{MUTED}{p['desc']:<28}{RESET}{GRAY}{p['voice']:<12}{RESET}{active}"
        print(bline(row))

    print(pad + BLUE + "╰" + "─" * (bw-2) + "╯" + RESET)
    print()

    while True:
        choice = input(BLUE + f"  ◈ Pick 1-{len(keys)} or Enter to cancel: " + RESET + WHITE).strip()
        print(RESET, end="")
        if choice == "": return current
        if choice.isdigit() and 1 <= int(choice) <= len(keys):
            chosen = keys[int(choice) - 1]
            p = PERSONAS[chosen]
            print()
            print(p["accent"] + f"  ◈ Switched to {p['name']} — {p['desc']}" + RESET)
            print(MUTED + f"  ◦ Voice: {p['voice']}\n" + RESET)
            speak(f"Hi {user_name}! I am {p['name']}. {p['desc']}.", p["voice"])
            return chosen
        print(CORAL + f"  Invalid. Enter 1-{len(keys)}." + RESET)

# ── Open URL ──────────────────────────────────────────────────────────────────
def open_url(url_or_name):
    name = url_or_name.lower().strip()
    for key, url in SITE_MAP.items():
        if key in name:
            print(GREEN + f"\n  ◦ Opening {key.capitalize()}...\n" + RESET)
            webbrowser.open(url)
            return f"Opened {key.capitalize()}"
    if name.startswith("http"):
        webbrowser.open(url_or_name)
        return f"Opened {url_or_name}"
    url = f"https://{name}" if "." in name else f"https://www.google.com/search?q={name}"
    webbrowser.open(url)
    return f"Opened {url}"

# ── History ───────────────────────────────────────────────────────────────────
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f: return json.load(f)
        except: return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w") as f: json.dump(history, f, indent=2)
    except: pass

def show_history():
    history = load_history()
    if not history:
        print(TEAL + "  ◦ No history yet." + RESET); return
    w = get_terminal_width()
    print()
    print(DARK + "  " + "─" * (w - 4) + RESET)
    print(TEAL + f"  ◈ Last {min(10, len(history))} messages" + RESET)
    print(DARK + "  " + "─" * (w - 4) + RESET)
    for msg in history[-10:]:
        t       = msg.get("time", "")
        role    = msg.get("role", "")
        content = msg.get("content", "")[:80]
        if role == "user":
            print(GREEN + f"  ~ [{t}] You: " + WHITE + f"{content}..." + RESET)
        else:
            print(BLUE + f"  ◈ [{t}] AI:  " + MUTED + f"{content}..." + RESET)
    print(DARK + "  " + "─" * (w - 4) + RESET)
    print()

def clear_history():
    if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
    conversation_history.clear()
    print(TEAL + "  ◦ Memory cleared." + RESET)

# ── Print Dev response ────────────────────────────────────────────────────────
def print_dev(text, color=BLUE):
    in_code = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_code = not in_code
            print(YELLOW + "  " + line + RESET)
        elif in_code:
            print(YELLOW + "  " + line + RESET)
        else:
            print(color + "  " + line + RESET)

def status_line(start_time, reply, persona_name, accent):
    elapsed = int((time.time() - start_time) * 1000)
    words   = len(reply.split())
    now     = datetime.now().strftime("%I:%M %p")
    w       = get_terminal_width()
    line    = f"  {accent}◈ {persona_name}{RESET}  {DARK}◦{RESET}  {MUTED}{elapsed}ms{RESET}  {DARK}◦{RESET}  {MUTED}{words} words{RESET}  {DARK}◦{RESET}  {MUTED}{now}{RESET}"
    print()
    print(DARK + "  " + "─" * (w - 4) + RESET)
    print(line)
    print(DARK + "  " + "─" * (w - 4) + RESET)
    print()

# ── File Reader ───────────────────────────────────────────────────────────────
def handle_file_read(cmd, p, voice, persona_key):
    parts = cmd.strip().split(" ", 1)
    if len(parts) < 2:
        print(TEAL + "  Usage: read <filename>" + RESET)
        print(MUTED + "  Example: read dev.py" + RESET)
        return
    filepath = os.path.expanduser(parts[1].strip())
    if not os.path.exists(filepath):
        local = os.path.join(os.getcwd(), parts[1].strip())
        if os.path.exists(local): filepath = local
        else:
            print(CORAL + f"  ✕ File not found: {parts[1]}" + RESET); return

    size = os.path.getsize(filepath)
    w    = get_terminal_width()
    print()
    print(DARK + "  " + "─" * (w-4) + RESET)
    print(BLUE + f"  ◈ Reading: {WHITE}{os.path.basename(filepath)}{RESET}  {MUTED}◦  {size} bytes{RESET}")
    print(DARK + "  " + "─" * (w-4) + RESET)
    print()

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        total_lines = len(lines)
        print(YELLOW + f"  ◦ Preview — first {min(20, total_lines)} lines" + RESET)
        print(DARK + "  " + "─" * 40 + RESET)
        for i, line in enumerate(lines[:20], 1):
            print(MUTED + f"  {i:3} " + RESET + WHITE + line.rstrip() + RESET)
        if total_lines > 20:
            print(MUTED + f"  ... {total_lines - 20} more lines" + RESET)
        print()
        print(BLUE + f"  ◈ {p['name']} analyzing..." + RESET)

        stop_event = threading.Event()
        anim_thread = threading.Thread(target=thinking_animation, args=(stop_event,))
        anim_thread.daemon = True
        anim_thread.start()

        file_content = "".join(lines[:200])
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": PERSONAS[persona_key]["prompt"]},
                    {"role": "user", "content": f"Analyze this file:\n1. What it does\n2. Key functions\n3. Issues or improvements\n\nFilename: {os.path.basename(filepath)}\n\n{file_content}"}
                ],
                max_tokens=1024)
        finally:
            stop_event.set()
            anim_thread.join()

        reply = response.choices[0].message.content
        print()
        print(DARK + "  " + "─" * (w-4) + RESET)
        print_dev(reply, p["accent"])
        print(DARK + "  " + "─" * (w-4) + RESET)
        print()
        speak(f"Analysis complete. {reply[:200]}", voice)
    except Exception as e:
        print(CORAL + f"  ✕ Error: {e}" + RESET)

# ── Web Search ────────────────────────────────────────────────────────────────
def web_search(query):
    print(MUTED + f"  ◦ Searching: {query}" + RESET)
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))
        if not results: return "No results found."
        return "".join(f"- {r['title']}\n  {r['body']}\n  Source: {r['href']}\n\n" for r in results)
    except Exception as e: return f"Search failed: {e}"

def should_search(user_input):
    keywords = ["search","look up","latest","news","today","current","price of",
                "weather","2024","2025","2026","what is","who is","when is","how much"]
    return any(k in user_input.lower() for k in keywords)

# ── Run Command ───────────────────────────────────────────────────────────────
def run_command(cmd):
    if any(d in cmd for d in DANGEROUS):
        return CORAL + "  ✕ Blocked: too dangerous." + RESET
    print(MUTED + f"  ◦ Running: {cmd}" + RESET)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return YELLOW + (result.stdout or result.stderr or "(no output)").strip() + RESET
    except subprocess.TimeoutExpired: return CORAL + "  ✕ Timed out." + RESET
    except Exception as e: return CORAL + f"  ✕ Error: {e}" + RESET

# ── Chat with streaming ───────────────────────────────────────────────────────
def chat_stream(user_input, persona_key, accent=BLUE, voice="Samantha"):
    import tty, termios, select

    stop_event  = threading.Event()
    start_time  = time.time()

    def watch_keys():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while not stop_event.is_set():
                r, _, _ = select.select([sys.stdin], [], [], 0.05)
                if r:
                    ch = sys.stdin.read(1)
                    if ch: stop_event.set(); break
        except: pass
        finally:
            try: termios.tcsetattr(fd, termios.TCSADRAIN, old)
            except: pass

    anim_thread = threading.Thread(target=thinking_animation, args=(stop_event,))
    anim_thread.daemon = True
    anim_thread.start()

    reply = ""
    try:
        extra = ""
        if should_search(user_input):
            results = web_search(user_input)
            extra = f"\n\nWeb search results:\n{results}\n\nUse these to answer."

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conversation_history.append({"role": "user", "content": user_input + extra})
        saved = load_history()
        saved.append({"role": "user", "content": user_input, "time": now})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": PERSONAS[persona_key]["prompt"]}] + conversation_history,
            max_tokens=1024,
            stream=True
        )

        # stop spinner, start streaming
        stop_event.set()
        anim_thread.join(timeout=0.3)
        print("\r" + " " * 30 + "\r", end="", flush=True)
        stop_event.clear()

        key_thread = threading.Thread(target=watch_keys)
        key_thread.daemon = True
        key_thread.start()

        in_code = False
        buffer  = ""

        for chunk in response:
            if stop_event.is_set():
                print(MUTED + "\n  ◦ stopped" + RESET)
                stop_speaking()
                break
            delta   = chunk.choices[0].delta.content or ""
            reply  += delta
            buffer += delta

            while " " in buffer or "\n" in buffer:
                idx_s = buffer.find(" ")
                idx_n = buffer.find("\n")
                if idx_n != -1 and (idx_s == -1 or idx_n < idx_s):
                    word   = buffer[:idx_n]
                    buffer = buffer[idx_n+1:]
                    if word:
                        if word.strip().startswith("```"):
                            in_code = not in_code
                            print(YELLOW + "  " + word + RESET, end="", flush=True)
                        else:
                            col = YELLOW if in_code else accent
                            print(col + word + RESET, end="", flush=True)
                    print()
                else:
                    word   = buffer[:idx_s]
                    buffer = buffer[idx_s+1:]
                    if word.strip().startswith("```"):
                        in_code = not in_code
                        print(YELLOW + "  " + word + " " + RESET, end="", flush=True)
                    else:
                        col = YELLOW if in_code else accent
                        print(col + word + " " + RESET, end="", flush=True)

        if buffer and not stop_event.is_set():
            col = YELLOW if in_code else accent
            print(col + "  " + buffer + RESET, end="", flush=True)
        print()

        stop_event.set()

        conversation_history.append({"role": "assistant", "content": reply})
        saved.append({"role": "assistant", "content": reply, "time": now})
        save_history(saved)

        if reply:
            speak(reply, voice)

    except Exception as e:
        stop_event.set()
        print(CORAL + f"  ✕ Error: {e}" + RESET)

    return reply, start_time

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global conversation_history

    user_name       = get_user_name()
    current_persona = load_persona()
    city            = get_city()
    saved           = load_history()

    if saved:
        conversation_history = [{"role": m["role"], "content": m["content"]} for m in saved[-20:]]
        splash_screen(returning=True, msg_count=len(conversation_history),
                      current_persona=current_persona, user_name=user_name)
    else:
        splash_screen(returning=False, current_persona=current_persona, user_name=user_name)

    p = PERSONAS[current_persona]
    morning_briefing(p["voice"], user_name, city, p["accent"])

    while True:
        try:
            p     = PERSONAS[current_persona]
            voice = p["voice"]
            ac    = p["accent"]
            w     = get_terminal_width()

            # user prompt — tilde style
            prompt = ac + "  ~ " + RESET + WHITE
            user_input = input(prompt).strip()
            print(RESET, end="")

            if not user_input: continue

            if user_input.lower() in ["exit", "quit", "bye"]:
                farewell(user_name, voice); break

            if user_input.lower() == "history":
                show_history(); continue

            if user_input.lower() == "clear memory":
                clear_history(); continue

            if user_input.lower() == "briefing":
                morning_briefing(voice, user_name, city, ac); continue

            if user_input.lower().startswith("city "):
                set_city(user_input[5:].strip(), voice)
                city = user_input[5:].strip(); continue

            if user_input.lower().startswith("todo"):
                handle_todo(user_input, ac, voice); continue

            if user_input.lower().startswith("git "):
                git_helper(user_input, ac, voice, current_persona); continue

            if user_input.lower() == "persona":
                current_persona = show_personas(current_persona, user_name)
                save_persona(current_persona); continue

            if user_input.lower().startswith("persona "):
                new_p = user_input[8:].strip().lower()
                if new_p in PERSONAS:
                    current_persona = new_p
                    save_persona(current_persona)
                    p2 = PERSONAS[current_persona]
                    print(p2["accent"] + f"\n  ◈ Switched to {p2['name']} — {p2['desc']}\n" + RESET)
                    speak(f"Hi {user_name}! I am {p2['name']}.", p2["voice"])
                else:
                    print(CORAL + f"  Unknown persona. Try: {', '.join(PERSONAS.keys())}" + RESET)
                continue

            if user_input.lower().startswith("open "):
                result = open_url(user_input[5:].strip())
                speak(result, voice); continue

            if user_input.lower().startswith("read "):
                handle_file_read(user_input, p, voice, current_persona); continue

            if user_input.lower() == "v":
                print(TEAL + "  ◦ Listening for 6 seconds... speak now!" + RESET)
                import scipy.io.wavfile as wav_mod
                sample_rate = 16000
                recording   = sd.rec(int(6*sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
                sd.wait()
                print(MUTED + "  ◦ Transcribing..." + RESET)
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    tmp_path = f.name
                    wav_mod.write(tmp_path, sample_rate, recording)
                try:
                    with open(tmp_path, "rb") as af:
                        t = client.audio.transcriptions.create(model="whisper-large-v3", file=af)
                    os.unlink(tmp_path)
                    spoken = t.text
                    if not spoken: continue
                    print(GREEN + f"  ~ You (voice): {WHITE}{spoken}{RESET}")
                    user_input = spoken
                except Exception as e:
                    print(CORAL + f"  ✕ {e}" + RESET); continue

            if user_input.lower().startswith("search:"):
                query   = user_input[7:].strip()
                results = web_search(query)
                conversation_history.append({"role": "user", "content": f"Summarize:\n{results}"})
                stop_event = threading.Event()
                anim = threading.Thread(target=thinking_animation, args=(stop_event,))
                anim.daemon = True
                anim.start()
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": p["prompt"]}] + conversation_history,
                    max_tokens=1024)
                stop_event.set(); anim.join()
                print("\r" + " " * 30 + "\r", end="", flush=True)
                reply = response.choices[0].message.content
                conversation_history.append({"role": "assistant", "content": reply})
                print()
                print(DARK + "  " + "─" * (w-4) + RESET)
                print(ac + f"  ◈ {p['name']}:" + RESET)
                print(DARK + "  " + "─" * (w-4) + RESET)
                print_dev(reply, ac)
                status_line(time.time(), reply, p["name"], ac)
                speak(reply, voice)
                continue

            # normal chat
            print()
            print(DARK + "  " + "─" * (w-4) + RESET)
            print(ac + f"  ◈ {p['name']}:" + RESET)
            print(DARK + "  " + "─" * (w-4) + RESET)

            reply, start_time = chat_stream(user_input, current_persona, accent=ac, voice=voice)

            open_line = next((l.strip().replace("OPEN_URL:","").strip() for l in reply.splitlines() if l.strip().startswith("OPEN_URL:")), None)
            run_line  = next((l.strip().replace("RUN_CMD:", "").strip() for l in reply.splitlines() if l.strip().startswith("RUN_CMD:")),  None)

            if open_line:
                result = open_url(open_line)
                print(GREEN + f"  ◦ {result}" + RESET)
                speak(result, voice)
            elif run_line:
                confirm = input(YELLOW + f"\n  ◦ Run this? '{run_line}' (y/n): " + RESET + WHITE).strip()
                print(RESET, end="")
                if confirm == "y":
                    print(run_command(run_line))
                    speak("Done.", voice)
                else:
                    print(MUTED + "  Cancelled." + RESET)

            status_line(start_time, reply, p["name"], ac)

        except KeyboardInterrupt:
            stop_speaking()
            farewell(user_name, voice)
            sys.exit(0)

if __name__ == "__main__":
    main()
