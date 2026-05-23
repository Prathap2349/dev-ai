#!/usr/bin/env python3
"""
Dev AI - Your Personal Terminal Assistant
GitHub: https://github.com/YOUR_USERNAME/dev-ai
"""

import os
import sys
import json
import subprocess
import tempfile
import time
import random
import threading
import requests
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from groq import Groq
from ddgs import DDGS
from datetime import datetime

# ── API Key ───────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    print("\033[1;31m\n  ERROR: GROQ_API_KEY not set!\033[0m")
    print("\033[1;33m  Run this first:\033[0m")
    print("  export GROQ_API_KEY='your_key_here'\n")
    print("  Or add it to ~/.zshrc to make it permanent.\n")
    sys.exit(1)

client = Groq(api_key=GROQ_API_KEY)

# ── Files ─────────────────────────────────────────────────────────────────────
HISTORY_FILE = os.path.expanduser("~/.dev_history.json")
PERSONA_FILE = os.path.expanduser("~/.dev_persona.json")
TODO_FILE    = os.path.expanduser("~/.dev_todos.json")
CONFIG_FILE  = os.path.expanduser("~/.dev_config.json")
CITY         = "Coimbatore"  # Change to your city

# ── Config (name setup) ───────────────────────────────────────────────────────
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def setup_name():
    """Ask for user's name on first run."""
    print("\n\033[1;36m  Welcome to Dev AI!\033[0m")
    print("\033[0;37m  Let's get you set up.\033[0m\n")
    while True:
        name = input("\033[1;32m  What is your name? \033[0m").strip()
        if name:
            config = {"name": name}
            save_config(config)
            print(f"\033[1;36m\n  Nice to meet you, {name}! Let's get started.\n\033[0m")
            return name
        print("\033[1;31m  Please enter your name.\033[0m")

def get_user_name():
    config = load_config()
    if config.get("name"):
        return config["name"]
    return setup_name()

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
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

def speak_wait(text, voice="Samantha"):
    speak(text, voice)
    global _tts_proc
    if _tts_proc:
        _tts_proc.wait()

def stop_speaking():
    global _tts_proc
    with _tts_lock:
        if _tts_proc and _tts_proc.poll() is None:
            _tts_proc.kill()
            _tts_proc.wait()

# ── Personas ──────────────────────────────────────────────────────────────────
PERSONAS = {
    "dev": {
        "name": "Dev",
        "emoji": "⚡",
        "color": "\033[1;36m",
        "voice": "Samantha",
        "desc": "Professional coder & problem solver",
        "prompt": """You are Dev, a professional and focused AI assistant in the terminal on a Mac.
Be concise, accurate, and practical. Use code blocks when sharing code.
Never waste words. Get straight to the point.
You have memory of past conversations with the user.
When the user asks you to run, execute, show, list, or check something on their Mac, respond with ONLY this on one line:
RUN_CMD: the command here
Only use RUN_CMD for safe read-only commands. Never run anything destructive."""
    },
    "mentor": {
        "name": "Mentor",
        "emoji": "🎓",
        "color": "\033[1;33m",
        "voice": "Karen",
        "desc": "Patient teacher who explains everything",
        "prompt": """You are Mentor, a patient and encouraging senior developer teacher.
You explain concepts clearly with examples and analogies.
Break down complex topics into simple steps.
Always encourage the user and celebrate their progress.
Use code examples with detailed comments.
You have memory of past conversations with the user.
When the user asks you to run commands, respond with ONLY: RUN_CMD: the command"""
    },
    "buddy": {
        "name": "Buddy",
        "emoji": "😎",
        "color": "\033[1;32m",
        "voice": "Daniel",
        "desc": "Friendly & casual coding friend",
        "prompt": """You are Buddy, a fun and friendly coding companion.
Be casual, use humor, and keep things light while still being helpful.
Use everyday language, the occasional emoji, and be encouraging.
You genuinely enjoy helping and get excited about cool solutions.
You have memory of past conversations with the user.
When the user asks you to run commands, respond with ONLY: RUN_CMD: the command"""
    },
    "sage": {
        "name": "Sage",
        "emoji": "🧠",
        "color": "\033[1;35m",
        "voice": "Alex",
        "desc": "Deep thinker for architecture & design",
        "prompt": """You are Sage, a wise and thoughtful software architect.
You think deeply about system design, architecture, best practices, and long-term solutions.
You consider tradeoffs, scalability, and maintainability in every answer.
You ask clarifying questions before giving big recommendations.
You have memory of past conversations with the user.
When the user asks you to run commands, respond with ONLY: RUN_CMD: the command"""
    },
    "turbo": {
        "name": "Turbo",
        "emoji": "🚀",
        "color": "\033[1;31m",
        "voice": "Fred",
        "desc": "Ultra fast, no fluff, just answers",
        "prompt": """You are Turbo, an extremely fast and direct AI assistant.
Give the shortest possible correct answer. No intros, no explanations unless asked.
One sentence max when possible. Code only when needed.
You have memory of past conversations with the user.
When the user asks you to run commands, respond with ONLY: RUN_CMD: the command"""
    },
}

