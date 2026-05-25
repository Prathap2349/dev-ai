# 🌊 Dev AI — Ocean Dark Edition

> A futuristic AI-powered terminal assistant for macOS built with Python, Groq, voice interaction, web search, Git tools, AI personas, and an Ocean Dark cyberpunk interface.

---

## ✨ Preview

```text
██████╗ ███████╗██╗   ██╗
██╔══██╗██╔════╝██║   ██║
██║  ██║█████╗  ██║   ██║
██║  ██║██╔══╝  ╚██╗ ██╔╝
██████╔╝███████╗ ╚████╔╝
╚═════╝ ╚══════╝  ╚═══╝

◈ Dev AI — Ocean Dark Edition
Powered by Groq • llama-3.3-70b
```

---

# 🚀 Features

## 🎭 Multiple AI Personas
Switch between different AI personalities instantly.

| Persona | Style |
|---|---|
| ⚡ Dev | Professional coding assistant |
| 🎓 Mentor | Patient teacher |
| 😎 Buddy | Friendly coding partner |
| 🧠 Sage | Deep software architect |
| 🚀 Turbo | Fast minimal answers |

---

## 🎤 Voice Features

- Voice input using Whisper
- AI speaks responses aloud
- Natural macOS voices
- Hands-free interaction

---

## 🌐 Built-in Web Search

Search the internet directly from the terminal:

```bash
search: latest AI news
```

---

## 📋 Smart To-Do System

Manage tasks directly inside Dev AI.

```bash
todo add Build portfolio website
todo done 1
```

---

## 🔧 Git Assistant

AI-powered Git helper:

- Generate commit messages
- Explain Git commands
- Push/Pull support
- Git status overview

---

## ☁️ Morning Briefing

Get:

- Weather updates
- Top news
- Sports headlines
- Technology news
- India news

directly inside your terminal.

---

## 🧠 Memory System

Dev AI remembers:

- Your name
- Chat history
- Preferred persona
- City for weather

All stored locally on your Mac.

---

# 🖥️ Requirements

- macOS (Apple Silicon / Intel)
- Python 3.10+
- Homebrew
- Groq API Key

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/Prathap2349/Dev-Ai.git
cd Dev-Ai
```

---

## 2. Install Homebrew (if needed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## 3. Install PortAudio

```bash
brew install portaudio
```

---

## 4. Install Python Packages

```bash
pip3 install groq requests sounddevice scipy numpy duckduckgo-search ddgs
```

---

## 5. Add Groq API Key

Open `.zshrc`

```bash
nano ~/.zshrc
```

Add:

```bash
export GROQ_API_KEY="your_api_key_here"
```

Reload terminal:

```bash
source ~/.zshrc
```

---

## 6. Create Dev Shortcut

```bash
echo 'alias dev="python3 ~/dev-ai/dev.py"' >> ~/.zshrc
source ~/.zshrc
```

---

## 7. Run Dev AI

```bash
dev
```

---

# 📚 Commands

| Command | Description |
|---|---|
| `v` | Voice input |
| `search: query` | Web search |
| `todo` | Show tasks |
| `todo add <task>` | Add task |
| `todo done <n>` | Complete task |
| `git status` | Show git changes |
| `git commit` | AI-generated commit message |
| `git push` | Push repository |
| `persona` | Switch AI persona |
| `briefing` | Daily weather + news |
| `history` | View conversation history |
| `read <file>` | AI explains a file |
| `open github` | Open websites |
| `exit` | Quit Dev AI |

---

# 🧠 Powered By

- Groq
- llama-3.3-70b
- Whisper
- Python
- DuckDuckGo Search
- macOS Terminal APIs

---

# 📁 Project Structure

```text
dev-ai/
│
├── dev.py
├── README.md
├── requirements.txt
│
├── ~/.dev_history.json
├── ~/.dev_persona.json
├── ~/.dev_todos.json
└── ~/.dev_config.json
```

---

# 🔒 Privacy

Your data stays local.

- Chat history stored locally
- Name stored locally
- No tracking
- API key stored in environment variables

Only Groq receives prompts for AI generation.

---

# 🛠️ Future Plans

- Linux support
- Windows support
- Plugin system
- Local LLM support
- VS Code integration
- Better UI animations
- Multi-agent workflows

---

# 🤝 Contributing

Pull requests are welcome.

Ideas:
- New personas
- New themes
- More Git tools
- Better voice system
- Plugins

---

# 📜 License

MIT License

Free to use, modify, and distribute.

---

# 👨‍💻 Author

### Prathap Senthilkumar

GitHub:
https://github.com/Prathap2349

---

# ⭐ Support

If you like this project:

- Star the repository
- Share it with friends
- Fork and improve it

---

## 🌊 Dev AI — Your Terminal. Your Assistant. Your Workflow.
