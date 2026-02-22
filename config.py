"""
Configuration management for Social Saver Bot
"""

import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    FLASK_BASE_URL = os.getenv('FLASK_BASE_URL', '')

    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
    WHATSAPP_WEBHOOK_VERIFY_TOKEN = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN', 'social_saver_verify_token')

    # MiniMax AI
    MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY', '')
    MINIMAX_BASE_URL = os.getenv('MINIMAX_BASE_URL', 'https://api.minimax.chat/v1')
    MINIMAX_MODEL = os.getenv('MINIMAX_MODEL', 'abab6.5s-chat')

    # Gemini AI
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_BASE_URL = os.getenv('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta')
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash")

    # Groq AI
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_BASE_URL = os.getenv('GROQ_BASE_URL', 'https://api.groq.com/openai/v1')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

    ACTIVE_AI_PROVIDER = os.getenv('ACTIVE_AI_PROVIDER', 'groq')

    # Content
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
    DATABASE_PATH = os.getenv('DATABASE_PATH', os.path.join(os.path.dirname(__file__), 'social_saver.db'))
    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 20))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 5000))

    # Platform patterns
    PLATFORM_PATTERNS = {
        'instagram': ['instagram.com', 'instagr.am'],
        'twitter': ['twitter.com', 'x.com'],
        'facebook': ['facebook.com', 'fb.com'],
        'youtube': ['youtube.com', 'youtu.be'],
        'tiktok': ['tiktok.com'],
        'linkedin': ['linkedin.com'],
        'reddit': ['reddit.com', 'redd.it'],
        'pinterest': ['pinterest.com', 'pin.it'],
        'blog': []
    }

    ALLOWED_PLATFORMS = ['instagram', 'twitter', 'facebook', 'youtube', 'tiktok',
                         'linkedin', 'reddit', 'pinterest', 'blog']

    # ── 100 Categories ─────────────────────────────────────────────────────────
    DEFAULT_CATEGORIES = [
        # Technology (12)
        'Artificial Intelligence', 'Machine Learning', 'Programming & Coding',
        'Web Development', 'Mobile Apps', 'Cybersecurity', 'Cloud Computing',
        'Data Science', 'Blockchain & Crypto', 'Tech Gadgets & Reviews',
        'Open Source', 'Software Engineering',

        # Business & Finance (12)
        'Entrepreneurship', 'Startups & Funding', 'Marketing & Growth',
        'SEO & Content Marketing', 'Social Media Marketing', 'E-Commerce',
        'Personal Finance', 'Stock Market & Investing', 'Real Estate',
        'Business Strategy', 'Remote Work & Productivity', 'Career Development',

        # Health & Wellness (10)
        'Fitness & Workouts', 'Yoga & Stretching', 'Nutrition & Diet',
        'Mental Health & Mindfulness', 'Weight Loss', 'Bodybuilding',
        'Running & Cardio', 'Sleep & Recovery', 'Supplements & Biohacking',
        'Medical & Health News',

        # Food & Cooking (8)
        'Recipes & Cooking', 'Baking & Desserts', 'Meal Prep',
        'Vegan & Plant-Based', 'Street Food & Restaurants',
        'Coffee & Beverages', 'Wine & Cocktails', 'Food Science',

        # Entertainment (10)
        'Movies & Cinemas', 'TV Shows & Series', 'Anime & Manga',
        'Stand-Up Comedy', 'Music & Artists', 'Podcasts',
        'Gaming & Esports', 'Books & Literature', 'Streaming & Reviews',
        'Celebrity & Pop Culture',

        # Travel & Adventure (8)
        'Travel Destinations', 'Budget Travel & Backpacking',
        'Luxury Travel', 'Road Trips', 'Solo Travel',
        'Travel Tips & Hacks', 'Adventure Sports', 'Digital Nomad Life',

        # Education & Learning (8)
        'Science & Research', 'History & Archaeology', 'Space & Astronomy',
        'Mathematics & Logic', 'Language Learning', 'Online Courses',
        'Study Tips & Productivity', 'Philosophy & Critical Thinking',

        # Creative & Arts (8)
        'Photography', 'Graphic Design & UI/UX', 'Video Production',
        'Digital Art & Illustration', 'Architecture & Interiors',
        'Fashion & Style', 'DIY & Crafts', 'Writing & Storytelling',

        # Lifestyle (8)
        'Minimalism & Organization', 'Parenting & Family',
        'Pets & Animals', 'Relationships & Dating',
        'Luxury & Lifestyle', 'Motivation & Self-Help',
        'Spirituality & Religion', 'Astrology & Wellness',

        # News & Society (8)
        'World News', 'Politics & Policy', 'Environment & Climate',
        'Human Rights & Social Justice', 'Economics & Global Markets',
        'Science News', 'Sports News', 'Local & Community',

        # Sports (6)
        'Football & Soccer', 'Cricket', 'Basketball & NBA',
        'Tennis & Racket Sports', 'Combat Sports & MMA', 'Motorsports & F1',

        # Miscellaneous (2)
        'Viral & Trending', 'Other',
    ]

    # ── Prompts ─────────────────────────────────────────────────────────────────

    CATEGORY_PROMPT = """You are an expert content librarian. Your only job is to assign ONE category label to a piece of saved content.

AVAILABLE CATEGORIES:
{categories}

CONTENT TO CATEGORIZE:
- URL: {url}
- Title: {title}
- Description: {caption}

RULES:
1. Return ONLY the exact category name from the list above — nothing else.
2. No explanation, no punctuation, no quotes around the answer.
3. Pick the MOST SPECIFIC category that applies.
4. If the content is a how-to or tutorial, prefer the skill-based category (e.g. "Programming & Coding" over "Education").
5. If the URL is a video platform (youtube.com, tiktok.com), factor in the title heavily.
6. Never invent a new category. If unsure, return "Other".

EXAMPLES:
Title: "I built a SaaS in 24 hours with Next.js" → Web Development
Title: "10-minute morning yoga for beginners" → Yoga & Stretching
Title: "Why the Fed raised rates again" → Economics & Global Markets
Title: "Gordon Ramsay's perfect scrambled eggs" → Recipes & Cooking

Category:"""

    SUMMARY_PROMPT = """You are a viral content writer. Your job is to write one irresistible hook sentence for a saved piece of content — the kind that makes someone stop scrolling.

CONTENT:
- Platform: {platform}
- Title: {title}
- Description: {caption}

RULES:
1. Return ONLY the one-liner — no labels, no quotes, no explanation.
2. Maximum 20 words.
3. Do NOT just rephrase the title. Add curiosity, urgency, or value.
4. No emojis, no hashtags, no markdown.
5. Write in second person ("you") or use an action verb to create energy.
6. If the content is technical, highlight the outcome/benefit, not the method.

EXAMPLES:
Title: "How to negotiate your salary" → You're leaving money on the table every time you skip this one conversation.
Title: "React hooks explained" → Finally understand React hooks without the confusion that killed your last project.
Title: "Sourdough bread recipe" → The beginner sourdough recipe that actually works on the first try.
Title: "Morning routine tips" → The 10-minute morning habit that separates productive people from everyone else.

One-liner:"""

    TAGS_PROMPT = """You are a search engine optimizer. Extract highly searchable tags from a piece of saved content so the user can find it later by keyword.

CONTENT:
- URL: {url}
- Platform: {platform}
- Title: {title}
- Description: {caption}

RULES:
1. Return ONLY comma-separated tags — no explanation, no numbering, no extra text.
2. Generate between 8 and 12 tags.
3. Use lowercase. Hyphenate multi-word tags: "machine-learning", "home-workout".
4. Mix broad tags (e.g. "fitness") with specific ones (e.g. "beginner-workout", "no-equipment").
5. Include: main topic, subtopics, target audience, content format (e.g. tutorial, recipe, review), mood/style.
6. Avoid useless generic tags like "post", "content", "link", "video", "article".
7. Include the platform name as a tag if it's a social platform.

EXAMPLES:
Title: "10 Python tricks every developer should know" →
python, programming, developer-tips, code-quality, python-tricks, software-engineering, beginner-friendly, tutorial, productivity, clean-code

Title: "Budget travel in Southeast Asia" →
travel, southeast-asia, budget-travel, backpacking, travel-tips, thailand, vietnam, solo-travel, cheap-flights, digital-nomad

Tags:"""

    RAG_PROMPT = """You are a personal knowledge assistant. The user has saved a collection of links with AI-generated summaries, categories, and tags. Your job is to answer their question using ONLY the saved content provided below.

USER QUESTION:
{question}

SAVED CONTENT (most relevant matches):
{context}

RULES:
1. Answer conversationally — like a smart friend who has read all their saves.
2. If the answer is found in the saves, cite the title and provide the URL.
3. If multiple saves are relevant, mention all of them briefly.
4. If NO saves are relevant, say: "I couldn't find anything about that in your saves. Try saving some content on this topic first!"
5. Keep the response under 200 words — this will be sent via WhatsApp.
6. Never make up information. Only use what's in the provided saves.
7. Format for WhatsApp: use line breaks, no markdown headers, no bullet symbols.

RESPONSE:"""

    DAILY_DIGEST_PROMPT = """You are a personal curator sending a warm, engaging morning message to someone about content they forgot they saved.

USER'S TOP CATEGORIES THIS WEEK:
{top_categories}

FEATURED SAVE:
- Title: {title}
- Category: {category}
- Summary: {summary}
- Saved: {time_ago}
- URL: {url}

RULES:
1. Write a short, warm WhatsApp message (under 150 words).
2. Start with a friendly morning greeting tied to the content topic.
3. Remind them why this save matters or what they might gain from it.
4. End with a gentle call to action to revisit it.
5. Use 1–2 emojis max. No markdown. WhatsApp-friendly line breaks.
6. Make it feel personal, not automated.

EXAMPLE TONE:
"Good morning! ☀️ You saved this one 3 weeks ago and never got back to it...
📌 How to negotiate a raise
Knowing this could literally change your next salary conversation.
Worth 5 minutes today 👉 [url]"

Message:"""

    DUPLICATE_CHECK_PROMPT = """You are a content deduplication engine. Determine if two pieces of content are about the same topic, even if the URLs or exact wording differ.

EXISTING SAVE:
- Title: {existing_title}
- Summary: {existing_summary}
- URL: {existing_url}

NEW CONTENT:
- Title: {new_title}
- Summary: {new_summary}
- URL: {new_url}

RULES:
1. Return ONLY one word: "DUPLICATE" or "UNIQUE".
2. Mark as DUPLICATE if: same video/article on different URL formats, same news story from different outlets, same tutorial/recipe with minor variations.
3. Mark as UNIQUE if: same broad topic but meaningfully different content, perspective, or format.
4. Do not consider platform differences alone as making content unique.

Result:"""

    COLLECTION_SUGGEST_PROMPT = """You are a personal content organizer. Based on a user's saved content, suggest the most fitting collection name for a new save.

USER'S EXISTING COLLECTIONS:
{existing_collections}

NEW CONTENT BEING SAVED:
- Title: {title}
- Category: {category}
- Tags: {tags}
- Summary: {summary}

RULES:
1. If the new content fits an existing collection well, return that EXACT collection name.
2. If no existing collection fits, suggest a SHORT new collection name (2–4 words max).
3. Return ONLY the collection name — nothing else.
4. Collection names should be intuitive, personal, and action-oriented.
   Good: "Morning Reads", "Startup Ideas", "Workout Plans", "Python Resources"
   Bad: "Technology", "Content", "Saved Items"

Collection:"""


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True


def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    return {'development': DevelopmentConfig, 'production': ProductionConfig,
            'testing': TestingConfig}.get(env, DevelopmentConfig)


def detect_platform(url: str) -> str:
    url_lower = url.lower()
    for platform, patterns in Config.PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if pattern in url_lower:
                return platform
    return 'blog'


def is_valid_url(url: str) -> bool:
    from urllib.parse import urlparse
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False