# ── Colors ────────────────────────────────────────────────────────────────────
RESET   = "\033[0m"
CYAN    = "\033[1;36m"
GREEN   = "\033[1;32m"
BLUE    = "\033[1;34m"
YELLOW  = "\033[1;33m"
RED     = "\033[1;31m"
GRAY    = "\033[0;37m"
WHITE   = "\033[1;37m"
BOLD    = "\033[1m"
DIM     = "\033[2m"

DANGEROUS = ["rm -rf", "rmdir", "mkfs", "dd if", "shutdown", "reboot", "chmod 777", "sudo rm"]
BOX = 56

conversation_history = []

# ── Helpers ───────────────────────────────────────────────────────────────────
def strip_ansi(text):
    import re
    return re.sub(r'\033\[[0-9;]*m', '', text)

def box_line(content, color, box=BOX):
    raw = strip_ansi(content)
    pad = box - 2 - len(raw)
    return color + "║" + RESET + content + " " * max(0, pad) + color + "║" + RESET

def load_persona():
    if os.path.exists(PERSONA_FILE):
        try:
            with open(PERSONA_FILE) as f:
                return json.load(f).get("persona", "dev")
        except:
            return "dev"
    return "dev"

def save_persona(name):
    with open(PERSONA_FILE, "w") as f:
        json.dump({"persona": name}, f)

def get_terminal_width():
    try:
        return os.get_terminal_size().columns
    except:
        return 80

def get_greeting(user_name):
    hour = datetime.now().hour
    if 5 <= hour < 12:    tg = "Good morning"
    elif 12 <= hour < 17: tg = "Good afternoon"
    elif 17 <= hour < 21: tg = "Good evening"
    else:                 tg = "Good night"
    greetings = [
        f"{tg}, {user_name}! Ready to get things done?",
        f"Hey {user_name}! Great to see you again.",
        f"Welcome back, {user_name}! What are we building today?",
        f"{tg}, {user_name}! I am here and ready.",
        f"Hello {user_name}! Lets make today productive.",
        f"{tg}, {user_name}! What can I help you with?",
    ]
    return random.choice(greetings)

def get_farewell(user_name):
    farewells = [
        f"Goodbye, {user_name}! Have a great day!",
        f"See you later, {user_name}! Take care.",
        f"Bye {user_name}! Come back anytime.",
        f"Catch you later, {user_name}!",
        f"Goodbye {user_name}! Stay awesome.",
        f"See you soon, {user_name}! It was a pleasure.",
        f"Take care, {user_name}! Until next time.",
    ]
    return random.choice(farewells)

def get_datetime_line():
    now = datetime.now()
    return f"{now.strftime('%A')}, {now.strftime('%B %d, %Y')}  |  {now.strftime('%I:%M %p')}"

def clear_screen():
    os.system("clear")

def type_out(text, color=CYAN, delay=0.03):
    for ch in text:
        print(color + ch + RESET, end="", flush=True)
        time.sleep(delay)
    print()

# ── Weather & News ────────────────────────────────────────────────────────────
def get_weather():
    try:
        r = requests.get(f"https://wttr.in/{CITY}?format=%C+%t+Humidity:%h+Wind:%w", timeout=6)
        return r.text.strip()
    except:
        return "Weather unavailable"

def get_top_news():
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news("top news India today", max_results=4))
        if not results:
            return []
        return [{"title": r.get("title","")[:50], "body": r.get("body","")[:80], "source": r.get("source","")} for r in results]
    except:
        return []

