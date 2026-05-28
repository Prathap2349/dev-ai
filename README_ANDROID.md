# Dev AI — Android Termux Edition v6.0

> Your personal AI terminal assistant for Android — powered by Groq + LLaMA 3.3

![Version](https://img.shields.io/badge/version-6.0-blue)
![Platform](https://img.shields.io/badge/platform-Android%20Termux-green)
![Python](https://img.shields.io/badge/python-3.8%2B-yellow)

---

## What's New in v6.0

| Feature | Command |
|---|---|
| ✦ Email Drafter | `email` |
| ✦ LinkedIn Post Writer | `linkedin` |
| ✦ Documentation Generator | `docgen` |
| ✦ Secure Encrypted Notes | `secu note` |

---

## Installation (Termux on Android)

### Step 1 — Update Termux
```bash
pkg update && pkg upgrade -y
```

### Step 2 — Install Python
```bash
pkg install python -y
```

### Step 3 — Install Dependencies
```bash
pip install groq requests
```

### Step 4 — Optional (clipboard & notifications)
```bash
pkg install termux-api -y
```
Also install **Termux:API** app from F-Droid.

### Step 5 — Get Free Groq API Key
1. Go to https://console.groq.com
2. Sign up free → API Keys → Create API Key
3. Copy your key

### Step 6 — Set API Key
```bash
echo "export GROQ_API_KEY='your_key_here'" >> ~/.bashrc && source ~/.bashrc
```

### Step 7 — Download the file
```bash
curl -o ~/devai.py https://raw.githubusercontent.com/Prathap2349/dev-ai/android/devai_android.py
```

### Step 8 — Run!
```bash
python ~/devai.py
```

### Optional Shortcut
```bash
echo "alias devai='python ~/devai.py'" >> ~/.bashrc && source ~/.bashrc
```
Now just type `devai` to launch!

---

## All Commands

### ✦ New v6.0 Features
| Command | Description |
|---|---|
| `email` | AI-powered email drafter with tone options |
| `linkedin` | LinkedIn post writer with 6 style options |
| `docgen` | Generate README, API docs, changelogs |
| `secu note` | PIN-protected encrypted notes |
| `secu note add <text>` | Add encrypted note |
| `secu note view <n>` | View a note |
| `secu note delete <n>` | Delete a note |
| `secu note pin` | Change PIN |

### AI & Chat
| Command | Description |
|---|---|
| Just type anything | Chat with AI |
| `search: <query>` | Web search + AI summary |
| `persona` | Switch AI personality |
| `history` | View past messages |
| `clear memory` | Reset memory |

### Tools
| Command | Description |
|---|---|
| `calc <expr>` | Calculator (supports sqrt, pi, etc.) |
| `convert <val> <from> <to>` | Unit converter |
| `passgen <length>` | Password generator |
| `b64 enc/dec <text>` | Base64 encode/decode |
| `myip` | Your IP and location |
| `netinfo` | Network info |
| `pomodoro` | 25min focus timer |

### Files & System
| Command | Description |
|---|---|
| `fm` or `files` | File manager |
| `read <filename>` | AI reads and explains file |
| `open <site>` | Open website |
| `copy <text>` | Copy to clipboard |
| `sysinfo` | CPU, RAM, battery |

### Productivity
| Command | Description |
|---|---|
| `todo` | To-do list |
| `todo add <task>` | Add task |
| `todo done <n>` | Mark done |
| `note` | Quick notes |
| `note add <text>` | Add note |
| `git status/log/commit/push/pull` | Git helper |
| `briefing` | Daily news + weather |

### Settings
| Command | Description |
|---|---|
| `theme <name>` | Switch theme |
| `city <name>` | Change weather city |
| `exit` | Quit |

---

## Themes
`ocean` `hacker` `amber` `frost` `nord` `rose` `dracula`

---

## AI Personas
| Persona | Style |
|---|---|
| `dev` | Professional coder (default) |
| `mentor` | Patient teacher |
| `buddy` | Friendly and casual |
| `sage` | Deep thinker / architect |
| `turbo` | Ultra fast, shortest answers |

---

## Differences from Mac Version

| Feature | Mac Version | Android Version |
|---|---|---|
| Search library | duckduckgo-search | Google News RSS (no Rust needed) |
| Clipboard | pyperclip | termux-clipboard-set |
| Notifications | desktop notify | termux-notification |
| Open URLs | webbrowser | termux-open-url |
| New features | v5.0 | v6.0 (email, linkedin, docgen, secure notes) |

---

## Requirements
- Android phone with Termux installed
- Python 3.8+
- `groq` and `requests` packages
- Groq API key (free at console.groq.com)

---

## License
MIT — Free to use and modify.

---

Made with ❤️ for Android developers
