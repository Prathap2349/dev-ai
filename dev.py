#!/usr/bin/env python3
"""
Dev AI - Your Personal Terminal Assistant
GitHub: https://github.com/Prathap2349/Dev-Ai
"""

import os, sys, json, subprocess, tempfile, time, random, threading, requests, webbrowser
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from groq import Groq
from ddgs import DDGS
from datetime import datetime

# API Key
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

RESET="\033[0m"; CYAN="\033[1;36m"; GREEN="\033[1;32m"; BLUE="\033[1;34m"
YELLOW="\033[1;33m"; RED="\033[1;31m"; GRAY="\033[0;37m"; WHITE="\033[1;37m"
BOLD="\033[1m"; DIM="\033[2m"
DANGEROUS=["rm -rf","rmdir","mkfs","dd if","shutdown","reboot","chmod 777","sudo rm"]
BOX=56
conversation_history=[]

_tts_proc=None
_tts_lock=threading.Lock()

def speak(text,voice="Samantha"):
    global _tts_proc
    clean_lines=[]
    in_code=False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_code=not in_code; continue
        if not in_code:
            clean_lines.append(line)
    clean=" ".join(clean_lines).strip()
    if not clean: return
    with _tts_lock:
        if _tts_proc and _tts_proc.poll() is None:
            _tts_proc.kill(); _tts_proc.wait()
        try:
            _tts_proc=subprocess.Popen(["say","-v",voice,clean],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        except: pass

def speak_wait(text,voice="Samantha"):
    speak(text,voice)
    global _tts_proc
    if _tts_proc: _tts_proc.wait()

def stop_speaking():
    global _tts_proc
    with _tts_lock:
        if _tts_proc and _tts_proc.poll() is None:
            _tts_proc.kill(); _tts_proc.wait()

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f: return json.load(f)
        except: return {}
    return {}

def save_config(config):
    with open(CONFIG_FILE,"w") as f: json.dump(config,f,indent=2)

def get_user_name():
    config=load_config()
    if config.get("name"): return config["name"]
    print("\n"+CYAN+"  Welcome to Dev AI!"+RESET)
    print(GRAY+"  Lets get you set up.\n"+RESET)
    while True:
        name=input(GREEN+"  What is your name? "+RESET).strip()
        if name:
            config["name"]=name; save_config(config)
            print(CYAN+f"\n  Nice to meet you, {name}! Lets get started.\n"+RESET)
            return name
        print(RED+"  Please enter your name."+RESET)

def get_city():
    config=load_config()
    if config.get("city"): return config["city"]
    try:
        r=requests.get("https://ipapi.co/city/",timeout=5)
        city=r.text.strip()
        if city and len(city)<50:
            config["city"]=city; save_config(config)
            return city
    except: pass
    return "Chennai"

def set_city(new_city,voice):
    config=load_config()
    config["city"]=new_city; save_config(config)
    print(GREEN+f"  City updated to: {new_city}"+RESET)
    speak(f"City updated to {new_city}.",voice)

PERSONAS={
    "dev":{"name":"Dev","emoji":"⚡","color":"\033[1;36m","voice":"Samantha","desc":"Professional coder & problem solver",
        "prompt":"You are Dev, a professional AI assistant in the terminal on a Mac. Be concise and practical. Use code blocks for code. When user asks to open a website respond ONLY with: OPEN_URL: https://url.com — When asked to run a command respond ONLY with: RUN_CMD: the command — Only safe read-only commands."},
    "mentor":{"name":"Mentor","emoji":"🎓","color":"\033[1;33m","voice":"Karen","desc":"Patient teacher who explains everything",
        "prompt":"You are Mentor, a patient encouraging teacher. Explain clearly with examples. When asked to open URLs: OPEN_URL: https://url.com — When asked to run commands: RUN_CMD: command"},
    "buddy":{"name":"Buddy","emoji":"😎","color":"\033[1;32m","voice":"Daniel","desc":"Friendly & casual coding friend",
        "prompt":"You are Buddy, a fun friendly coding companion. Be casual, use humor, keep it helpful. When asked to open URLs: OPEN_URL: https://url.com — When asked to run commands: RUN_CMD: command"},
    "sage":{"name":"Sage","emoji":"🧠","color":"\033[1;35m","voice":"Alex","desc":"Deep thinker for architecture & design",
        "prompt":"You are Sage, a wise software architect. Think deeply about design and best practices. When asked to open URLs: OPEN_URL: https://url.com — When asked to run commands: RUN_CMD: command"},
    "turbo":{"name":"Turbo","emoji":"🚀","color":"\033[1;31m","voice":"Fred","desc":"Ultra fast, no fluff, just answers",
        "prompt":"You are Turbo, extremely fast and direct. Shortest correct answer only. When asked to open URLs: OPEN_URL: https://url.com — When asked to run commands: RUN_CMD: command"},
}

SITE_MAP={
    "github":"https://github.com","youtube":"https://youtube.com","google":"https://google.com",
    "twitter":"https://twitter.com","x":"https://x.com","linkedin":"https://linkedin.com",
    "stackoverflow":"https://stackoverflow.com","reddit":"https://reddit.com",
    "gmail":"https://mail.google.com","drive":"https://drive.google.com",
    "notion":"https://notion.so","vercel":"https://vercel.com","netlify":"https://netlify.com",
    "replit":"https://replit.com","claude":"https://claude.ai","chatgpt":"https://chatgpt.com",
}

NEWS_CATEGORIES={
    "1":("Technology","latest technology AI news today"),
    "2":("Finance","finance stock market news today"),
    "3":("Economy","economy economic news today"),
    "4":("World","world news today top stories"),
    "5":("India","India news today top stories"),
    "6":("Sports","sports cricket IPL news today India"),
}

def strip_ansi(t):
    import re
    return re.sub(r'\033\[[0-9;]*m','',t)

def box_line(content,color,box=BOX):
    raw=strip_ansi(content)
    pad=box-2-len(raw)
    return color+"║"+RESET+content+" "*max(0,pad)+color+"║"+RESET

def load_persona():
    if os.path.exists(PERSONA_FILE):
        try:
            with open(PERSONA_FILE) as f: return json.load(f).get("persona","dev")
        except: return "dev"
    return "dev"

def save_persona(name):
    with open(PERSONA_FILE,"w") as f: json.dump({"persona":name},f)

def get_terminal_width():
    try: return os.get_terminal_size().columns
    except: return 80

def get_greeting(n):
    h=datetime.now().hour
    tg="Good morning" if 5<=h<12 else "Good afternoon" if 12<=h<17 else "Good evening" if 17<=h<21 else "Good night"
    return random.choice([f"{tg}, {n}! Ready to get things done?",f"Hey {n}! Great to see you again.",
        f"Welcome back, {n}! What are we building today?",f"{tg}, {n}! I am here and ready.",
        f"Hello {n}! Lets make today productive.",f"{tg}, {n}! What can I help you with?"])

def get_farewell(n):
    return random.choice([f"Goodbye, {n}! Have a great day!",f"See you later, {n}! Take care.",
        f"Bye {n}! Come back anytime.",f"Catch you later, {n}!",
        f"Goodbye {n}! Stay awesome.",f"Take care, {n}! Until next time."])

def get_datetime_line():
    now=datetime.now()
    return f"{now.strftime('%A')}, {now.strftime('%B %d, %Y')}  |  {now.strftime('%I:%M %p')}"

def clear_screen(): os.system("clear")

def type_out(text,color=CYAN,delay=0.03):
    for ch in text:
        print(color+ch+RESET,end="",flush=True)
        time.sleep(delay)
    print()

def get_weather(city):
    try:
        r=requests.get(f"https://wttr.in/{city}?format=%C+%t+Humidity:%h+Wind:%w",timeout=6)
        return r.text.strip()
    except: return "Weather unavailable"

def get_top_news(query="top news India today"):
    try:
        with DDGS() as ddgs:
            results=list(ddgs.news(query,max_results=4))
        if not results: return []
        return [{"title":r.get("title","")[:55],"body":r.get("body","")[:100],"source":r.get("source","")} for r in results]
    except: return []

def pick_news_category(pc,voice):
    w=get_terminal_width()
    pad=" "*max(0,(w-BOX)//2)
    print()
    print(pad+pc+"╔"+"═"*(BOX-2)+"╗"+RESET)
    print(pad+box_line(f"  {YELLOW}Pick your news category:{RESET}",pc))
    print(pad+pc+"╠"+"═"*(BOX-2)+"╣"+RESET)
    for key,(name,_) in NEWS_CATEGORIES.items():
        print(pad+box_line(f"  {YELLOW}{key}.{RESET}  {name}",pc))
    print(pad+pc+"╚"+"═"*(BOX-2)+"╝"+RESET)
    print()
    speak("What type of news would you like? Technology, Finance, Economy, World, India, or Sports?",voice)
    choice=input(f"  {YELLOW}Pick 1-6 (or Enter for India):{RESET} ").strip()
    if choice in NEWS_CATEGORIES:
        name,query=NEWS_CATEGORIES[choice]
        speak(f"Getting {name} news.",voice)
        return name,query
    return "India","India top news today"

def morning_briefing(pc,voice,user_name,city):
    w=get_terminal_width()
    pad=" "*max(0,(w-BOX)//2)
    now=datetime.now()
    category_name,news_query=pick_news_category(pc,voice)
    print()
    print(pad+pc+"╔"+"═"*(BOX-2)+"╗"+RESET)
    print(pad+box_line(f"  {YELLOW}Daily Briefing — {user_name}!{RESET}",pc))
    print(pad+pc+"╠"+"═"*(BOX-2)+"╣"+RESET)
    print(pad+box_line(f"  {YELLOW}Date   {RESET}{now.strftime('%A, %B %d, %Y')}",pc))
    print(pad+box_line(f"  {YELLOW}Time   {RESET}{now.strftime('%I:%M %p')}",pc))
    print(pad+pc+"╠"+"═"*(BOX-2)+"╣"+RESET)
    print(pad+box_line(f"  {YELLOW}Weather in {city}{RESET}",pc))
    weather=get_weather(city)
    print(pad+box_line(f"  {weather}",pc))
    print(pad+pc+"╠"+"═"*(BOX-2)+"╣"+RESET)
    print(pad+box_line(f"  {YELLOW}Top {category_name} News{RESET}",pc))
    print(pad+pc+"║"+" "*(BOX-2)+"║"+RESET)
    news=get_top_news(news_query)
    if news:
        for i,item in enumerate(news[:3],1):
            print(pad+box_line(f"  {i}. {item['title']}",pc))
            for chunk in [item['body'][j:j+50] for j in range(0,len(item['body']),50)]:
                print(pad+box_line(f"     {chunk.strip()}",pc))
            print(pad+box_line(f"     Source: {item['source']}",pc))
            if i<3: print(pad+pc+"║"+DIM+"─"*(BOX-2)+RESET+pc+"║"+RESET)
    else:
        print(pad+box_line("  News unavailable right now.",pc))
    print(pad+pc+"╚"+"═"*(BOX-2)+"╝"+RESET)
    print()
    speak_wait(f"Here is your briefing. Today is {now.strftime('%A %B %d')}. Weather in {city}: {weather}.",voice)
    if news:
        speak(f"Top {category_name} news: {news[0]['title']}. {news[0]['body']}",voice)

def load_todos():
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE) as f: return json.load(f)
        except: return []
    return []

def save_todos(todos):
    with open(TODO_FILE,"w") as f: json.dump(todos,f,indent=2)

def show_todos(pc):
    todos=load_todos()
    w=get_terminal_width()
    pad=" "*max(0,(w-BOX)//2)
    print()
    print(pad+pc+"╔"+"═"*(BOX-2)+"╗"+RESET)
    print(pad+box_line(f"  {YELLOW}My To-Do List{RESET}",pc))
    print(pad+pc+"╠"+"═"*(BOX-2)+"╣"+RESET)
    if not todos:
        print(pad+box_line("  No tasks yet! Type: todo add <task>",pc))
    else:
        for i,t in enumerate(todos,1):
            status=GREEN+"✓"+RESET if t["done"] else GRAY+"○"+RESET
            date=GRAY+f" ({t.get('date','')})" +RESET if t.get("date") else ""
            print(pad+box_line(f"  {status} {i}. {t['task'][:40]}{date}",pc))
    print(pad+pc+"╠"+"═"*(BOX-2)+"╣"+RESET)
    done=sum(1 for t in todos if t["done"])
    total=len(todos)
    print(pad+box_line(f"  {GREEN}{done} done{RESET}  |  {YELLOW}{total-done} remaining{RESET}  |  {total} total",pc))
    print(pad+pc+"╚"+"═"*(BOX-2)+"╝"+RESET)
    print()

def handle_todo(cmd,pc,voice):
    parts=cmd.strip().split(" ",2)
    action=parts[1].lower() if len(parts)>1 else "list"
    todos=load_todos()
    if action=="list" or len(parts)==1:
        show_todos(pc)
    elif action=="add" and len(parts)==3:
        task=parts[2]
        date=datetime.now().strftime("%b %d")
        todos.append({"task":task,"done":False,"date":date})
        save_todos(todos)
        print(GREEN+f"\n  Added: {task}\n"+RESET)
        speak(f"Task added: {task}",voice)
        show_todos(pc)
    elif action=="done" and len(parts)==3:
        try:
            idx=int(parts[2])-1
            if 0<=idx<len(todos):
                todos[idx]["done"]=True; save_todos(todos)
                print(GREEN+f"\n  Done: {todos[idx]['task']}\n"+RESET)
                speak(f"Marked done: {todos[idx]['task']}",voice)
                show_todos(pc)
            else: print(RED+f"  No task number {parts[2]}."+RESET)
        except ValueError: print(RED+"  Use: todo done <number>"+RESET)
    elif action=="undone" and len(parts)==3:
        try:
            idx=int(parts[2])-1
            if 0<=idx<len(todos):
                todos[idx]["done"]=False; save_todos(todos)
                print(YELLOW+f"\n  Unmarked: {todos[idx]['task']}\n"+RESET)
                show_todos(pc)
            else: print(RED+f"  No task number {parts[2]}."+RESET)
        except ValueError: print(RED+"  Use: todo undone <number>"+RESET)
    elif action=="delete" and len(parts)==3:
        try:
            idx=int(parts[2])-1
            if 0<=idx<len(todos):
                removed=todos.pop(idx); save_todos(todos)
                print(RED+f"\n  Deleted: {removed['task']}\n"+RESET)
                show_todos(pc)
            else: print(RED+f"  No task number {parts[2]}."+RESET)
        except ValueError: print(RED+"  Use: todo delete <number>"+RESET)
    elif action=="clear":
        confirm=input(YELLOW+"  Clear all tasks? (y/n): "+RESET).strip().lower()
        if confirm=="y":
            save_todos([]); print(CYAN+"  All tasks cleared."+RESET)
    else:
        print(f"\n  {YELLOW}todo{RESET}               -> show list")
        print(f"  {YELLOW}todo add <task>{RESET}    -> add task")
        print(f"  {YELLOW}todo done <n>{RESET}      -> mark done")
        print(f"  {YELLOW}todo undone <n>{RESET}    -> unmark done")
        print(f"  {YELLOW}todo delete <n>{RESET}    -> delete task")
        print(f"  {YELLOW}todo clear{RESET}         -> clear all\n")

def git_helper(cmd,pc,voice,persona_key):
    parts=cmd.strip().split(" ",1)
    action=parts[1].lower() if len(parts)>1 else "help"
    if action=="status":
        r=subprocess.run("git status --short",shell=True,capture_output=True,text=True)
        print(YELLOW+"\n  Git Status:\n"+RESET)
        for line in (r.stdout.strip() or "Nothing to commit.").split("\n"): print(f"  {line}")
        print()
    elif action=="log":
        r=subprocess.run("git log --oneline -5",shell=True,capture_output=True,text=True)
        print(YELLOW+"\n  Recent Commits:\n"+RESET)
        for line in (r.stdout.strip() or "No commits yet.").split("\n"): print(f"  {line}")
        print()
    elif action=="commit":
        r=subprocess.run("git status --short",shell=True,capture_output=True,text=True)
        status=r.stdout.strip()
        if not status:
            print(CYAN+"  Nothing to commit."+RESET); return
        print(CYAN+"\n  Generating commit message..."+RESET)
        response=client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":f"Write a short git commit message using conventional commits. Only output the message.\n\nGit status:\n{status}"}],
            max_tokens=60)
        msg=response.choices[0].message.content.strip().strip('"')
        print(YELLOW+f"\n  Suggested: {msg}"+RESET)
        confirm=input(f"\n  {GREEN}Use this? (y/n/edit):{RESET} ").strip().lower()
        if confirm=="y":
            subprocess.run(f'git add -A && git commit -m "{msg}"',shell=True)
            print(GREEN+"  Committed!"+RESET); speak(f"Committed: {msg}",voice)
        elif confirm=="edit":
            custom=input(f"  {YELLOW}Your message:{RESET} ").strip()
            if custom:
                subprocess.run(f'git add -A && git commit -m "{custom}"',shell=True)
                print(GREEN+"  Committed!"+RESET)
        else: print(CYAN+"  Cancelled."+RESET)
    elif action=="push":
        r=subprocess.run("git push",shell=True,capture_output=True,text=True)
        print(YELLOW+(r.stdout or r.stderr).strip()+RESET); speak("Push complete.",voice)
    elif action=="pull":
        r=subprocess.run("git pull",shell=True,capture_output=True,text=True)
        print(YELLOW+(r.stdout or r.stderr).strip()+RESET); speak("Pull complete.",voice)
    elif action.startswith("explain "):
        git_cmd=action[8:].strip()
        response=client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":f"Explain 'git {git_cmd}' in 2 simple sentences. No markdown."}],
            max_tokens=100)
        explanation=response.choices[0].message.content.strip()
        print(BLUE+f"\n  {explanation}\n"+RESET); speak(explanation,voice)
    else:
        print(f"\n  {YELLOW}git status{RESET}          -> changed files")
        print(f"  {YELLOW}git log{RESET}             -> recent commits")
        print(f"  {YELLOW}git commit{RESET}          -> AI commit message")
        print(f"  {YELLOW}git push / pull{RESET}     -> push or pull")
        print(f"  {YELLOW}git explain <cmd>{RESET}   -> explain command\n")

def show_personas(current,user_name):
    keys=list(PERSONAS.keys())
    print()
    print(CYAN+"  ╔══════════════════════════════════════════════════╗"+RESET)
    print(CYAN+"  ║             Switch AI Persona                    ║"+RESET)
    print(CYAN+"  ╠══════════════════════════════════════════════════╣"+RESET)
    for i,key in enumerate(keys,1):
        p=PERSONAS[key]
        active=GREEN+" ✓"+RESET if key==current else "  "
        print(CYAN+"  ║"+RESET+YELLOW+f"  {i}. {p['emoji']}  {p['name']:<10}"+RESET+f"{p['desc']:<26}"+GRAY+f" {p['voice']:<10}"+RESET+active+CYAN+"║"+RESET)
    print(CYAN+"  ╚══════════════════════════════════════════════════╝"+RESET)
    print()
    while True:
        choice=input(f"  {YELLOW}Pick 1-{len(keys)} or Enter to cancel:{RESET} ").strip()
        if choice=="": return current
        if choice.isdigit() and 1<=int(choice)<=len(keys):
            chosen=keys[int(choice)-1]; p=PERSONAS[chosen]
            print(p["color"]+f"\n  Switched to {p['emoji']} {p['name']} — {p['desc']}"+RESET)
            print(GRAY+f"  Voice: {p['voice']}\n"+RESET)
            speak(f"Hi {user_name}! I am {p['name']}. {p['desc']}.",p["voice"])
            return chosen
        print(RED+f"  Invalid. Enter 1-{len(keys)}."+RESET)

def open_url(url_or_name):
    name=url_or_name.lower().strip()
    for key,url in SITE_MAP.items():
        if key in name:
            print(GREEN+f"  Opening {key.capitalize()}..."+RESET)
            webbrowser.open(url)
            return f"Opened {key.capitalize()}"
    if name.startswith("http"):
        webbrowser.open(url_or_name)
        return f"Opened {url_or_name}"
    url=f"https://{name}" if "." in name else f"https://www.google.com/search?q={name}"
    webbrowser.open(url)
    return f"Opened {url}"

def splash_screen(returning=False,msg_count=0,current_persona="dev",user_name="Friend"):
    clear_screen()
    w=get_terminal_width(); p=PERSONAS[current_persona]; pc=p["color"]
    logo=["██████╗ ███████╗██╗   ██╗","██╔══██╗██╔════╝██║   ██║","██║  ██║█████╗  ██║   ██║",
          "██║  ██║██╔══╝  ╚██╗ ██╔╝","██████╔╝███████╗ ╚████╔╝ ","╚═════╝ ╚══════╝  ╚═══╝  "]
    bw=58; pad=" "*max(0,(w-bw)//2)
    print()
    print(pad+pc+"╔"+"═"*(bw-2)+"╗"+RESET)
    print(pad+pc+"║"+" "*(bw-2)+"║"+RESET)
    for line in logo:
        print(pad+pc+"║"+WHITE+line.center(bw-2)+RESET+pc+"║"+RESET)
    print(pad+pc+"║"+" "*(bw-2)+"║"+RESET)
    print(pad+pc+"║"+GREEN+f"{p['emoji']}  {p['name']}  |  {p['desc']}".center(bw-2)+RESET+pc+"║"+RESET)
    print(pad+pc+"║"+DIM+GRAY+"Powered by Groq  |  llama-3.3-70b".center(bw-2)+RESET+pc+"║"+RESET)
    print(pad+pc+"║"+" "*(bw-2)+"║"+RESET)
    print(pad+pc+"╚"+"═"*(bw-2)+"╝"+RESET)
    print()
    print(GRAY+get_datetime_line().center(w)+RESET)
    print()
    time.sleep(0.2)
    greeting=get_greeting(user_name)
    g_pad=" "*max(0,(w-len(greeting))//2)
    type_out(g_pad+greeting,GREEN,0.03)
    if returning:
        print(DIM+GRAY+f"I remember {msg_count} past messages.".center(w)+RESET)
    print()
    mw=58; m_pad=" "*max(0,(w-mw)//2)
    print(m_pad+pc+"┌"+"─"*(mw-2)+"┐"+RESET)
    items=[("v","voice input (6 sec)"),("search: x","search the web"),("open <site>","open a website"),
           ("todo","manage to-do list"),("git <cmd>","git helper"),("persona","switch AI persona + voice"),
           ("briefing","daily news briefing"),("city <name>","change your city"),
           ("history","see past chats"),("clear memory","forget everything"),("exit","quit")]
    for cmd,desc in items:
        rr=" "*max(0,mw-2-len(cmd)-len(desc)-8)
        print(m_pad+pc+"│"+RESET+YELLOW+f"  {cmd:<18}"+RESET+f"->  {desc}"+rr+pc+"│"+RESET)
    print(m_pad+pc+"└"+"─"*(mw-2)+"┘"+RESET)
    print()
    for i in range(4):
        print(f"\r  {GRAY}Loading{'.'*i}   {RESET}",end="",flush=True)
        time.sleep(0.15)
    print(f"\r  {GREEN}Ready!{RESET}          ")
    print()
    speak_wait(greeting,p["voice"])

def farewell(user_name,voice):
    msg=get_farewell(user_name)
    print()
    w=get_terminal_width()
    pad=" "*max(0,(w-len(msg))//2)
    type_out(pad+msg,CYAN,0.04)
    speak_wait(msg,voice)
    print()

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

def show_history():
    history=load_history()
    if not history:
        print(CYAN+"  No history yet."+RESET); return
    print(CYAN+f"\n  Last {min(10,len(history))} messages"+RESET)
    for msg in history[-10:]:
        t=msg.get("time",""); role=msg.get("role",""); content=msg.get("content","")[:80]
        if role=="user": print(GREEN+f"  [{t}] You: {content}..."+RESET)
        else: print(BLUE+f"  [{t}] AI : {content}..."+RESET)
    print()

def clear_history():
    if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
    conversation_history.clear()
    print(CYAN+"  Memory cleared."+RESET)

def print_dev(text,color=BLUE):
    in_code=False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_code=not in_code; print(YELLOW+line+RESET)
        elif in_code: print(YELLOW+line+RESET)
        else: print(color+line+RESET)

def listen():
    print(CYAN+"  Listening for 6 seconds... speak now!"+RESET)
    sample_rate=16000
    recording=sd.rec(int(6*sample_rate),samplerate=sample_rate,channels=1,dtype="int16")
    sd.wait()
    print(CYAN+"  Transcribing..."+RESET)
    with tempfile.NamedTemporaryFile(suffix=".wav",delete=False) as f:
        tmp_path=f.name
        wav.write(tmp_path,sample_rate,recording)
    try:
        with open(tmp_path,"rb") as af:
            t=client.audio.transcriptions.create(model="whisper-large-v3",file=af)
        os.unlink(tmp_path)
        return t.text
    except Exception as e:
        print(RED+f"  Error: {e}"+RESET)
        return ""

def web_search(query):
    print(CYAN+f"  Searching: {query}"+RESET)
    try:
        with DDGS() as ddgs:
            results=list(ddgs.text(query,max_results=4))
        if not results: return "No results found."
        return "".join(f"- {r['title']}\n  {r['body']}\n  Source: {r['href']}\n\n" for r in results)
    except Exception as e: return f"Search failed: {e}"

def should_search(user_input):
    keywords=["search","look up","latest","news","today","current","price of","weather",
              "2024","2025","2026","what is","who is","when is","how much"]
    return any(k in user_input.lower() for k in keywords)

def run_command(cmd):
    if any(d in cmd for d in DANGEROUS):
        return RED+"  Blocked: too dangerous."+RESET
    print(CYAN+f"  Running: {cmd}"+RESET)
    try:
        result=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=15)
        return YELLOW+(result.stdout or result.stderr or "(no output)").strip()+RESET
    except subprocess.TimeoutExpired: return RED+"  Timed out."+RESET
    except Exception as e: return RED+f"  Error: {e}"+RESET

def chat(user_input,persona_key):
    extra=""
    if should_search(user_input):
        results=web_search(user_input)
        extra=f"\n\nWeb search results:\n{results}\n\nUse these to answer."
    now=datetime.now().strftime("%Y-%m-%d %H:%M")
    conversation_history.append({"role":"user","content":user_input+extra})
    saved=load_history()
    saved.append({"role":"user","content":user_input,"time":now})
    response=client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"system","content":PERSONAS[persona_key]["prompt"]}]+conversation_history,
        max_tokens=1024)
    reply=response.choices[0].message.content
    conversation_history.append({"role":"assistant","content":reply})
    saved.append({"role":"assistant","content":reply,"time":now})
    save_history(saved)
    return reply

def main():
    global conversation_history
    user_name=get_user_name()
    current_persona=load_persona()
    city=get_city()
    saved=load_history()
    if saved:
        conversation_history=[{"role":m["role"],"content":m["content"]} for m in saved[-20:]]
        splash_screen(returning=True,msg_count=len(conversation_history),current_persona=current_persona,user_name=user_name)
    else:
        splash_screen(returning=False,current_persona=current_persona,user_name=user_name)

    p=PERSONAS[current_persona]
    morning_briefing(p["color"],p["voice"],user_name,city)

    while True:
        try:
            p=PERSONAS[current_persona]
            voice=p["voice"]
            user_input=input(p["color"]+f"  {p['emoji']} You: "+RESET).strip()
            if not user_input: continue

            if user_input.lower() in ["exit","quit","bye"]:
                farewell(user_name,voice); break
            if user_input.lower()=="history":
                show_history(); continue
            if user_input.lower()=="clear memory":
                clear_history(); continue
            if user_input.lower()=="briefing":
                morning_briefing(p["color"],voice,user_name,city); continue
            if user_input.lower().startswith("city "):
                set_city(user_input[5:].strip(),voice)
                city=user_input[5:].strip(); continue
            if user_input.lower().startswith("todo"):
                handle_todo(user_input,p["color"],voice); continue
            if user_input.lower().startswith("git "):
                git_helper(user_input,p["color"],voice,current_persona); continue
            if user_input.lower()=="persona":
                current_persona=show_personas(current_persona,user_name)
                save_persona(current_persona); continue
            if user_input.lower().startswith("persona "):
                new_p=user_input[8:].strip().lower()
                if new_p in PERSONAS:
                    current_persona=new_p; save_persona(current_persona)
                    p2=PERSONAS[current_persona]
                    print(p2["color"]+f"\n  Switched to {p2['emoji']} {p2['name']}"+RESET)
                    speak(f"Hi {user_name}! I am {p2['name']}. {p2['desc']}.",p2["voice"])
                else:
                    print(RED+f"  Unknown persona. Try: {', '.join(PERSONAS.keys())}"+RESET)
                continue
            if user_input.lower().startswith("open "):
                result=open_url(user_input[5:].strip())
                speak(result,voice); continue
            if user_input.lower()=="v":
                spoken=listen()
                if not spoken: continue
                print(GREEN+f"  You (voice): {spoken}"+RESET)
                user_input=spoken
            if user_input.lower().startswith("search:"):
                query=user_input[7:].strip()
                results=web_search(query)
                conversation_history.append({"role":"user","content":f"Summarize:\n{results}"})
                response=client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"system","content":p["prompt"]}]+conversation_history,
                    max_tokens=1024)
                reply=response.choices[0].message.content
                conversation_history.append({"role":"assistant","content":reply})
                print(BOLD+f"\n  {p['emoji']} {p['name']}:"+RESET)
                print_dev(reply,p["color"]); print(); speak(reply,voice); continue

            print(BOLD+f"\n  {p['emoji']} {p['name']}:"+RESET)
            reply=chat(user_input,current_persona)

            open_line=next((l.strip().replace("OPEN_URL:","").strip() for l in reply.splitlines() if l.strip().startswith("OPEN_URL:")),None)
            run_line=next((l.strip().replace("RUN_CMD:","").strip() for l in reply.splitlines() if l.strip().startswith("RUN_CMD:")),None)

            if open_line:
                clean=reply.replace(f"OPEN_URL: {open_line}","").replace(f"OPEN_URL:{open_line}","").strip()
                if clean: print_dev(clean,p["color"])
                result=open_url(open_line)
                print(GREEN+f"  {result}"+RESET); speak(result,voice)
            elif run_line:
                clean=reply.replace(f"RUN_CMD: {run_line}","").replace(f"RUN_CMD:{run_line}","").strip()
                if clean: print_dev(clean,p["color"]); speak(clean,voice)
                confirm=input(YELLOW+f"\n  Run this? '{run_line}' (y/n): "+RESET).strip()
                if confirm=="y":
                    print(run_command(run_line)); speak("Done.",voice)
                else: print(CYAN+"  Cancelled."+RESET)
            else:
                print_dev(reply,p["color"]); speak(reply,voice)
            print()

        except KeyboardInterrupt:
            stop_speaking(); farewell(user_name,voice); sys.exit(0)

if __name__=="__main__":
    main()
