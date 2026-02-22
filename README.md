# Social Saver Bot

A WhatsApp-driven content bookmarking system with AI-powered enrichment and a searchable web dashboard.

Built for Hack the Thread — National Institute of Technology Karnataka (NITK), Surathkal.

The core problem: you save links on WhatsApp and never find them again. Social Saver Bot intercepts that behavior, processes every link through an AI pipeline, and surfaces it in a clean, searchable interface. No new app to install. No new habit to build. You already share links on WhatsApp — just send them to this number instead.

---

## Problem Statement

Social media content is ephemeral by design. Instagram Reels get buried. Twitter threads get lost. Blog articles sit forgotten in Saved Messages. The average person has no structured way to retrieve content they found valuable five minutes after they leave the app.

This project treats WhatsApp as the input layer — because that is already where links get shared — and builds a personal knowledge base on top of it automatically.

---

## How It Works

Send any URL to the bot's WhatsApp number. The system handles everything else:

1. Detects the platform from the URL (Instagram, YouTube, Twitter, Reddit, TikTok, LinkedIn, Pinterest, or any blog)
2. Scrapes the page for title, caption, and Open Graph image using BeautifulSoup
3. Passes the extracted data to a Groq-hosted LLM which classifies the content into one of 100 categories, writes a short hook summary, and pulls out 8-12 searchable tags
4. Saves everything to SQLite with the user's phone number attached
5. Replies on WhatsApp with the summary, category, and a link to the dashboard entry
6. Suggests related content from existing saves in the same reply

The web dashboard at `/dashboard` reflects saved content in real time.

---

## Architecture

```
User (WhatsApp)
      |
      | sends URL or command
      v
Twilio Webhook  -->  /whatsapp/webhook  (POST)
      |
      +---> Content Extractor
      |         - Platform detection via URL pattern matching
      |         - OG meta tag scraping (requests + BeautifulSoup4)
      |         - Article body extraction for blogs
      |
      +---> AI Processor (Groq API — llama-3.3-70b-versatile)
      |         - Category  : classifies into 1 of 100 predefined categories
      |         - Summary   : generates a 20-word hook sentence
      |         - Tags      : extracts 8-12 hyphenated, lowercase tags
      |
      +---> SQLite Database
      |         - saved_content (url, platform, title, caption,
      |           image_url, category, summary, tags, user_phone, timestamp)
      |         - collections (named folders for grouping saves)
      |         - Indexed on platform, category, user_phone, timestamp
      |
      +---> Flask Web Dashboard
                - /dashboard       : paginated grid with search and filter
                - /content/<id>    : detail view with platform embeds
                - /discover        : browse and filter all saves
                - /stats           : platform breakdown, category bars, activity heatmap
                - /collections     : folder-based organization
                - /export/csv      : one-click full export
```

---

## WhatsApp Commands

| Input | What happens |
|---|---|
| Any valid URL | Extracts, processes with AI, saves, replies with summary and related content |
| `surprise me` | Returns a random item from your save history |
| `motivate me` | Returns a random save from Motivation, Fitness, or Mindfulness categories |
| `teach me` | Returns a random save from Tech or Education categories |
| `feed me` | Returns a random save from Food or Recipes categories |
| `ask: <question>` | Searches your saves and answers your question using only your saved content as context |
| `my streak` | Shows your current saving streak, weekly count, and all-time best |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.0 |
| AI / LLM | Groq API — llama-3.3-70b-versatile |
| WhatsApp | Twilio Programmable Messaging (Sandbox) |
| Database | SQLite3 |
| Scraping | BeautifulSoup4, Requests |
| Frontend | Vanilla JS, CSS3, Font Awesome 6 |
| Scheduling | Python `schedule` library via background thread |

---

## Project Structure

```
social-saver-bot/
|
|-- app.py                  Flask app, all routes, WhatsApp webhook handler
|-- database.py             SQLite operations: CRUD, search, stats, collections, heatmap
|-- content_extractor.py    Platform detection, OG scraping, article extraction
|-- ai_processor.py         Groq wrapper: categorize, summarize, tag, RAG, digest
|-- config.py               Environment config, 100-category list, all LLM prompts
|-- sample_data.py          Demo data generator and database seeder
|-- main.js                 Frontend JS: form handling, delete, edit modal, toasts
|-- requirements.txt
|-- .env.example
|
|-- templates/
    |-- dashboard.html      Main content grid, search, filter, pagination
    |-- content.html        Single content view with platform embeds
    |-- discover.html       Browse mode
    |-- stats.html          Analytics: platform breakdown, category bars, heatmap
    |-- collections.html    Folder management
```

