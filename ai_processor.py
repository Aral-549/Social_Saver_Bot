"""
AI Processor for Social Saver Bot
Uses Groq for text tasks and Gemini for multimodal summaries.
"""

import mimetypes
import os
import re
import tempfile
import time
from typing import Dict, Optional, Tuple

import requests

from config import Config


class AIProcessor:
    def __init__(self):
        self.groq_api_key = Config.GROQ_API_KEY
        self.groq_model = Config.GROQ_MODEL
        self.groq_base_url = Config.GROQ_BASE_URL

        self.gemini_api_key = Config.GEMINI_API_KEY
        self.gemini_base_url = Config.GEMINI_BASE_URL.rstrip('/')
        self.gemini_upload_base_url = Config.GEMINI_UPLOAD_BASE_URL.rstrip('/')
        self.gemini_model = Config.GEMINI_MODEL
        self.gemini_video_model = Config.GEMINI_VIDEO_MODEL

        self.max_tokens = 1024
        self.temperature = 0.4

        self.session = requests.Session()
        self.session.headers.update({'User-Agent': Config.USER_AGENT})

    def _call_groq(self, prompt: str) -> str | None:
        """Call Groq API in OpenAI-compatible format."""
        if not self.groq_api_key:
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
            response = self.session.post(
                f'{self.groq_base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if data.get('choices'):
                return data['choices'][0]['message']['content'].strip()
            return None
        except Exception as exc:
            print(f"Groq API error: {exc}")
            return None

    def _call_gemini(self, parts: list[dict], model: Optional[str] = None) -> str | None:
        """Call Gemini generateContent with arbitrary parts."""
        if not self.gemini_api_key:
            return None

        headers = {
            'x-goog-api-key': self.gemini_api_key,
            'Content-Type': 'application/json'
        }
        payload = {'contents': [{'parts': parts}]}

        try:
            response = self.session.post(
                f'{self.gemini_base_url}/models/{model or self.gemini_model}:generateContent',
                headers=headers,
                json=payload,
                timeout=90
            )
            response.raise_for_status()
            data = response.json()

            candidates = data.get('candidates', [])
            if not candidates:
                return None

            text_parts = []
            for part in candidates[0].get('content', {}).get('parts', []):
                if 'text' in part:
                    text_parts.append(part['text'])

            text = ' '.join(text_parts).strip()
            return text or None
        except Exception as exc:
            print(f"Gemini API error: {exc}")
            return None

    def _clean_summary(self, text: str, max_words: int, complete_sentences: bool = False) -> str:
        """Normalize model output to a single short sentence."""
        if not text:
            return ''

        cleaned = text.strip()
        for prefix in ('One-liner:', 'Summary:', 'Description:', 'Caption:'):
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()

        cleaned = ' '.join(cleaned.split())
        words = cleaned.split()
        if len(words) > max_words:
            if complete_sentences:
                sentences = re.split(r'(?<=[.!?])\s+', cleaned)
                selected_sentences = []
                word_count = 0

                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    sentence_words = sentence.split()
                    if selected_sentences and word_count + len(sentence_words) > max_words:
                        break
                    if not selected_sentences and len(sentence_words) > max_words:
                        break

                    selected_sentences.append(sentence)
                    word_count += len(sentence_words)

                if selected_sentences:
                    cleaned = ' '.join(selected_sentences).strip()
                    if cleaned[-1] not in '.!?':
                        cleaned += '.'
                    return cleaned

            cleaned = ' '.join(words[:max_words]).rstrip(' ,;:')
            if cleaned and cleaned[-1] not in '.!?':
                cleaned += '.'
        return cleaned

    def _download_media_to_temp(
        self,
        media_url: str,
        fallback_suffix: str,
        expected_prefix: str
    ) -> Optional[Tuple[str, str]]:
        """Download remote media to a temp file for Gemini upload."""
        temp_path = None

        try:
            response = self.session.get(media_url, stream=True, timeout=60)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '').split(';')[0].strip().lower()
            if not content_type or not content_type.startswith(expected_prefix):
                guessed_type, _ = mimetypes.guess_type(media_url)
                content_type = guessed_type or content_type

            if not content_type:
                content_type = 'video/mp4' if expected_prefix == 'video/' else 'image/jpeg'

            suffix = mimetypes.guess_extension(content_type) or fallback_suffix
            fd, temp_path = tempfile.mkstemp(suffix=suffix)

            total_bytes = 0
            with os.fdopen(fd, 'wb') as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    total_bytes += len(chunk)
                    if total_bytes > Config.MAX_MEDIA_DOWNLOAD_BYTES:
                        raise ValueError('Media file is too large to analyze')
                    temp_file.write(chunk)

            return temp_path, content_type
        except Exception as exc:
            print(f"Media download error: {exc}")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return None

    def _upload_file_to_gemini(self, file_path: str, mime_type: str, display_name: str) -> Optional[Dict]:
        """Upload a local file to Gemini Files API."""
        if not self.gemini_api_key:
            return None

        try:
            file_size = os.path.getsize(file_path)
            start_headers = {
                'x-goog-api-key': self.gemini_api_key,
                'X-Goog-Upload-Protocol': 'resumable',
                'X-Goog-Upload-Command': 'start',
                'X-Goog-Upload-Header-Content-Length': str(file_size),
                'X-Goog-Upload-Header-Content-Type': mime_type,
                'Content-Type': 'application/json'
            }
            start_payload = {'file': {'display_name': display_name}}

            start_response = self.session.post(
                f'{self.gemini_upload_base_url}/files',
                headers=start_headers,
                json=start_payload,
                timeout=30
            )
            start_response.raise_for_status()

            upload_url = start_response.headers.get('X-Goog-Upload-URL')
            if not upload_url:
                return None

            with open(file_path, 'rb') as handle:
                upload_response = self.session.post(
                    upload_url,
                    headers={
                        'X-Goog-Upload-Offset': '0',
                        'X-Goog-Upload-Command': 'upload, finalize'
                    },
                    data=handle,
                    timeout=120
                )

            upload_response.raise_for_status()
            file_info = upload_response.json().get('file') or upload_response.json()

            file_name = file_info.get('name')
            if mime_type.startswith('video/') and file_name:
                processed = self._wait_for_gemini_file(file_name)
                if processed:
                    return processed

            return file_info
        except Exception as exc:
            print(f"Gemini upload error: {exc}")
            return None

    def _wait_for_gemini_file(self, file_name: str, timeout_seconds: int = 120) -> Optional[Dict]:
        """Poll Gemini until an uploaded file is ready."""
        deadline = time.time() + timeout_seconds
        headers = {'x-goog-api-key': self.gemini_api_key}

        while time.time() < deadline:
            try:
                response = self.session.get(
                    f'{self.gemini_base_url}/{file_name}',
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                file_info = response.json().get('file') or response.json()

                state = file_info.get('state', '')
                if isinstance(state, dict):
                    state = state.get('name', '')

                if state == 'ACTIVE':
                    return file_info
                if state == 'FAILED':
                    return None

                time.sleep(5)
            except Exception as exc:
                print(f"Gemini file polling error: {exc}")
                return None

        return None

    def _delete_gemini_file(self, file_name: str) -> None:
        """Best-effort cleanup for uploaded Gemini files."""
        if not self.gemini_api_key or not file_name:
            return

        try:
            self.session.delete(
                f'{self.gemini_base_url}/{file_name}',
                headers={'x-goog-api-key': self.gemini_api_key},
                timeout=30
            )
        except Exception:
            pass

    def _summarize_youtube_video(self, url: str, title: str, caption: str, platform: str) -> str | None:
        """Use Gemini URL context for YouTube links."""
        prompt = Config.VIDEO_SUMMARY_PROMPT.format(
            title=title or 'Unknown title',
            caption=caption or 'No caption available',
            platform=platform
        )
        return self._call_gemini(
            [
                {'file_data': {'file_uri': url}},
                {'text': prompt}
            ],
            model=self.gemini_video_model
        )

    def _summarize_uploaded_media(
        self,
        media_url: str,
        prompt: str,
        expected_prefix: str,
        fallback_suffix: str,
        model: str
    ) -> str | None:
        """Download remote media, upload it to Gemini, summarize, then clean up."""
        downloaded = self._download_media_to_temp(
            media_url=media_url,
            fallback_suffix=fallback_suffix,
            expected_prefix=expected_prefix
        )
        if not downloaded:
            return None

        temp_path, mime_type = downloaded
        uploaded_file = None

        try:
            uploaded_file = self._upload_file_to_gemini(
                file_path=temp_path,
                mime_type=mime_type,
                display_name=os.path.basename(temp_path)
            )
            if not uploaded_file or not uploaded_file.get('uri'):
                return None

            return self._call_gemini(
                [
                    {
                        'file_data': {
                            'mime_type': mime_type,
                            'file_uri': uploaded_file['uri']
                        }
                    },
                    {'text': prompt}
                ],
                model=model
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if uploaded_file and uploaded_file.get('name'):
                self._delete_gemini_file(uploaded_file['name'])

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
            for category in Config.DEFAULT_CATEGORIES:
                if result.lower() == category.lower():
                    return category
            return result
        return 'Other'

    def summarize_content(
        self,
        url: str,
        title: str,
        caption: str,
        platform: str,
        media_url: str = '',
        media_type: str = '',
        image_url: str = ''
    ) -> Tuple[str, str]:
        """
        Summarize content with the strongest available signal.

        Returns:
            (summary, summary_source)
        """
        video_prompt = Config.VIDEO_SUMMARY_PROMPT.format(
            title=title or 'Unknown title',
            caption=caption or 'No caption available',
            platform=platform
        )
        image_prompt = Config.IMAGE_SUMMARY_PROMPT.format(
            title=title or 'Unknown title',
            caption=caption or 'No caption available',
            platform=platform
        )
        metadata_prompt = Config.METADATA_SUMMARY_PROMPT.format(
            url=url,
            title=title or 'Unknown title',
            caption=caption or 'No caption available',
            platform=platform
        )

        is_video_content = media_type in {'video', 'reel'}

        if self.gemini_api_key and is_video_content:
            if platform == 'youtube':
                result = self._summarize_youtube_video(url, title, caption, platform)
                if result:
                    return self._clean_summary(result, max_words=30), 'video'

            if media_url:
                result = self._summarize_uploaded_media(
                    media_url=media_url,
                    prompt=video_prompt,
                    expected_prefix='video/',
                    fallback_suffix='.mp4',
                    model=self.gemini_video_model
                )
                if result:
                    return self._clean_summary(result, max_words=30), 'video'

        if self.gemini_api_key and image_url and not is_video_content:
            result = self._summarize_uploaded_media(
                media_url=image_url,
                prompt=image_prompt,
                expected_prefix='image/',
                fallback_suffix='.jpg',
                model=self.gemini_model
            )
            if result:
                return self._clean_summary(result, max_words=25), 'image'

        result = self._call_groq(metadata_prompt)
        if result:
            return self._clean_summary(result, max_words=25), 'metadata_no_video' if is_video_content else 'metadata'

        if title:
            return self._clean_summary(title, max_words=25), 'title_no_video' if is_video_content else 'title'
        if caption:
            return self._clean_summary(caption, max_words=25), 'caption_no_video' if is_video_content else 'caption'
        return 'Open the original link to review this content.', 'fallback_no_video' if is_video_content else 'fallback'

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

        if title:
            words = title.lower().split()
            tags = [word.strip('.,!?;:') for word in words if len(word) > 3][:10]
            return ', '.join(tags) if tags else platform
        return platform

    def generate_video_summary(
        self,
        url: str,
        title: str,
        caption: str,
        platform: str,
        media_url: str = '',
        media_type: str = ''
    ) -> Tuple[str, str]:
        """Generate a detailed multi-sentence video summary using Gemini."""
        if media_type not in ('video', 'reel'):
            return '', ''
        if not self.gemini_api_key:
            return '', 'gemini_disabled'

        prompt = Config.DETAILED_VIDEO_SUMMARY_PROMPT.format(
            title=title or 'Unknown title',
            caption=caption or 'No caption available',
            platform=platform
        )

        result = None

        # YouTube: use URL context directly
        if platform == 'youtube':
            result = self._call_gemini(
                [
                    {'file_data': {'file_uri': url}},
                    {'text': prompt}
                ],
                model=self.gemini_video_model
            )
            if result:
                return self._clean_summary(result, max_words=80, complete_sentences=True), 'available'

        # Other platforms: upload the media file
        if not result and media_url:
            result = self._summarize_uploaded_media(
                media_url=media_url,
                prompt=prompt,
                expected_prefix='video/',
                fallback_suffix='.mp4',
                model=self.gemini_video_model
            )
            if result:
                return self._clean_summary(result, max_words=80, complete_sentences=True), 'available'

        if not media_url and platform != 'youtube':
            return '', 'video_media_missing'

        return '', 'video_analysis_failed'

    def process_content(
        self,
        url: str,
        title: str,
        caption: str,
        platform: str,
        media_url: str = '',
        media_type: str = '',
        image_url: str = ''
    ) -> Dict:
        """Run AI tasks and return a structured result."""
        category = self.categorize_content(url, title, caption)
        summary, summary_source = self.summarize_content(
            url=url,
            title=title,
            caption=caption,
            platform=platform,
            media_url=media_url,
            media_type=media_type,
            image_url=image_url
        )
        tags = self.extract_tags(url, title, caption, platform)

        # Generate detailed video summary for video/reel content
        video_summary, video_summary_status = self.generate_video_summary(
            url=url,
            title=title,
            caption=caption,
            platform=platform,
            media_url=media_url,
            media_type=media_type
        )

        return {
            'category': category,
            'summary': summary,
            'summary_source': summary_source,
            'video_summary': video_summary,
            'video_summary_status': video_summary_status,
            'tags': tags
        }


    def rag_answer(self, question: str, context: str) -> str:
        """Answer a question using saved content as context."""
        prompt = Config.RAG_PROMPT.format(
            question=question,
            context=context
        )
        result = self._call_groq(prompt)
        if result:
            return result.strip()
        return "I couldn't find an answer to that in your saves."

    def generate_daily_digest(
        self,
        top_categories: str,
        title: str,
        category: str,
        summary: str,
        time_ago: str,
        url: str
    ) -> str:
        """Generate a short daily digest message."""
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

    def check_duplicate(
        self,
        existing_title: str,
        existing_summary: str,
        existing_url: str,
        new_title: str,
        new_summary: str,
        new_url: str
    ) -> bool:
        """Check if new content is a duplicate of existing content."""
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
        """Suggest a collection name for new content."""
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
        return bool(self.groq_api_key or self.gemini_api_key)


ai_processor = AIProcessor()


def categorize_content(url, title, caption):
    return ai_processor.categorize_content(url, title, caption)


def summarize_content(url, title, caption, platform, media_url='', media_type='', image_url=''):
    return ai_processor.summarize_content(url, title, caption, platform, media_url, media_type, image_url)


def extract_tags(url, title, caption, platform):
    return ai_processor.extract_tags(url, title, caption, platform)


def process_content(url, title, caption, platform, media_url='', media_type='', image_url=''):
    return ai_processor.process_content(url, title, caption, platform, media_url, media_type, image_url)


def rag_answer(question, context):
    return ai_processor.rag_answer(question, context)


def generate_daily_digest(top_categories, title, category, summary, time_ago, url):
    return ai_processor.generate_daily_digest(top_categories, title, category, summary, time_ago, url)


def check_duplicate(existing_title, existing_summary, existing_url, new_title, new_summary, new_url):
    return ai_processor.check_duplicate(existing_title, existing_summary, existing_url, new_title, new_summary, new_url)


def suggest_collection(existing_collections, title, category, tags, summary):
    return ai_processor.suggest_collection(existing_collections, title, category, tags, summary)
