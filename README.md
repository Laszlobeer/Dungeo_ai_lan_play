
# 🧝 RPG Adventure Game with AI Dungeon Master


![Project Banner](./yyqWt5B%20-%20Imgur.png)



⚔️ A text-based lan multiplayer RPG where players create characters and embark on an AI-generated adventure. Featuring an AI Dungeon Master powered by LLMs, immersive storytelling, and real-time voice narration!



---

## ✨ Features

- 🧙 **AI-Powered Storytelling** — Real-time narration powered by **Ollama LLMs**
- 🎙️ **Voice Narration** — Text-to-speech via **AllTalk TTS**
- 👥 **Locally only multiplayer Support** — 2–5 players, turn-based adventure
- 🎭 **Character Creation** — 20+ classes from 4 genres: *Fantasy*, *Sci-Fi*, *Cyberpunk*, *Post-Apocalyptic*
- 🌍 **Dynamic World System** — Permanent world state changes
- 💰 **Economy System** — Class-specific currencies and gear
- 💾 **Persistent Save/Load** — Save and continue your journey
- 📊 **World Tracker** — Tracks NPCs, factions, and consequences

---

## 🛠️ Installation

### ✅ Requirements

* Python 3.8+
* [🧠 Ollama](https://ollama.ai/)
* [🗣️ AllTalk TTS](https://github.com/erew123/alltalk_tts)

### 📥 Clone the Repository

```bash
git clone https://github.com/Laszlobeer/Dungeo_ai_lan_play.git
cd Dungeo_ai_lan_play
```

### 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

### ▶️ Run the Game

```bash
python main.py
```


If you want, I can add a full updated README with this included, just say!


---

## 🎮 Gameplay

### 🆕 Starting a New Game

1. Choose number of players (2–5)
2. Select a genre (Fantasy, Sci-Fi, Cyberpunk, Post-Apocalyptic)
3. Create your characters
4. Pick a starting location

### 💬 Commands

| Command         | Description                  |
| --------------- | ---------------------------- |
| `/?` or `/help` | Show help message            |
| `/save`         | Save the game                |
| `/load`         | Load a saved game            |
| `/redo`         | Regenerate last AI message   |
| `/state`        | Show world state             |
| `/players`      | List party members           |
| `/consequences` | View consequences of actions |
| `/change`       | Switch Ollama model          |
| `/count`        | Debug: count subarrays       |
| `/exit`         | Quit the game                |

---

## ⚙️ Configuration

### 🧠 Ollama Models

* Default: `llama3:instruct`
* Auto-detects installed models
* Use `/change` to switch mid-game

### 🧩 Custom Content

| File/Variable     | Customization                        |
| ----------------- | ------------------------------------ |
| `GENRE_LOCATIONS` | Add or edit locations                |
| `CLASS_ABILITIES` | Create new classes or edit abilities |
| `ROLE_STARTERS`   | Customize story starters             |
| `CURRENCY_MAP`    | Customize in-game economy            |

---

## 💻 System Requirements

### Minimum:

* 8GB RAM
* RTX gpu
* 4-core CPU
* Python 3.8+

### Recommended:

* 16GB+ RAM
* RTX gpu
* GPU for LLMs
* Dedicated sound card

---

## 🧯 Troubleshooting

### 🧠 Ollama Not Connecting

* Run `ollama serve`
* Check firewall settings

### 🔊 No Audio Playback

* Ensure AllTalk TTS is running on port 7851
* Check sound drivers

### 🤖 Model Load Fails

* Check model spelling
* Run `ollama list` to see installed models

> Logs are saved as: `rpg_adventure_YYYYMMDD_HHMMSS.log`

---

## 🤝 Contributing

We welcome contributions!

1. Fork the repo
2. Create a new branch
3. Submit a pull request
4. Include clear documentation for changes

---

## 📜 License

This project is licensed under the [MIT License](LICENSE)

---



---