def morning_briefing(persona_color, voice, user_name):
    hour = datetime.now().hour
    if not (5 <= hour < 12):
        return
    pc  = persona_color
    w   = get_terminal_width()
    pad = " " * max(0, (w - BOX) // 2)
    now = datetime.now()
    print()
    print(pad + pc + "╔" + "═" * (BOX-2) + "╗" + RESET)
    print(pad + box_line(f"  {YELLOW}Good Morning Briefing - {user_name}!{RESET}", pc))
    print(pad + pc + "╠" + "═" * (BOX-2) + "╣" + RESET)
    print(pad + box_line(f"  {YELLOW}Date   {RESET}{now.strftime('%A, %B %d, %Y')}", pc))
    print(pad + box_line(f"  {YELLOW}Time   {RESET}{now.strftime('%I:%M %p')}", pc))
    print(pad + pc + "╠" + "═" * (BOX-2) + "╣" + RESET)
    print(pad + box_line(f"  {YELLOW}Weather in {CITY}{RESET}", pc))
    weather = get_weather()
    print(pad + box_line(f"  {weather}", pc))
    print(pad + pc + "╠" + "═" * (BOX-2) + "╣" + RESET)
    print(pad + box_line(f"  {YELLOW}Top News Today{RESET}", pc))
    print(pad + pc + "║" + " " * (BOX-2) + "║" + RESET)
    news = get_top_news()
    if news:
        for i, item in enumerate(news[:3], 1):
            print(pad + box_line(f"  {i}. {item['title']}", pc))
            for chunk in [item['body'][j:j+50] for j in range(0, len(item['body']), 50)]:
                print(pad + box_line(f"     {chunk.strip()}", pc))
            print(pad + box_line(f"     Source: {item['source']}", pc))
            if i < 3:
                print(pad + pc + "║" + DIM + "─"*(BOX-2) + RESET + pc + "║" + RESET)
    else:
        print(pad + box_line("  News unavailable right now.", pc))
    print(pad + pc + "╚" + "═" * (BOX-2) + "╝" + RESET)
    print()
    speak_wait(f"Good morning {user_name}! Today is {now.strftime('%A %B %d')}. Weather: {weather}.", voice)
    if news:
        speak(f"Top news: {news[0]['title']}.", voice)

# ── To-Do List ────────────────────────────────────────────────────────────────
def load_todos():
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE) as f:
                return json.load(f)
        except:
            return []
    return []

def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)

