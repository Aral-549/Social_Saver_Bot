# 📌 Social Saver Bot

> **Save anything from WhatsApp. Rediscover everything with AI.**

Social Saver Bot is a WhatsApp-first content bookmarking assistant powered by advanced AI. Send any link — Instagram reel, YouTube video, Twitter thread, blog post — and get back an AI-powered summary with intelligent categorization and searchable tags. Everything lands in a beautiful web dashboard where you can search, filter, and rediscover your saves.



---

##  Why This Exists

We've all been there: you see a great article, save it to WhatsApp "Saved Messages," and forget about it forever. Bookmarks pile up. Notes get lost. The content you wanted to revisit never gets revisited.

**Social Saver Bot fixes this.**

It meets you where you already are — WhatsApp — and does the heavy lifting:
- Extracts content automatically with fallback strategies for difficult platforms
- Summarizes with AI so you remember *why* you saved it
- Categorizes into 100+ intelligent categories
- Generates searchable tags for future discovery
- Provides detailed video analysis for reels and short-form content
- Tracks extraction status so you know exactly what worked and what didn't

No new apps to install. No habits to build. Just send a link.

---

##  Features

### Core Functionality
| Feature | Description |
|---------|-------------|
| 📱 **WhatsApp Integration** | Send any URL via WhatsApp and get an instant AI summary back |
| 🤖 **Dual AI Processing** | Groq for text categorization/tagging + Gemini for video understanding |
| 🎬 **Video Analysis** | Detailed multi-sentence summaries for reels and short videos |
| 📊 **Smart Extraction** | Two-tier extraction (meta tags + yt-dlp fallback) with authenticated scraping support |
| 🔍 **Full-Text Search** | Search across titles, captions, tags, summaries, and URLs |
| 📈 **Status Tracking** | Know exactly why extraction succeeded or failed (login required, rate limited, etc.) |
| 💬 **RAG-Powered Chat** | Ask questions about your saves using AI-powered retrieval |

### Dashboard Features
| Feature | Description |
|---------|-------------|
| 🗂️ **Collections** | Organize saves into custom folders |
| 📊 **Analytics Dashboard** | Track saves by platform, category, and time with visual heatmaps |
| 🎲 **Discover Mode** | Browse random saves to rediscover forgotten gems |
| 🌅 **Daily Dose** | Get a forgotten save resurfaced every morning at 8AM |
| 📤 **CSV Export** | Download all your saves in one click |
| 🏷️ **100+ Categories** | From AI & Machine Learning to Food & Recipes |

### WhatsApp Commands
```
<any URL>           → Save & summarize content
surprise me         → Random save from your history
motivate me         → Random Motivation/Fitness save
teach me            → Random Tech/Education save
feed me             → Random Food/Recipe save
ask: <question>     → Chat with your saves using RAG
my streak           → See your saving streak and stats
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER (WhatsApp)                          │
└────────────────────────┬────────────────────────────────────┘
                         │ Sends URL or command
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  TWILIO WEBHOOK                              │
│            /whatsapp/webhook (POST)                          │
│    • Immediate acknowledgment                                │
│    • Background processing thread                            │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼──────────────┐
         ▼               ▼              ▼
  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
  │  Content    │ │  AI         │ │  Database    │
  │  Extractor  │ │  Processor  │ │  (SQLite)    │
  │             │ │             │ │              │
  │  • Meta     │ │  • Groq     │ │  • Status    │
  │    tags     │ │    (text)   │ │    tracking  │
  │  • yt-dlp   │ │  • Gemini   │ │  • Full      │
  │    fallback │ │    (video)  │ │    metadata  │
  └─────────────┘ └─────────────┘ └──────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   Flask Web Dashboard         │
         │   • Search & Filter           │
         │   • Collections               │
         │   • Analytics                 │
         │   • Export                    │
         └───────────────────────────────┘
```

### Extraction Pipeline

Every URL goes through a **two-tier extraction strategy**:

