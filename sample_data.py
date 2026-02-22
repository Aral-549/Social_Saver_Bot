"""
Sample Data Generator for Social Saver Bot
Run this script to populate the database with demo content for testing
"""

import random
from datetime import datetime, timedelta
from database import init_db, save_content, get_all_content


# ✅ FIX: Added image_url to every sample + more varied, realistic content
SAMPLE_CONTENT = [
    {
        'url': 'https://www.instagram.com/p/beachsunset2024/',
        'platform': 'instagram',
        'title': 'Golden Hour at the Beach',
        'caption': 'Nothing beats a perfect sunset by the ocean 🌅 #sunset #beach #nature #travel #photography #goldenhour',
        'category': 'Photography',
        'tags': 'sunset, beach, nature, travel, photography, golden-hour, ocean, landscape',
        'summary': 'You will never scroll past a sunset again after seeing this golden hour shot.',
        'image_url': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=80',
    },
    {
        'url': 'https://twitter.com/OpenAI/status/1234567890123',
        'platform': 'twitter',
        'title': 'Tweet by OpenAI: New AI Model Announcement',
        'caption': 'Introducing our most capable model yet — faster reasoning, longer context, and dramatically improved coding. Available now via API.',
        'category': 'Artificial Intelligence',
        'tags': 'ai, openai, llm, machine-learning, gpt, announcement, tech, api',
        'summary': 'The AI model you\'ve been waiting for just dropped — and it rewrites what\'s possible.',
        'image_url': '',
    },
    {
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'platform': 'youtube',
        'title': 'Build a Full-Stack App in 1 Hour with Next.js 14',
        'caption': 'Complete tutorial: Authentication, database, deployment — everything from scratch in under 60 minutes.',
        'category': 'Web Development',
        'tags': 'nextjs, react, fullstack, tutorial, web-development, coding, javascript, deployment',
        'summary': 'Ship a production-ready full-stack app before your next coffee break.',
        'image_url': 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
    },
    {
        'url': 'https://www.linkedin.com/posts/elonmusk_leadership-activity-123',
        'platform': 'linkedin',
        'title': '5 Hard Truths About Building a Startup',
        'caption': 'After 10 years of building companies, here\'s what nobody tells you about entrepreneurship. Thread 🧵',
        'category': 'Entrepreneurship',
        'tags': 'startup, entrepreneurship, leadership, business, founder, lessons, career, growth',
        'summary': 'The startup advice that could save you from making the same costly mistakes.',
        'image_url': 'https://images.unsplash.com/photo-1556761175-4b46a572b786?w=600&q=80',
    },
    {
        'url': 'https://www.reddit.com/r/programming/comments/ai_replaces_devs/',
        'platform': 'reddit',
        'title': 'Will AI Replace Software Developers by 2027?',
        'caption': 'r/programming • Posted by u/techDebater • 2.4k upvotes • 847 comments',
        'category': 'Artificial Intelligence',
        'tags': 'ai, programming, future-of-work, developers, debate, technology, careers, reddit',
        'summary': 'The Reddit thread that every developer is secretly reading right now.',
        'image_url': 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=600&q=80',
    },
    {
        'url': 'https://healthline.com/nutrition/mediterranean-diet-meal-plan',
        'platform': 'blog',
        'title': '7-Day Mediterranean Diet Meal Plan for Beginners',
        'caption': 'A complete week of heart-healthy, delicious meals with shopping list included. Nutritionist approved.',
        'category': 'Nutrition & Diet',
        'tags': 'mediterranean-diet, nutrition, meal-plan, healthy-eating, recipes, heart-health, beginner, food',
        'summary': 'The one-week meal plan that makes healthy eating actually enjoyable.',
        'image_url': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&q=80',
    },
    {
        'url': 'https://www.youtube.com/watch?v=workout2024abc',
        'platform': 'youtube',
        'title': '20-Minute Home HIIT Workout — No Equipment Needed',
        'caption': 'Burn 300 calories in 20 minutes with this high-intensity interval training workout you can do anywhere.',
        'category': 'Fitness & Workouts',
        'tags': 'hiit, workout, fitness, home-workout, no-equipment, cardio, exercise, beginner',
        'summary': 'The 20-minute routine that makes skipping gym day feel like a crime.',
        'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&q=80',
    },
    {
        'url': 'https://www.tiktok.com/@chefgordon/video/pasta_hack_99',
        'platform': 'tiktok',
        'title': 'The Pasta Trick That Changes Everything',
        'caption': 'POV: You\'ve been cooking pasta wrong your entire life 🍝 #pasta #cookinghacks #foodtiktok #viral',
        'category': 'Recipes & Cooking',
        'tags': 'pasta, cooking-hack, kitchen-tips, food-tiktok, recipe, viral, chef, easy-cooking',
        'summary': 'You\'ve been cooking pasta wrong — and this 30-second trick proves it.',
        'image_url': 'https://images.unsplash.com/photo-1551892374-ecf8754cf8b0?w=600&q=80',
    },
    {
        'url': 'https://www.pinterest.com/interior_design/minimalist-bedroom-ideas/',
        'platform': 'pinterest',
        'title': 'Minimalist Bedroom Ideas That Feel Like a 5-Star Hotel',
        'caption': '25 stunning minimalist bedroom designs that turn any room into a peaceful sanctuary.',
        'category': 'Architecture & Interiors',
        'tags': 'minimalist, bedroom, interior-design, home-decor, aesthetic, luxury, calm, pinterest',
        'summary': 'Transform your bedroom into a hotel suite with these budget-friendly minimalist ideas.',
        'image_url': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=600&q=80',
    },
    {
        'url': 'https://medium.com/@devblog/react-hooks-2024-guide',
        'platform': 'blog',
        'title': 'The Complete React Hooks Guide You\'ve Been Waiting For',
        'caption': 'From useState to custom hooks — everything explained with real-world examples and common pitfalls to avoid.',
        'category': 'Programming & Coding',
        'tags': 'react, hooks, javascript, frontend, tutorial, web-development, coding, beginners',
        'summary': 'Finally understand React hooks without the confusion that killed your last project.',
        'image_url': 'https://images.unsplash.com/photo-1633356122102-3fe601e05bd2?w=600&q=80',
    },
    {
        'url': 'https://www.instagram.com/p/travel_japan_2024/',
        'platform': 'instagram',
        'title': 'Tokyo Cherry Blossom Season 🌸',
        'caption': 'Sakura season in Tokyo hits different. The best 10 spots to see cherry blossoms + the exact timing 🗓️ #japan #tokyo #sakura #travel',
        'category': 'Travel Destinations',
        'tags': 'japan, tokyo, cherry-blossom, sakura, travel, spring, photography, asia',
        'summary': 'The cherry blossom guide that will make you book a flight to Tokyo tonight.',
        'image_url': 'https://images.unsplash.com/photo-1522383225653-ed111181a951?w=600&q=80',
    },
    {
        'url': 'https://www.youtube.com/watch?v=crypto_explained_2024',
        'platform': 'youtube',
        'title': 'Bitcoin Explained in 10 Minutes — For Complete Beginners',
        'caption': 'No jargon, no hype. Just a clear explanation of what Bitcoin is, how it works, and whether you should care.',
        'category': 'Blockchain & Crypto',
        'tags': 'bitcoin, crypto, blockchain, investing, beginner, explainer, finance, youtube',
        'summary': 'The only Bitcoin explainer you need — no jargon, no hype, just clarity.',
        'image_url': 'https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=600&q=80',
    },
    {
        'url': 'https://twitter.com/naval/status/motivation_thread_42',
        'platform': 'twitter',
        'title': 'Tweet by Naval: How to Get Rich Without Getting Lucky',
        'caption': 'Specific knowledge, accountability, leverage, and judgment. A thread on wealth creation that will change how you think.',
        'category': 'Personal Finance',
        'tags': 'wealth, finance, motivation, naval, twitter, self-improvement, investing, mindset',
        'summary': 'The wealth-building thread that\'s been screenshot and reshared a million times for a reason.',
        'image_url': '',
    },
    {
        'url': 'https://www.reddit.com/r/MachineLearning/comments/llm_primer/',
        'platform': 'reddit',
        'title': 'I Spent 3 Months Learning LLMs From Scratch — Here\'s My Complete Guide',
        'caption': 'A comprehensive beginner-to-intermediate guide on large language models, transformers, and how to fine-tune your own model.',
        'category': 'Machine Learning',
        'tags': 'llm, machine-learning, ai, transformers, deep-learning, guide, beginner, reddit',
        'summary': 'Three months of LLM research condensed into the guide you wish existed when you started.',
        'image_url': 'https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=600&q=80',
    },
    {
        'url': 'https://www.instagram.com/p/morning_routine_wellness/',
        'platform': 'instagram',
        'title': '5AM Morning Routine That Changed My Life',
        'caption': 'I\'ve done this routine every day for 6 months. Here\'s exactly what I do and why it works 🌅 #morningroutine #wellness #productivity',
        'category': 'Mental Health & Mindfulness',
        'tags': 'morning-routine, wellness, productivity, mindfulness, self-care, habit, health, instagram',
        'summary': 'The 5AM morning ritual that high-performers swear by — and why it actually works.',
        'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80',
    },
    {
        'url': 'https://techcrunch.com/2024/startup-funding-guide',
        'platform': 'blog',
        'title': 'How to Raise Your First $1M Seed Round in 2024',
        'caption': 'A practical step-by-step guide to seed fundraising — from deck to term sheet, written by a founder who\'s done it three times.',
        'category': 'Startups & Funding',
        'tags': 'startup, fundraising, venture-capital, seed-round, founder, pitch-deck, investors, business',
        'summary': 'The fundraising playbook that closes deals — written by someone who\'s raised millions.',
        'image_url': 'https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=600&q=80',
    },
]