def show_todos(pc):
    todos = load_todos()
    w   = get_terminal_width()
    pad = " " * max(0, (w - BOX) // 2)
    print()
    print(pad + pc + "╔" + "═"*(BOX-2) + "╗" + RESET)
    print(pad + box_line(f"  {YELLOW}My To-Do List{RESET}", pc))
    print(pad + pc + "╠" + "═"*(BOX-2) + "╣" + RESET)
    if not todos:
        print(pad + box_line("  No tasks yet! Type: todo add <task>", pc))
    else:
        for i, t in enumerate(todos, 1):
            status = GREEN + "✓" + RESET if t["done"] else GRAY + "○" + RESET
            print(pad + box_line(f"  {status} {i}. {t['task'][:44]}", pc))
    print(pad + pc + "╠" + "═"*(BOX-2) + "╣" + RESET)
    done  = sum(1 for t in todos if t["done"])
    total = len(todos)
    print(pad + box_line(f"  {GREEN}{done} done{RESET}  |  {YELLOW}{total-done} remaining{RESET}  |  {total} total", pc))
    print(pad + pc + "╚" + "═"*(BOX-2) + "╝" + RESET)
    print()

def handle_todo(cmd, pc, voice):
    todos  = load_todos()
    parts  = cmd.strip().split(" ", 2)
    action = parts[1].lower() if len(parts) > 1 else "list"
    if action == "list" or len(parts) == 1:
        show_todos(pc); return
    if action == "add" and len(parts) == 3:
        todos.append({"task": parts[2], "done": False})
        save_todos(todos)
        print(GREEN + f"  Added: {parts[2]}" + RESET)
        speak(f"Task added: {parts[2]}", voice)
    elif action == "done" and len(parts) == 3:
        try:
            idx = int(parts[2]) - 1
            if 0 <= idx < len(todos):
                todos[idx]["done"] = True
                save_todos(todos)
                print(GREEN + f"  Done: {todos[idx]['task']}" + RESET)
                speak(f"Marked done: {todos[idx]['task']}", voice)
        except:
            print(RED + "  Use: todo done <number>" + RESET)
    elif action == "undone" and len(parts) == 3:
        try:
            idx = int(parts[2]) - 1
            if 0 <= idx < len(todos):
                todos[idx]["done"] = False
                save_todos(todos)
                print(YELLOW + f"  Unmarked: {todos[idx]['task']}" + RESET)
        except:
            print(RED + "  Use: todo undone <number>" + RESET)
    elif action == "delete" and len(parts) == 3:
        try:
            idx = int(parts[2]) - 1
            if 0 <= idx < len(todos):
                removed = todos.pop(idx)
                save_todos(todos)
                print(RED + f"  Deleted: {removed['task']}" + RESET)
        except:
            print(RED + "  Use: todo delete <number>" + RESET)
    elif action == "clear":
        save_todos([])
        print(CYAN + "  All tasks cleared." + RESET)
    else:
        print(f"  {YELLOW}todo{RESET}               -> show list")
        print(f"  {YELLOW}todo add <task>{RESET}    -> add task")
        print(f"  {YELLOW}todo done <n>{RESET}      -> mark done")
        print(f"  {YELLOW}todo undone <n>{RESET}    -> unmark")
        print(f"  {YELLOW}todo delete <n>{RESET}    -> delete")
        print(f"  {YELLOW}todo clear{RESET}         -> clear all")

# ── Git Helper ────────────────────────────────────────────────────────────────
def git_helper(cmd, pc, voice, persona_key):
    parts  = cmd.strip().split(" ", 1)
    action = parts[1].lower() if len(parts) > 1 else "help"
    if action == "status":
        r = subprocess.run("git status --short", shell=True, capture_output=True, text=True)
        print(YELLOW + "\n  Git Status:\n" + RESET)
        for line in (r.stdout.strip() or "Nothing to commit.").split("\n"):
            print(f"  {line}")
        print()
    elif action == "log":
        r = subprocess.run("git log --oneline -5", shell=True, capture_output=True, text=True)
        print(YELLOW + "\n  Recent Commits:\n" + RESET)
        for line in (r.stdout.strip() or "No commits yet.").split("\n"):
            print(f"  {line}")
        print()
    elif action == "commit":
        r = subprocess.run("git status --short", shell=True, capture_output=True, text=True)
        status = r.stdout.strip()
        if not status:
            print(CYAN + "  Nothing to commit." + RESET); return
        print(CYAN + "\n  Generating commit message..." + RESET)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Write a short git commit message using conventional commits format. Only output the message.\n\nGit status:\n{status}"}],
            max_tokens=60,
        )
        msg = response.choices[0].message.content.strip().strip('"')
        print(YELLOW + f"\n  Suggested: {msg}" + RESET)
        confirm = input(f"\n  {GREEN}Use this message? (y/n/edit):{RESET} ").strip().lower()
        if confirm == "y":
            subprocess.run(f'git add -A && git commit -m "{msg}"', shell=True)
            print(GREEN + "  Committed!" + RESET)
            speak(f"Committed: {msg}", voice)
        elif confirm == "edit":
            custom = input(f"  {YELLOW}Your message:{RESET} ").strip()
            if custom:
                subprocess.run(f'git add -A && git commit -m "{custom}"', shell=True)
                print(GREEN + "  Committed!" + RESET)
                speak(f"Committed: {custom}", voice)
        else:
            print(CYAN + "  Cancelled." + RESET)
    elif action == "push":
        print(CYAN + "  Pushing..." + RESET)
        r = subprocess.run("git push", shell=True, capture_output=True, text=True)
        print(YELLOW + (r.stdout or r.stderr).strip() + RESET)
        speak("Push complete.", voice)
    elif action == "pull":
        print(CYAN + "  Pulling..." + RESET)
        r = subprocess.run("git pull", shell=True, capture_output=True, text=True)
        print(YELLOW + (r.stdout or r.stderr).strip() + RESET)
        speak("Pull complete.", voice)
    elif action.startswith("explain "):
        git_cmd = action[8:].strip()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Explain what 'git {git_cmd}' does in 2-3 simple sentences. No markdown."}],
            max_tokens=150,
        )
        explanation = response.choices[0].message.content.strip()
        print(BLUE + f"\n  {explanation}\n" + RESET)
        speak(explanation, voice)
    else:
        print(f"\n  {YELLOW}git status{RESET}          -> show changed files")
        print(f"  {YELLOW}git log{RESET}             -> recent commits")
        print(f"  {YELLOW}git commit{RESET}          -> AI writes commit message")
        print(f"  {YELLOW}git push{RESET}            -> push to remote")
        print(f"  {YELLOW}git pull{RESET}            -> pull from remote")
        print(f"  {YELLOW}git explain <cmd>{RESET}   -> explain any git command\n")

