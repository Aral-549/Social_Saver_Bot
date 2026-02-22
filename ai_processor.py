"""
AI Processor for Social Saver Bot
Uses Groq API for fast AI inference
"""

import json
import requests
from typing import Dict
from config import Config


class AIProcessor:
    def __init__(self):
        self.groq_api_key = Config.GROQ_API_KEY
        self.groq_model = Config.GROQ_MODEL
        self.groq_base_url = Config.GROQ_BASE_URL
        self.max_tokens = 1024
        self.temperature = 0.7

    def _call_groq(self, prompt: str) -> str | None:
        """Call Groq API (OpenAI-compatible format)"""
        if not self.groq_api_key:
            print("Warning: GROQ_API_KEY not set")
            return None
        
        headers = {
            'Authorization': f'Bearer {self.groq_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.groq_model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': self.max_tokens,
            'temperature': self.temperature
        }
        
        try:
            response = requests.post(
                f'{self.groq_base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content'].strip()
            return None
        except Exception as e:
            print(f"Groq API error: {e}")
            return None

    def categorize_content(self, url: str, title: str, caption: str) -> str:
        categories_str = ', '.join(Config.DEFAULT_CATEGORIES)
        prompt = Config.CATEGORY_PROMPT.format(
            categories=categories_str,
            url=url,
            title=title or 'No title',
            caption=caption or 'No caption'
        )
        result = self._call_groq(prompt)
        if result:
            result = result.strip()
            for cat in Config.DEFAULT_CATEGORIES:
                if result.lower() == cat.lower():
                    return cat
            return result
        return 'Other'

    def summarize_content(self, url: str, title: str, caption: str, platform: str) -> str:
        prompt = Config.SUMMARY_PROMPT.format(
            url=url,
            title=title or 'Unknown title',
            caption=caption or 'No caption available',
            platform=platform
        )
        result = self._call_groq(prompt)
        if result:
            result = result.strip()
            # Remove any prefixes
            result = result.replace('One-liner:', '').replace('Summary:', '').replace('Description:', '').strip()
            # Ensure it fits in one line (max 25 words)
            words = result.split()
            if len(words) > 25:
                result = ' '.join(words[:25]) + '...'
            return result
        # Fallback
        if title:
            return f"Check out: {title[:50]}{'...' if len(title) > 50 else ''}"
        return 'Click to view this content.'

    def extract_tags(self, url: str, title: str, caption: str, platform: str) -> str:
        prompt = Config.TAGS_PROMPT.format(
            url=url,
            title=title or 'No title',
            caption=caption or 'No caption',
            platform=platform
        )
        result = self._call_groq(prompt)
        if result:
            result = result.strip().lower()
            result = result.replace('"', '').replace("'", '').replace('tags:', '').strip()
            if len(result) >= 3:
                return result
        # Fallback: keywords from title
        if title:
            words = title.lower().split()
            tags = [w.strip('.,!?;:') for w in words if len(w) > 3][:10]
            return ', '.join(tags) if tags else platform
        return platform

    def process_content(self, url: str, title: str, caption: str, platform: str) -> Dict:
        """Run all three AI tasks and return results"""
        category = self.categorize_content(url, title, caption)
        summary = self.summarize_content(url, title, caption, platform)
        tags = self.extract_tags(url, title, caption, platform)
        return {'category': category, 'summary': summary, 'tags': tags}

    def rag_answer(self, question: str, context: str) -> str:
        """Answer a question using saved content as context (RAG)"""
        prompt = Config.RAG_PROMPT.format(
            question=question,
            context=context
        )
        result = self._call_groq(prompt)
        if result:
            return result.strip()
        return "I couldn't find an answer to that in your saves."

    def generate_daily_digest(self, top_categories: str, title: str, category: str, summary: str, time_ago: str, url: str) -> str:
        """Generate a warm daily digest message"""
        prompt = Config.DAILY_DIGEST_PROMPT.format(
            top_categories=top_categories,
            title=title,
            category=category,
            summary=summary,
            time_ago=time_ago,
            url=url
        )
        result = self._call_groq(prompt)
        if result:
            return result.strip()
        return f"You saved this {time_ago}: {title}"

    def check_duplicate(self, existing_title: str, existing_summary: str, existing_url: str,
                       new_title: str, new_summary: str, new_url: str) -> bool:
        """Check if new content is a duplicate of existing content"""
        prompt = Config.DUPLICATE_CHECK_PROMPT.format(
            existing_title=existing_title,
            existing_summary=existing_summary,
            existing_url=existing_url,
            new_title=new_title,
            new_summary=new_summary,
            new_url=new_url
        )
        result = self._call_groq(prompt)
        if result:
            return 'DUPLICATE' in result.upper()
        return False

    def suggest_collection(self, existing_collections: str, title: str, category: str, tags: str, summary: str) -> str:
        """Suggest a collection name for new content"""
        prompt = Config.COLLECTION_SUGGEST_PROMPT.format(
            existing_collections=existing_collections,
            title=title,
            category=category,
            tags=tags,
            summary=summary
        )
        result = self._call_groq(prompt)
        if result:
            return result.strip()
        return category

    def is_configured(self) -> bool:
        return bool(self.groq_api_key)


# Singleton
ai_processor = AIProcessor()


def categorize_content(url, title, caption):
    return ai_processor.categorize_content(url, title, caption)

def summarize_content(url, title, caption, platform):
    return ai_processor.summarize_content(url, title, caption, platform)

def extract_tags(url, title, caption, platform):
    return ai_processor.extract_tags(url, title, caption, platform)

def process_content(url, title, caption, platform):
    return ai_processor.process_content(url, title, caption, platform)

def rag_answer(question, context):
    return ai_processor.rag_answer(question, context)

def generate_daily_digest(top_categories, title, category, summary, time_ago, url):
    return ai_processor.generate_daily_digest(top_categories, title, category, summary, time_ago, url)

def check_duplicate(existing_title, existing_summary, existing_url, new_title, new_summary, new_url):
    return ai_processor.check_duplicate(existing_title, existing_summary, existing_url, new_title, new_summary, new_url)

def suggest_collection(existing_collections, title, category, tags, summary):
    return ai_processor.suggest_collection(existing_collections, title, category, tags, summary)
