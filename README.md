# 📌 Social Saver Bot

> **Save anything from WhatsApp. Rediscover everything with AI.**

Social Saver Bot is a WhatsApp-first content bookmarking assistant. Send any link — Instagram reel, YouTube video, Twitter thread, blog post — and get back an AI-powered summary, category, and tags instantly. Everything lands in a beautiful web dashboard you can search, filter, and explore.

---

## 🌟 Why We Built This

We've all been there: you see a great article, save it to WhatsApp "Saved Messages", and forget about it forever. Bookmarks pile up. Notes get lost. The content you wanted to revisit never gets revisited.

**Social Saver Bot fixes this.**

It meets you where you already are — WhatsApp — and does the heavy lifting:
- Extracts the content automatically
- Summarizes it with AI so you remember *why* you saved it
- Categorizes and tags it for future discovery
- Resurfaces forgotten saves with a daily dose and smart commands

No new apps to install. No habits to build. Just send a link.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📱 **WhatsApp Integration** | Send any URL via WhatsApp and get an instant AI summary back |
| 🤖 **AI Processing** | Groq-powered categorization and tags, plus Gemini-powered visual summaries for reels and videos |
| 🔍 **Smart Search** | Full-text search across titles, captions, tags, and summaries |
| 📊 **Statistics Dashboard** | Track your saved content by platform, category, and time |
| 💡 **Chat With Your Saves** | Ask questions like *"what did I save about AI?"* via WhatsApp |
| 🌅 **Daily Dose** | Resurfaces a forgotten save every morning at 8AM |
| 🗂️ **Collections** | Organize saves into named folders |
| 📤 **CSV Export** | Download all your saves in one click |
| 🎲 **Discover Mode** | Browse random saves to rediscover forgotten gems |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER                                  │
│                    (WhatsApp)                                │
└──────────────────────────┬──────────────────────────────────┘
                           │ Sends URL or command
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    TWILIO WEBHOOK                            │
│              /whatsapp/webhook (POST)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌───────────────┐
    │  Content    │ │  AI         │ │   Commands    │
    │  Extractor  │ │  Processor  │ │   Handler     │
    │             │ │  (Groq)     │ │ "surprise me" │
    │  OG Tags    │ │             │ │ "teach me"    │
    │  Meta Data  │ │  Category   │ │ "my streak"   │
    │  Images     │ │  Summary    │ │ "ask: ..."    │
    └──────┬──────┘ │  Tags       │ └───────────────┘
           │        └──────┬──────┘
           └───────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    SQLite Database                           │
│         saved_content | collections | users                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Flask Web Dashboard                         │
│   Dashboard | Discover | Stats | Collections | Export       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 AI Pipeline

Every saved URL goes through a 3-step AI pipeline powered by **Groq** for text tasks and **Gemini** for multimodal summaries:

```
URL Submitted
     │
     ▼
[1] Content Extraction
     ├── Platform detection (Instagram, YouTube, Twitter, etc.)
     ├── OG meta tags scraping
     └── Article body extraction (for blogs)
     │
     ▼
[2] AI Processing (Groq + Gemini)
     ├── CATEGORY  → "Which of 100 categories fits best?"
     ├── SUMMARY   → "Describe what actually happens in the reel or video"
     └── TAGS      → "Extract 8–12 specific, searchable tags"
     │
     ▼
[3] Storage + WhatsApp Reply
     ├── Saved to SQLite with full metadata
     ├── Related content suggestions included in reply
     └── Dashboard link returned to user
```

---

## 💬 WhatsApp Commands

| Command | What it does |
|---|---|
| `<any URL>` | Save & summarize the content |
| `surprise me` | Get a random save from your history |
| `motivate me` | Get a random Motivation/Fitness save |
| `teach me` | Get a random Tech/Education save |
| `feed me` | Get a random Food/Recipe save |
| `ask: <question>` | Chat with your saves using RAG |
| `my streak` | See your saving streak and weekly stats |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourname/social-saver-bot
cd social-saver-bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Fill in: GROQ_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
```

### 3. Run

```bash
python sample_data.py   # Load demo content
python app.py           # Start server at http://localhost:5000
```

### 4. Connect WhatsApp

```
Twilio Console → Messaging → WhatsApp Settings
Webhook URL: https://your-ngrok-url.ngrok.io/whatsapp/webhook
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, Flask 3.0 |
| **AI** | Groq API (llama-3.3-70b-versatile) |
| **WhatsApp** | Twilio Programmable Messaging |
| **Database** | SQLite (zero-config, portable) |
| **Scraping** | BeautifulSoup4, Requests |
| **Frontend** | Vanilla JS, CSS3, Font Awesome |

---

## 📁 Project Structure

```
social-saver-bot/
├── app.py                 # Flask app + all routes + WhatsApp webhook
├── database.py            # All SQLite operations
├── content_extractor.py   # Platform-specific content extraction
├── ai_processor.py        # Groq AI: categorize, summarize, tag
├── config.py              # Config, prompts, platform patterns
├── sample_data.py         # Demo data generator
├── requirements.txt
├── .env.example
└── templates/
    ├── dashboard.html     # Main saved content grid
    ├── content.html       # Single content detail view
    ├── discover.html      # Random content discovery
    └── stats.html         # Usage statistics
```

---

## 🌐 Supported Platforms

`Instagram` · `Twitter / X` · `YouTube` · `TikTok` · `Facebook` · `LinkedIn` · `Reddit` · `Pinterest` · `Any Blog or Website`

---

## 📸 Screenshots

> Dashboard — all your saves in one place

![Dashboard](docs/screenshot-dashboard.png)

> WhatsApp — save a link, get an AI summary instantly

![WhatsApp](docs/screenshot-whatsapp.png)

> Stats — understand your reading habits

![Stats](docs/screenshot-stats.png)

---

## 🔮 Roadmap

- [x] WhatsApp link saving
- [x] AI categorization, summarization, tagging
- [x] Web dashboard with search & filter
- [x] Daily dose WhatsApp reminders
- [x] Chat with your saves (RAG via WhatsApp)
- [x] Collections / Folders
- [x] CSV Export
- [ ] Notion sync
- [ ] iOS / Android app

---

## 📄 License

MIT License — free to use, hack, and build upon.

---

## 👥 Team

Built with ❤️ for the MiniMax Hackathon 2025.

> *"The best bookmark is the one you actually revisit."*