# ── Persona Menu ──────────────────────────────────────────────────────────────
def show_personas(current, user_name):
    keys = list(PERSONAS.keys())
    print()
    print(CYAN + "  ╔══════════════════════════════════════════════════╗" + RESET)
    print(CYAN + "  ║             Switch AI Persona                    ║" + RESET)
    print(CYAN + "  ╠══════════════════════════════════════════════════╣" + RESET)
    for i, key in enumerate(keys, 1):
        p      = PERSONAS[key]
        active = GREEN + " ✓" + RESET if key == current else "  "
        print(CYAN + "  ║" + RESET +
              YELLOW + f"  {i}. {p['emoji']}  {p['name']:<10}" + RESET +
              f"{p['desc']:<26}" +
              GRAY + f" {p['voice']:<12}" + RESET +
              active + CYAN + "║" + RESET)
    print(CYAN + "  ╚══════════════════════════════════════════════════╝" + RESET)
    print()
    while True:
        choice = input(f"  {YELLOW}Pick a number (1-{len(keys)}) or Enter to cancel:{RESET} ").strip()
        if choice == "":
            print(GRAY + "  Persona unchanged.\n" + RESET)
            return current
        if choice.isdigit() and 1 <= int(choice) <= len(keys):
            chosen = keys[int(choice) - 1]
            p = PERSONAS[chosen]
            print(p["color"] + f"\n  Switched to {p['emoji']} {p['name']} — {p['desc']}" + RESET)
            print(GRAY + f"  Voice: {p['voice']}\n" + RESET)
            speak(f"Hi {user_name}! I am {p['name']}. {p['desc']}.", p["voice"])
            return chosen
        print(RED + f"  Invalid. Enter 1-{len(keys)}." + RESET)

