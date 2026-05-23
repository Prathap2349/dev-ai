# ⚡ Dev AI — Your Personal Terminal Assistant

A powerful AI assistant that lives in your Mac terminal. Powered by Groq and llama-3.3-70b.

```
╔══════════════════════════════════════════════════════╗
║                                                      ║
║        ██████╗ ███████╗██╗   ██╗                     ║
║        ██╔══██╗██╔════╝██║   ██║                     ║
║        ██║  ██║█████╗  ██║   ██║                     ║
║        ██║  ██║██╔══╝  ╚██╗ ██╔╝                     ║
║        ██████╔╝███████╗ ╚████╔╝                      ║
║        ╚═════╝ ╚══════╝  ╚═══╝                       ║
║                                                      ║
║        ⚡  Dev  |  Professional coder & solver        ║
║           Powered by Groq  |  llama-3.3-70b           ║
╚══════════════════════════════════════════════════════╝
```

---

## Features

- **5 AI Personas** — Each with a unique voice and personality
- **Voice output** — Dev speaks every response out loud
- **Voice input** — Speak your questions (type `v`)
- **Web search** — Real-time internet search built in
- **Morning briefing** — Weather + top news every morning
- **To-do list** — Add, check off, and manage tasks
- **Git helper** — AI writes your commit messages
- **Chat memory** — Remembers your past conversations
- **Run commands** — Ask Dev to run terminal commands safely
- **Personalized** — Asks your name on first run, never forgets it

---

## Personas

| Command | Persona | Voice | Style |
|---|---|---|---|
| `persona dev` | ⚡ Dev | Samantha | Professional coder |
| `persona mentor` | 🎓 Mentor | Karen | Patient teacher |
| `persona buddy` | 😎 Buddy | Daniel | Casual & fun |
| `persona sage` | 🧠 Sage | Alex | Deep architect |
| `persona turbo` | 🚀 Turbo | Fred | Ultra fast answers |

---

## Requirements

- Mac (macOS 10.15+)
- Python 3.10+
- A free Groq API key → [console.groq.com](https://console.groq.com)

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/dev-ai.git
cd dev-ai
```

### 2. Install dependencies

```bash
pip3 install groq ddgs requests sounddevice scipy numpy --break-system-packages
```

### 3. Get your Groq API key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free
3. Click **API Keys** → **Create API Key**
4. Copy your key

### 4. Set your API key

Add this to your `~/.zshrc`:

```bash
echo 'export GROQ_API_KEY="paste_your_key_here"' >> ~/.zshrc
source ~/.zshrc
```

> **Never share your API key publicly or commit it to GitHub!**

### 5. Create the `dev` shortcut

```bash
echo 'alias dev="python3 ~/dev-ai/dev.py"' >> ~/.zshrc
source ~/.zshrc
```

### 6. Run Dev!

```bash
dev
```

On first run, Dev will ask your name and remember it forever.

---

## Commands

| Command | What it does |
|---|---|
| `v` | Voice input — speak your question |
| `search: x` | Force a web search |
| `todo` | Show your to-do list |
| `todo add <task>` | Add a task |
| `todo done <n>` | Mark task as done |
| `todo delete <n>` | Delete a task |
| `git status` | Show git changes |
| `git commit` | AI writes your commit message |
| `git push` | Push to remote |
| `git explain <cmd>` | Explain any git command |
| `persona` | Switch AI persona interactively |
| `briefing` | Show morning briefing again |
| `history` | See past conversations |
| `clear memory` | Wipe all memory |
| `exit` | Quit Dev |

---

## Customization

Open `dev.py` and change these at the top:

```python
CITY = "Coimbatore"  # Change to your city for weather
```

To change the default persona, edit `~/.dev_persona.json`.

---

## Privacy

- Your API key is **never stored in the code** — it's read from your environment
- Chat history is saved locally at `~/.dev_history.json`
- Your name is saved locally at `~/.dev_config.json`
- Nothing is sent to any server except Groq (for AI) and wttr.in (for weather)

---

## Contributing

Pull requests welcome! Feel free to add new personas, features, or improvements.

---

## License

MIT License — free to use, modify, and share.

---

Made with ❤️ by the Dev AI community