---

## Setup

### Prerequisites

- Python 3.11+
- A Groq API key (free tier is enough)
- A Twilio account with WhatsApp Sandbox enabled
- ngrok or any tunnel to expose localhost for the Twilio webhook

### Install

```bash
git clone https://github.com/yourname/social-saver-bot
cd social-saver-bot
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
```

Fill in your `.env`:

```
GROQ_API_KEY=your_groq_key_here
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1415xxxxxxx
SECRET_KEY=change_this_in_production
```

### Run

```bash
python sample_data.py          # Optional: seed with demo content
python app.py                  # Starts Flask at http://localhost:5000
```

### Connect WhatsApp

1. Run `ngrok http 5000` and copy the HTTPS URL
2. Twilio Console → Messaging → WhatsApp Sandbox Settings
3. Set webhook to: `https://your-ngrok-url.ngrok.io/whatsapp/webhook`
4. Send any message to your sandbox number from WhatsApp

Changing your ngrok URL only requires updating the webhook URL in Twilio. Nothing in the code is hardcoded to a domain — all URLs are built dynamically from `request.host_url`.

---

## Database Schema

```sql
CREATE TABLE saved_content (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    url         TEXT NOT NULL,
    platform    TEXT NOT NULL,
    title       TEXT,
    caption     TEXT,
    image_url   TEXT,
    category    TEXT,
    summary     TEXT,
    tags        TEXT,
    user_phone  TEXT,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE collections (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Indexes on `platform`, `category`, `user_phone`, and `timestamp` are created on first run. The schema auto-migrates on startup — if you have an older database without the `image_url` or `collection` columns, they get added automatically via `ALTER TABLE` without touching existing data.

---

## AI Pipeline

Three separate Groq calls happen for every saved URL. All prompts live in `config.py` so they're easy to tweak without touching the logic.

**Categorization** — The model gets the URL, title, and caption alongside the full list of 100 categories. It returns exactly one category name. The prompt includes worked examples to keep it from getting vague.

**Summarization** — The model writes a single sentence in under 20 words. The prompt explicitly tells it not to just rephrase the title — it has to add something: curiosity, urgency, or a clear statement of value. The output gets trimmed and stripped of any labels.

**Tag extraction** — Returns 8-12 comma-separated lowercase hyphenated tags covering the topic, subtopics, target audience, content format, and platform. The prompt bans generic tags like "post", "video", or "content" by name.

**RAG (ask: command)** — Your saves are searched with a full-text LIKE query. The top 5 results are formatted as context and passed to the model along with your question. The model is constrained to answer only from what's in those results — if it's not there, it says so. No embeddings, no vector DB — just structured context and a tight prompt.

---

## What's Included Beyond the Base Requirements

The hackathon spec asked for WhatsApp link saving, AI categorization and summarization, and a searchable card dashboard. This also ships:

- RAG question answering over saved content via WhatsApp (`ask:` command)
- Save streak tracking with current streak, best streak, and weekly count
- Collections / folder system for organizing saves

- Weekly digest with top categories delivered over WhatsApp
- GitHub-style activity heatmap on the stats page (last 365 days)
- CSV export of all saved content
- Inline edit and AI regeneration from the dashboard without a page reload
- Duplicate URL detection before saving

---

## Notes on Design Decisions

SQLite was chosen over Postgres or Firebase because it's zero-config and the database is just a file — easy to move, easy to demo, easy to seed. For a production deployment, swapping the database layer in `database.py` is straightforward since nothing else touches SQL directly.

The LLM provider is swappable. `config.py` has config blocks for Groq, Gemini, and MiniMax. Switching is a one-line change in `.env`.

The RAG implementation deliberately avoids vector embeddings. For a personal bookmark system where queries tend to use the same words as the saved content's tags and titles, keyword search is fast and accurate enough. Adding semantic search would require a vector store and an embedding model call per save — more infrastructure for marginal gain at this scale.

---

## License

MIT

---

Built For Hack the Thread — National Institute of Technology Karnataka (NITK), Surathkal.