# ── Splash Screen ─────────────────────────────────────────────────────────────
def splash_screen(returning=False, msg_count=0, current_persona="dev", user_name="Friend"):
    clear_screen()
    w   = get_terminal_width()
    p   = PERSONAS[current_persona]
    pc  = p["color"]
    logo = [
        "██████╗ ███████╗██╗   ██╗",
        "██╔══██╗██╔════╝██║   ██║",
        "██║  ██║█████╗  ██║   ██║",
        "██║  ██║██╔══╝  ╚██╗ ██╔╝",
        "██████╔╝███████╗ ╚████╔╝ ",
        "╚═════╝ ╚══════╝  ╚═══╝  ",
    ]
    bw  = 58
    pad = " " * max(0, (w - bw) // 2)
    print()
    print(pad + pc + "╔" + "═"*(bw-2) + "╗" + RESET)
    print(pad + pc + "║" + " "*(bw-2) + "║" + RESET)
    for line in logo:
        print(pad + pc + "║" + WHITE + line.center(bw-2) + RESET + pc + "║" + RESET)
    print(pad + pc + "║" + " "*(bw-2) + "║" + RESET)
    tagline = f"{p['emoji']}  {p['name']}  |  {p['desc']}"
    print(pad + pc + "║" + GREEN + tagline.center(bw-2) + RESET + pc + "║" + RESET)
    model_line = "Powered by Groq  |  llama-3.3-70b"
    print(pad + pc + "║" + DIM + GRAY + model_line.center(bw-2) + RESET + pc + "║" + RESET)
    print(pad + pc + "║" + " "*(bw-2) + "║" + RESET)
    print(pad + pc + "╚" + "═"*(bw-2) + "╝" + RESET)
    print()
    dt = get_datetime_line()
    print(GRAY + dt.center(w) + RESET)
    print()
    time.sleep(0.2)
    greeting = get_greeting(user_name)
    g_pad = " " * max(0, (w - len(greeting)) // 2)
    type_out(g_pad + greeting, GREEN, 0.03)
    if returning:
        mem = f"I remember {msg_count} past messages."
        print(DIM + GRAY + mem.center(w) + RESET)
    print()
    mw    = 54
    m_pad = " " * max(0, (w - mw) // 2)
    print(m_pad + pc + "┌" + "─"*(mw-2) + "┐" + RESET)
    items = [
        ("v",            "voice input"),
        ("search: x",    "search the web"),
        ("todo",         "manage to-do list"),
        ("git <cmd>",    "git helper"),
        ("persona",      "switch AI persona + voice"),
        ("briefing",     "morning briefing"),
        ("history",      "see past chats"),
        ("clear memory", "forget everything"),
        ("exit",         "quit"),
    ]
    for cmd, desc in items:
        row_right = " " * max(0, mw - 2 - len(cmd) - len(desc) - 8)
        print(m_pad + pc + "│" + RESET + YELLOW + f"  {cmd:<16}" + RESET + f"->  {desc}" + row_right + pc + "│" + RESET)
    print(m_pad + pc + "└" + "─"*(mw-2) + "┘" + RESET)
    print()
    for i in range(4):
        print(f"\r  {GRAY}Loading{'.'*i}   {RESET}", end="", flush=True)
        time.sleep(0.15)
    print(f"\r  {GREEN}Ready!{RESET}          ")
    print()
    speak_wait(greeting, p["voice"])

# ── Farewell ──────────────────────────────────────────────────────────────────
def farewell(user_name, voice):
    msg = get_farewell(user_name)
    print()
    w   = get_terminal_width()
    pad = " " * max(0, (w - len(msg)) // 2)
    type_out(pad + msg, CYAN, 0.04)
    speak_wait(msg, voice)
    print()

# ── History ───────────────────────────────────────────────────────────────────
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except:
        pass

def show_history():
    history = load_history()
    if not history:
        print(CYAN + "  No history yet." + RESET); return
    print(CYAN + f"\n  Last {min(10, len(history))} messages" + RESET)
    for msg in history[-10:]:
        t       = msg.get("time", "")
        role    = msg.get("role", "")
        content = msg.get("content", "")[:80]
        if role == "user":
            print(GREEN + f"  [{t}] You: {content}..." + RESET)
        else:
            print(BLUE  + f"  [{t}] AI : {content}..." + RESET)
    print()

def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    conversation_history.clear()
    print(CYAN + "  Memory cleared." + RESET)

# ── Print Dev Response ────────────────────────────────────────────────────────
def print_dev(text, color=BLUE):
    in_code = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_code = not in_code
            print(YELLOW + line + RESET)
        elif in_code:
            print(YELLOW + line + RESET)
        else:
            print(color + line + RESET)

# ── Voice Input ───────────────────────────────────────────────────────────────
def listen():
    print(CYAN + "  Listening for 6 seconds... speak now!" + RESET)
    sample_rate = 16000
    recording   = sd.rec(int(6*sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    print(CYAN + "  Transcribing..." + RESET)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name
        wav.write(tmp_path, sample_rate, recording)
    with open(tmp_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3", file=audio_file)
    os.unlink(tmp_path)
    return transcription.text

# ── Web Search ────────────────────────────────────────────────────────────────
def web_search(query):
    print(CYAN + f"  Searching: {query}" + RESET)
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))
        if not results:
            return "No results found."
        return "".join(
            f"- {r['title']}\n  {r['body']}\n  Source: {r['href']}\n\n"
            for r in results
        )
    except Exception as e:
        return f"Search failed: {e}"

def should_search(user_input):
    keywords = ["search", "look up", "latest", "news", "today", "current",
                "price of", "weather", "2024", "2025", "2026"]
    return any(k in user_input.lower() for k in keywords)

# ── Run Command ───────────────────────────────────────────────────────────────
def run_command(cmd):
    if any(d in cmd for d in DANGEROUS):
        return RED + "  Blocked: too dangerous." + RESET
    print(CYAN + f"  Running: {cmd}" + RESET)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return YELLOW + (result.stdout or result.stderr or "(no output)").strip() + RESET
    except subprocess.TimeoutExpired:
        return RED + "  Timed out." + RESET
    except Exception as e:
        return RED + f"  Error: {e}" + RESET

# ── Chat ──────────────────────────────────────────────────────────────────────
def chat(user_input, persona_key):
    extra_context = ""
    if should_search(user_input):
        results = web_search(user_input)
        extra_context = f"\n\nWeb search results:\n{results}\n\nUse these to answer."
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conversation_history.append({"role": "user", "content": user_input + extra_context})
    saved = load_history()
    saved.append({"role": "user", "content": user_input, "time": now})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": PERSONAS[persona_key]["prompt"]}] + conversation_history,
        max_tokens=1024,
    )
    reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": reply})
    saved.append({"role": "assistant", "content": reply, "time": now})
    save_history(saved)
    return reply

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global conversation_history

    user_name       = get_user_name()
    current_persona = load_persona()
    saved           = load_history()

    if saved:
        conversation_history = [
            {"role": m["role"], "content": m["content"]} for m in saved[-20:]
        ]
        splash_screen(returning=True, msg_count=len(conversation_history),
                      current_persona=current_persona, user_name=user_name)
    else:
        splash_screen(returning=False, current_persona=current_persona, user_name=user_name)

    p = PERSONAS[current_persona]
    morning_briefing(p["color"], p["voice"], user_name)

    while True:
        try:
            p            = PERSONAS[current_persona]
            voice        = p["voice"]
            prompt_label = p["color"] + f"  {p['emoji']} You: " + RESET
            user_input   = input(prompt_label).strip()

            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "bye"]:
                farewell(user_name, voice)
                break
            if user_input.lower() == "history":
                show_history(); continue
            if user_input.lower() == "clear memory":
                clear_history(); continue
            if user_input.lower() == "briefing":
                morning_briefing(p["color"], voice, user_name); continue
            if user_input.lower().startswith("todo"):
                handle_todo(user_input, p["color"], voice); continue
            if user_input.lower().startswith("git "):
                git_helper(user_input, p["color"], voice, current_persona); continue
            if user_input.lower() == "persona":
                current_persona = show_personas(current_persona, user_name)
                save_persona(current_persona); continue
            if user_input.lower().startswith("persona "):
                new_p = user_input[8:].strip().lower()
                if new_p in PERSONAS:
                    current_persona = new_p
                    save_persona(current_persona)
                    p2 = PERSONAS[current_persona]
                    print(p2["color"] + f"\n  Switched to {p2['emoji']} {p2['name']}" + RESET)
                    print(GRAY + f"  Voice: {p2['voice']}\n" + RESET)
                    speak(f"Hi {user_name}! I am {p2['name']}. {p2['desc']}.", p2["voice"])
                else:
                    print(RED + f"  Unknown persona. Try: {', '.join(PERSONAS.keys())}" + RESET)
                continue
            if user_input.lower() == "v":
                spoken = listen()
                if not spoken:
                    continue
                print(GREEN + f"  You (voice): {spoken}" + RESET)
                user_input = spoken
            if user_input.lower().startswith("search:"):
                query   = user_input[7:].strip()
                results = web_search(query)
                conversation_history.append({"role": "user", "content": f"Summarize:\n{results}"})
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": p["prompt"]}] + conversation_history,
                    max_tokens=1024,
                )
                reply = response.choices[0].message.content
                conversation_history.append({"role": "assistant", "content": reply})
                print(BOLD + f"\n  {p['emoji']} {p['name']}:" + RESET)
                print_dev(reply, p["color"])
                print()
                speak(reply, voice)
                continue

            print(BOLD + f"\n  {p['emoji']} {p['name']}:" + RESET)
            reply = chat(user_input, current_persona)
            run_line = None
            for line in reply.splitlines():
                if line.strip().startswith("RUN_CMD:"):
                    run_line = line.strip().replace("RUN_CMD:", "").strip()
                    break
            if run_line:
                clean_reply = reply.replace(f"RUN_CMD: {run_line}", "").strip()
                print_dev(clean_reply, p["color"])
                speak(clean_reply, voice)
                confirm = input(YELLOW + f"\n  Run this command? '{run_line}' (y/n): " + RESET).strip()
                if confirm == "y":
                    print(run_command(run_line))
                    speak("Done.", voice)
                else:
                    print(CYAN + "  Cancelled." + RESET)
            else:
                print_dev(reply, p["color"])
                speak(reply, voice)
            print()

        except KeyboardInterrupt:
            stop_speaking()
            farewell(user_name, voice)
            sys.exit(0)

if __name__ == "__main__":
    main()