def generate_sample_data(num_items=None):
    """
    Generate sample data and save to database.
    Inserts all unique SAMPLE_CONTENT items (up to num_items).
    
    Args:
        num_items: Max items to insert (default: all unique items)
    """
    init_db()

    if num_items is None:
        num_items = len(SAMPLE_CONTENT)

    print(f"Generating up to {num_items} sample content items...")

    # Get existing URLs from DB
    existing = get_all_content(limit=1000)
    existing_urls = {item['url'] for item in existing}

    user_phones = [
        '+1234567890',
        '+1987654321',
        '+1555123456',
        '+1555987654',
        None,
    ]

    items_added = 0

    # ✅ FIX: Shuffle so we get variety, then iterate (not random.choice in a loop)
    shuffled = SAMPLE_CONTENT[:]
    random.shuffle(shuffled)

    for sample in shuffled:
        if items_added >= num_items:
            break

        # ✅ FIX: Skip duplicates AND update set so same URL can't sneak through twice
        if sample['url'] in existing_urls:
            print(f"  Skipping duplicate: {sample['title'][:40]}")
            continue

        existing_urls.add(sample['url'])  # ✅ KEY FIX — prevent in-run duplicates

        try:
            save_content(
                url=sample['url'],
                platform=sample['platform'],
                title=sample['title'],
                caption=sample['caption'],
                image_url=sample.get('image_url', ''),  # ✅ Now includes real images
                category=sample['category'],
                summary=sample['summary'],
                tags=sample['tags'],
                user_phone=random.choice(user_phones),
            )
            items_added += 1
            print(f"  ✅ Added: {sample['title'][:50]}")
        except Exception as e:
            print(f"  ❌ Error adding {sample['url']}: {e}")

    print(f"\n✓ Successfully added {items_added} sample items!")
    print(f"Total content in database: {len(existing) + items_added}")
    return items_added


def clear_and_reseed(num_items=None):
    """
    ⚠️  Drops all rows and re-inserts fresh sample data.
    Useful to reset a messy demo database.
    """
    import sqlite3
    from database import DB_PATH

    print("⚠️  Clearing database and reseeding...")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM saved_content")
    conn.commit()
    conn.close()
    print("  Database cleared.")
    return generate_sample_data(num_items)


def show_sample_stats():
    """Display statistics about the database"""
    from database import get_stats

    stats = get_stats()

    print("\n" + "=" * 50)
    print("DATABASE STATISTICS")
    print("=" * 50)
    print(f"Total content:   {stats['total']}")
    print(f"Last 7 days:     {stats['recent_7_days']}")
    print(f"Unique users:    {stats['unique_users']}")
    print(f"\nBy Platform:")
    for platform, count in stats['by_platform'].items():
        print(f"  - {platform}: {count}")
    print(f"\nBy Category:")
    for category, count in stats['by_category'].items():
        print(f"  - {category}: {count}")
    print("=" * 50)


if __name__ == '__main__':
    import sys

    if '--reseed' in sys.argv:
        clear_and_reseed()
    else:
        generate_sample_data()

    show_sample_stats()