```
URL Received
     │
     ▼
[Tier 1] Meta Tag Scraping
     ├── Extract Open Graph tags
     ├── Parse video/image URLs
     └── Get title, caption, thumbnail
     │
     ▼
[Tier 2] yt-dlp Fallback (if needed)
     ├── Supports 1000+ platforms
     ├── Cookie-based authentication
     ├── Direct media URL extraction
     └── Error classification
     │
     ▼
[Status Tracking]
     ├── media_extraction_status
     │   • direct_media_found
     │   • yt_dlp_success
     │   • login_required
     │   • rate_limited
     │   • cookies_file_missing
     └── media_extraction_error (details)
```

### AI Processing Pipeline

```
Extracted Content
     │
     ▼
[1] CATEGORIZATION (Groq)
     └── Assign 1 of 100+ categories
     │
     ▼
[2] SUMMARIZATION (Smart Routing)
     ├── VIDEO? → Gemini video analysis
     ├── IMAGE? → Gemini image analysis
     └── ELSE   → Groq metadata summary
     │
     ▼
[3] TAG EXTRACTION (Groq)
     └── Generate 8-12 searchable tags
     │
     ▼
[4] VIDEO SUMMARY (Gemini, if applicable)
     └── Detailed 3-5 sentence breakdown
     │
     ▼
Storage with source tracking:
     • summary_source (video/image/metadata)
     • video_summary_status (available/missing/failed)
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **WhatsApp Business Account** (via Twilio)
- **API Keys:**
  - [Groq API](https://console.groq.com/) (free tier available)
  - [Google Gemini API](https://aistudio.google.com/app/apikey) (free tier available)
  - [Twilio Account](https://www.twilio.com/console) (WhatsApp sandbox or production)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Aral-549/Social_Saver_Bot.git
cd Social_Saver_Bot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` with your credentials:

```bash
# AI Providers
GROQ_API_KEY=your-groq-api-key
GEMINI_API_KEY=your-gemini-api-key

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+14155238886

# Optional: Cookie-based extraction for authenticated platforms
YTDLP_COOKIES_FILE=cookies/instagram.txt  # Relative or absolute path
```

### Running the Application

```bash
# 1. Initialize database with sample data (optional)
python sample_data.py

# 2. Start the Flask server
python app.py
# Server runs at http://localhost:5000
```

### WhatsApp Setup

```bash
# 1. Start ngrok to expose your local server
ngrok http 5000

# 2. In Twilio Console:
#    Messaging → WhatsApp → Sandbox Settings
#    Webhook URL: https://your-ngrok-url.ngrok.io/whatsapp/webhook
#    Method: POST

# 3. Send a test message to your WhatsApp sandbox number
```

---

##  Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.11, Flask 3.0 | Web framework and API |
| **AI - Text** | Groq API (Llama 3.3 70B) | Categorization, tagging, RAG |
| **AI - Video** | Google Gemini 2.0 Flash | Video/image analysis |
| **Messaging** | Twilio Programmable Messaging | WhatsApp integration |
| **Database** | SQLite | Zero-config persistence |
| **Extraction** | BeautifulSoup, yt-dlp | Content scraping & media extraction |
| **Frontend** | Vanilla JS, CSS3, Font Awesome | Dashboard UI |

---

## 📁 Project Structure

```
social-saver-bot/
├── app.py                      # Flask app, routes, WhatsApp webhook
├── database.py                 # SQLite operations & schema
├── content_extractor.py        # Platform-specific content extraction
├── ai_processor.py             # Groq + Gemini orchestration
├── config.py                   # Configuration & prompts
├── sample_data.py              # Demo data generator
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
│
├── static/
│   └── js/
│       └── main.js             # Dashboard interactivity
│
├── templates/
│   ├── dashboard.html          # Main content grid
│   ├── content.html            # Single content detail view
│   ├── discover.html           # Random content discovery
│   ├── stats.html              # Usage analytics with heatmap
│   └── collections.html        # Folder organization
│
└── tests/
    ├── test_ai_processor.py    # AI pipeline tests
    ├── test_app.py             # Webhook flow tests
    └── test_content_extractor.py  # Extraction tests
```

---

## 🌐 Supported Platforms

