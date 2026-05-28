<div align="center">

```
██████╗ ███████╗██╗   ██╗
██╔══██╗██╔════╝██║   ██║
██║  ██║█████╗  ██║   ██║
██║  ██║██╔══╝  ╚██╗ ██╔╝
██████╔╝███████╗ ╚████╔╝
╚═════╝ ╚══════╝  ╚═══╝
```

# Dev AI — Your Personal Terminal Assistant

**Professional AI assistant that lives in your Mac terminal**

Powered by [Groq](https://console.groq.com) · llama-3.3-70b · 7 Themes · 5 Personas

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq-orange?style=flat-square)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey?style=flat-square&logo=apple)](https://apple.com)

</div>

---

## What is Dev AI?

Dev AI is a fully featured AI assistant that runs inside your Mac terminal. It greets you by name, reads the news, checks the weather, manages your tasks, helps with Git, and answers any question — all with voice output and beautiful terminal UI.

---

## Features

| Feature | Description |
|---|---|
| 🎨 **7 Themes** | Ocean Dark, Hacker Green, Amber Retro, Frost White, Nord Arctic, Rose Gold, Dracula |
| 🤖 **5 AI Personas** | Dev, Mentor, Buddy, Sage, Turbo — each with unique voice |
| 🔊 **Voice output** | Every reply spoken aloud via Mac's built-in voices |
| 🎙️ **Voice input** | Speak your questions (type `v`) |
| 🌐 **Web search** | Real-time internet search built in |
| 📰 **Morning briefing** | Weather + top news every time you open Dev |
| ✅ **To-do list** | Add, check off, delete tasks with progress bar |
| 🔧 **Git helper** | AI writes your commit messages |
| 📁 **File reader** | Ask Dev to read and explain any file |
| 💻 **System monitor** | CPU, memory, disk, battery at a glance |
| 🧠 **Memory** | Remembers your past conversations |
| 🌍 **Auto city detect** | Automatically detects your city for weather |
| 🔒 **Safe** | API key never stored in code |

---

## Themes Preview

```
theme ocean    →  🌊 Ocean Dark     deep navy + blue purple + teal
theme hacker   →  💚 Hacker Green   pure black + bright matrix green
theme amber    →  🟡 Amber Retro    dark brown + warm amber CRT style
theme frost    →  ❄️  Frost White    clean white + navy + blue accents
theme nord     →  🔵 Nord Arctic    dark blue-grey + teal + soft white
theme rose     →  🌹 Rose Gold      dark charcoal + rose pink + gold
theme dracula  →  🧛 Dracula        dark purple + bright purple + pink
```

---

## Personas

| Command | Name | Voice | Style |
|---|---|---|---|
| `persona dev` | ⚡ Dev | Samantha | Professional coder |
| `persona mentor` | 🎓 Mentor | Karen | Patient teacher |
| `persona buddy` | 😎 Buddy | Daniel | Casual & fun |
| `persona sage` | 🧠 Sage | Alex | Deep architect |
| `persona turbo` | 🚀 Turbo | Fred | Ultra fast answers |

---

## Requirements

- **Mac** (macOS 10.15 or later)
- **Python 3.10+**
- **Free Groq API key** → [console.groq.com](https://console.groq.com)

---

## Setup Guide

### Step 1 — Clone the repo

```bash
git clone https://github.com/Prathap2349/Dev-Ai.git
cd Dev-Ai
```

### Step 2 — Install dependencies

```bash
pip3 install groq ddgs requests sounddevice scipy numpy --break-system-packages
```

### Step 3 — Get your free Groq API key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free
3. Click **API Keys** → **Create API Key**
4. Copy your key (starts with `gsk_...`)

### Step 4 — Set your API key

```bash
echo 'export GROQ_API_KEY="paste_your_key_here"' >> ~/.zshrc
source ~/.zshrc
```

> ⚠️ **Never share your API key or commit it to GitHub!**

### Step 5 — Create the shortcut

```bash
echo 'alias dev="python3 ~/Dev-Ai/dev.py"' >> ~/.zshrc
source ~/.zshrc
```

### Step 6 — Run Dev!

```bash
dev
```

Dev will ask your name on first run and remember it forever. 🎉

---

## How to change API key

```bash
nano ~/.zshrc
```

Find and update the line:
```
export GROQ_API_KEY="your_new_key_here"
```

Save with **CTRL+X → Y → Enter** then:

```bash
source ~/.zshrc
```

---

## All Commands

### Chat & Navigation
| Command | What it does |
|---|---|
| `v` | Voice input — speak your question |
| `search: x` | Force a web search |
| `open github` | Open any website in browser |
| `history` | See past conversations |
| `clear memory` | Wipe all chat memory |
| `exit` | Quit Dev |

### Themes & Personas
| Command | What it does |
|---|---|
| `theme` | Show all themes |
| `theme dracula` | Switch to Dracula theme |
| `persona` | Show all personas |
| `persona buddy` | Switch to Buddy persona |

### Tools
| Command | What it does |
|---|---|
| `todo` | Show your to-do list |
| `todo add <task>` | Add a task |
| `todo done <n>` | Mark task as done |
| `todo delete <n>` | Delete a task |
| `todo clear` | Clear all tasks |
| `briefing` | Show daily news briefing |
| `sysinfo` | CPU, memory, disk, battery |
| `city Mumbai` | Change your city |
| `read dev.py` | Read and explain any file |

### Git Helper
| Command | What it does |
|---|---|
| `git status` | Show changed files |
| `git commit` | AI writes your commit message |
| `git push` | Push to remote |
| `git pull` | Pull from remote |
| `git log` | Recent commits |
| `git explain rebase` | Explain any git command |

---

## File Storage

Dev saves everything locally on your Mac:

| File | What it stores | Size |
|---|---|---|
| `~/.dev_history.json` | Chat history | ~1-5 MB per month |
| `~/.dev_config.json` | Name, city, theme | < 1 KB |
| `~/.dev_persona.json` | Current persona | < 1 KB |
| `~/.dev_todos.json` | Your tasks | < 10 KB |

---

## Privacy

- ✅ API key stored in your shell config — never in code
- ✅ Chat history saved locally only
- ✅ Nothing shared except Groq API calls (for AI) and wttr.in (for weather)
- ✅ No tracking, no analytics, no ads

---

## Contributing

Pull requests are welcome! Feel free to:
- Add new themes
- Add new personas
- Add new features
- Fix bugs

---

## License

MIT License — free to use, modify, and share.

---

<div align="center">

Made with ❤️ by [Prathap](https://github.com/Prathap2349)

⭐ Star this repo if you find it useful!

</div>