**Full Support** (metadata + media extraction):
- Instagram (posts, reels, stories)
- YouTube (videos, shorts)
- Twitter / X
- TikTok
- Facebook
- LinkedIn
- Reddit
- Pinterest

**Generic Support** (metadata only):
- Any blog or website with Open Graph tags

---

## 🔧 Advanced Configuration

### Authenticated Media Extraction

For platforms that require login (Instagram, private accounts):

```bash
# 1. Export browser cookies (Chrome/Firefox)
#    Use extension: "Get cookies.txt LOCALLY"

# 2. Save to project directory
mkdir cookies
mv ~/Downloads/instagram.txt cookies/

# 3. Update .env
YTDLP_COOKIES_FILE=cookies/instagram.txt

# 4. Extraction will now use your session
```

### Custom Prompts

Edit prompts in `config.py`:

```python
CATEGORY_PROMPT = """Your custom categorization prompt..."""
VIDEO_SUMMARY_PROMPT = """Your custom video summary prompt..."""
```

---

## 📊 Status Tracking

The system tracks extraction and AI status for transparency:

### Extraction Status
- `direct_media_found` - Video URL found in meta tags
- `yt_dlp_success` - yt-dlp successfully extracted media
- `login_required` - Platform blocked anonymous access
- `rate_limited` - Too many requests
- `cookies_file_missing` - Configured cookie file not found
- `unsupported_extractor` - Platform not supported by yt-dlp

### Summary Source
- `video` - Generated from actual video analysis
- `image` - Generated from image analysis
- `metadata` - Generated from title/caption only
- `metadata_no_video` - Video extraction failed, used metadata

### Video Summary Status
- `available` - Detailed video summary generated
- `video_media_missing` - No video URL to analyze
- `video_analysis_failed` - Gemini analysis failed
- `gemini_disabled` - Gemini API not configured

---

## 🐛 Troubleshooting

### WhatsApp webhook not receiving messages

```bash
# Check ngrok is running
ngrok http 5000

# Verify webhook URL in Twilio Console
# Format: https://abc123.ngrok.io/whatsapp/webhook

# Check Flask logs
python app.py  # Should show incoming requests
```

### Instagram/TikTok extraction failing

```bash
# Enable yt-dlp fallback
YTDLP_ENABLED=true

# For "login required" errors:
# 1. Export browser cookies
# 2. Set YTDLP_COOKIES_FILE path
# 3. Retry extraction
```

### AI summaries not generating

```bash
# Verify API keys are set
echo $GROQ_API_KEY
echo $GEMINI_API_KEY

# Check API quota limits
# Groq: https://console.groq.com/
# Gemini: https://aistudio.google.com/
```

---

## 🚧 Known Limitations

**Production Readiness:**
- ❌ No authentication system
- ❌ Synchronous AI calls (blocking)
- ❌ Thread-based background jobs (not durable)
- ❌ Print-based logging (no structured logs)
- ❌ No rate limiting
- ❌ Minimal test coverage

**Database Design:**
- Tags stored as comma-separated strings (not queryable)
- No foreign key constraints
- Additive schema migrations only

**Extraction:**
- Some platforms require cookies for reliable extraction
- Rate limiting can block frequent requests
- Platform API changes can break extractors

---


## 📄 License

MIT License — free to use, hack, and build upon.

---

## 🙏 Acknowledgments

Built with:
- [Groq](https://groq.com/) for lightning-fast LLM inference
- [Google Gemini](https://ai.google.dev/) for multimodal understanding
- [Twilio](https://www.twilio.com/) for WhatsApp connectivity
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for robust media extraction

---

## 👥 Contributing

Contributions are welcome! This started as a hackathon project and has room for improvement.

**Areas that need help:**
- Adding test coverage
- Improving extraction reliability
- Optimizing AI prompt engineering
- Building the mobile app
- Documentation improvements

---

## 📧 Contact

Built by **Aral** for the MiniMax Hackathon 2025.

- GitHub: [@Aral-549](https://github.com/Aral-549)
- Project Link: [Social_Saver_Bot](https://github.com/Aral-549/Social_Saver_Bot)

---

> *"The best bookmark is the one you actually revisit."*
