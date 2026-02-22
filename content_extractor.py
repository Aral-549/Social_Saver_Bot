"""
Content Extractor for Social Saver Bot
Extracts content from various social media platforms and blogs
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, Tuple
from config import Config, detect_platform, is_valid_url


class ContentExtractor:
    """Extract content from various platforms"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.timeout = Config.REQUEST_TIMEOUT
    
    def extract(self, url: str) -> Dict:
        """
        Main extraction method - dispatches to platform-specific extractors
        
        Args:
            url: URL of the content to extract
        
        Returns:
            Dictionary with extracted content
        """
        if not is_valid_url(url):
            return {
                'success': False,
                'error': 'Invalid URL format'
            }
        
        platform = detect_platform(url)
        
        # Dispatch to platform-specific extractor
        extractors = {
            'instagram': self._extract_instagram,
            'twitter': self._extract_twitter,
            'facebook': self._extract_facebook,
            'youtube': self._extract_youtube,
            'tiktok': self._extract_tiktok,
            'linkedin': self._extract_linkedin,
            'reddit': self._extract_reddit,
            'pinterest': self._extract_pinterest,
        }
        
        extractor = extractors.get(platform, self._extract_generic)
        return extractor(url)
    
    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """Make HTTP request and return BeautifulSoup object"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
    
    def _clean_instagram_title(self, caption: str) -> str:
        """Clean Instagram caption to create a short title"""
        import re
        
        if not caption:
            return 'Instagram Post'
        
        # Strip hashtags
        text = re.sub(r'#\w+', '', caption)
        # Strip @mentions
        text = re.sub(r'@\w+', '', text)
        # Strip emojis (simple approach - remove non-ASCII and common emoji ranges)
        emoji_pattern = re.compile(
            "[" 
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        text = emoji_pattern.sub('', text)
        # Strip multiple dots
        text = re.sub(r'\.{2,}', '', text)
        # Strip extra whitespace
        text = ' '.join(text.split())
        
        # Get first sentence or first 60 chars
        if '.' in text:
            first_sentence = text.split('.')[0]
            if len(first_sentence) <= 60:
                return first_sentence.strip() + '.'
        
        # Return first 60 chars
        return text[:60].strip() if text else 'Instagram Post'
    
    def _extract_instagram(self, url: str) -> Dict:
        """Extract content from Instagram posts"""
        soup = self._make_request(url)
        
        if not soup:
            return {'success': False, 'error': 'Failed to fetch Instagram post'}
        
        # Try to extract from meta tags first
        title = soup.find('meta', property='og:title')
        caption = soup.find('meta', property='og:description')
        image = soup.find('meta', property='og:image')
        
        # Full caption (keep untouched)
        full_caption = caption['content'] if caption else ''
        
        result = {
            'success': True,
            'platform': 'instagram',
            'url': url,
            'title': '',  # Will be set below with cleaned version
            'caption': full_caption,  # Keep full caption
            'image_url': image['content'] if image else '',
            'author': '',
            'media_type': 'post'
        }
        
        # Try to extract additional data from script tags
        script = soup.find('script', text=re.compile(r'window._sharedData'))
        if script:
            try:
                data = json.loads(script.string.split('window._sharedData = ')[1].split(';')[0])
                if 'entry_data' in data and 'PostPage' in data['entry_data']:
                    post = data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
                    full_caption = post.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', full_caption)
                    result['caption'] = full_caption
                    result['author'] = post.get('owner', {}).get('username', '')
            except Exception:
                pass
        
        # Set cleaned title from caption
        result['title'] = self._clean_instagram_title(full_caption)
        
        return result
    
    def _extract_twitter(self, url: str) -> Dict:
        """Extract content from Twitter/X posts"""
        import re
        from urllib.parse import quote
        import html
        
        # Try Twitter's oEmbed API first
        try:
            oembed_url = f"https://publish.twitter.com/oembed?url={quote(url)}"
            oembed_response = self.session.get(oembed_url, timeout=10)
            if oembed_response.status_code == 200:
                oembed_data = oembed_response.json()
                html_content = oembed_data.get('html', '')
                author = oembed_data.get('author_name', '')
                
                # Extract text from HTML by stripping tags
                text = re.sub(r'<[^>]+>', '', html_content)
                text = text.strip()
                
                # Unescape HTML entities
                text = html.unescape(text)
                
                # Strip trailing attribution like "— Boris Cherny (@bcherny) February 20, 2026"
                text = re.sub(r'—\s*\S+\s*\(@\w+\)\s*\w+\s+\d+,\s*\d+', '', text).strip()
                
                return {
                    'success': True,
                    'platform': 'twitter',
                    'url': url,
                    'title': f'Tweet by {author}' if author else 'Twitter Post',
                    'caption': text,
                    'image_url': '',
                    'author': author,
                    'media_type': 'tweet'
                }
        except Exception as e:
            print(f"oEmbed failed: {e}")
        
        # Try direct page fetch
        soup = self._make_request(url)
        
        if soup:
            # Try meta tags
            title = soup.find('meta', property='og:title')
            description = soup.find('meta', property='og:description')
            image = soup.find('meta', property='og:image')
            
            # Also try meta name="description"
            if not description:
                description = soup.find('meta', attrs={'name': 'description'})
            
            caption = ''
            if description:
                caption = html.unescape(description.get('content', ''))
            
            # Try to find tweet data in page script
            author = ''
            script = soup.find('script', text=re.compile(r'window.__INITIAL_STATE__'))
            if script and script.string:
                try:
                    text_match = re.search(r'"text":"([^"]+)"', script.string)
                    if text_match:
                        caption = text_match.group(1).replace('\\n', '\n')
                    author_match = re.search(r'"screen_name":"([^"]+)"', script.string)
                    if author_match:
                        author = author_match.group(1)
                except Exception:
                    pass
            
            if caption:
                # Strip trailing attribution
                caption = re.sub(r'—\s*\S+\s*\(@\w+\)\s*\w+\s+\d+,\s*\d+', '', caption).strip()
                
                return {
                    'success': True,
                    'platform': 'twitter',
                    'url': url,
                    'title': title['content'] if title else f'Tweet by {author}' if author else 'Twitter Post',
                    'caption': caption,
                    'image_url': image['content'] if image else '',
                    'author': author,
                    'media_type': 'tweet'
                }
        
        # Fallback - extract author from URL
        author = ''
        match = re.search(r'twitter\.com/([^/]+)', url)
        if match:
            author = match.group(1)
        
        # Final fallback
        return {
            'success': True,
            'platform': 'twitter',
            'url': url,
            'title': f'Tweet by {author}' if author else 'Twitter Post',
            'caption': f'Tweet by {author} — click to view' if author else 'Twitter Post — click to view',
            'image_url': '',
            'author': author,
            'media_type': 'tweet'
        }
    
    def _extract_facebook(self, url: str) -> Dict:
        """Extract content from Facebook posts"""
        soup = self._make_request(url)
        
        if not soup:
            return {'success': False, 'error': 'Failed to fetch Facebook post'}
        
        title = soup.find('meta', property='og:title')
        description = soup.find('meta', property='og:description')
        image = soup.find('meta', property='og:image')
        
        return {
            'success': True,
            'platform': 'facebook',
            'url': url,
            'title': title['content'] if title else 'Facebook Post',
            'caption': description['content'] if description else '',
            'image_url': image['content'] if image else '',
            'author': '',
            'media_type': 'post'
        }
    
    def _extract_youtube(self, url: str) -> Dict:
        """Extract content from YouTube videos"""
        soup = self._make_request(url)
        
        if not soup:
            return {'success': False, 'error': 'Failed to fetch YouTube video'}
        
        title = soup.find('meta', property='og:title')
        description = soup.find('meta', property='og:description')
        image = soup.find('meta', property='og:image')
        
        # Extract video ID
        video_id = ''
        if 'youtube.com' in url:
            match = re.search(r'v=([^&]+)', url)
            if match:
                video_id = match.group(1)
        elif 'youtu.be' in url:
            match = re.search(r'youtu\.be/([^?]+)', url)
            if match:
                video_id = match.group(1)
        
        return {
            'success': True,
            'platform': 'youtube',
            'url': url,
            'title': title['content'] if title else 'YouTube Video',
            'caption': description['content'] if description else '',
            'image_url': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg' if video_id else (image['content'] if image else ''),
            'video_id': video_id,
            'media_type': 'video'
        }
    
    def _extract_tiktok(self, url: str) -> Dict:
        """Extract content from TikTok videos"""
        soup = self._make_request(url)
        
        if not soup:
            return {'success': False, 'error': 'Failed to fetch TikTok video'}
        
        title = soup.find('meta', property='og:title')
        description = soup.find('meta', property='og:description')
        image = soup.find('meta', property='og:image')
        
        return {
            'success': True,
            'platform': 'tiktok',
            'url': url,
            'title': title['content'] if title else 'TikTok Video',
            'caption': description['content'] if description else '',
            'image_url': image['content'] if image else '',
            'author': '',
            'media_type': 'video'
        }
    
    def _extract_linkedin(self, url: str) -> Dict:
        """Extract content from LinkedIn posts"""
        soup = self._make_request(url)
        
        if not soup:
            return {'success': False, 'error': 'Failed to fetch LinkedIn post'}
        
        title = soup.find('meta', property='og:title')
        description = soup.find('meta', property='og:description')
        image = soup.find('meta', property='og:image')
        
        return {
            'success': True,
            'platform': 'linkedin',
            'url': url,
            'title': title['content'] if title else 'LinkedIn Post',
            'caption': description['content'] if description else '',
            'image_url': image['content'] if image else '',
            'author': '',
            'media_type': 'post'
        }
    
    def _extract_reddit(self, url: str) -> Dict:
        """Extract content from Reddit posts"""
        soup = self._make_request(url)
        
        if not soup:
            return {'success': False, 'error': 'Failed to fetch Reddit post'}
        
        title = soup.find('meta', property='og:title')
        description = soup.find('meta', property='og:description')
        image = soup.find('meta', property='og:image')
        
        return {
            'success': True,
            'platform': 'reddit',
            'url': url,
            'title': title['content'] if title else 'Reddit Post',
            'caption': description['content'] if description else '',
            'image_url': image['content'] if image else '',
            'author': '',
            'media_type': 'post'
        }
    
    def _extract_pinterest(self, url: str) -> Dict:
        """Extract content from Pinterest pins"""
        soup = self._make_request(url)
        
        if not soup:
            return {'success': False, 'error': 'Failed to fetch Pinterest pin'}
        
        title = soup.find('meta', property='og:title')
        description = soup.find('meta', property='og:description')
        image = soup.find('meta', property='og:image')
        
        return {
            'success': True,
            'platform': 'pinterest',
            'url': url,
            'title': title['content'] if title else 'Pinterest Pin',
            'caption': description['content'] if description else '',
            'image_url': image['content'] if image else '',
            'author': '',
            'media_type': 'image'
        }
    
    def _extract_generic(self, url: str) -> Dict:
        """Extract content from generic websites/blogs"""
        soup = self._make_request(url)
        
        if not soup:
            return {'success': False, 'error': 'Failed to fetch webpage'}
        
        # Extract title
        title = soup.find('title')
        if not title:
            title = soup.find('meta', property='og:title')
            title = title['content'] if title else 'Untitled'
        else:
            title = title.string
        
        # Extract meta description
        description = soup.find('meta', attrs={'name': 'description'})
        if not description:
            description = soup.find('meta', property='og:description')
            description = description['content'] if description else ''
        else:
            description = description.get('content', '')
        
        # Extract og:image
        image = soup.find('meta', property='og:image')
        image_url = image['content'] if image else ''
        
        # Extract author if available
        author = ''
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta:
            author = author_meta.get('content', '')
        
        # Extract main content if it's a blog
        main_content = ''
        article = soup.find('article') or soup.find('main')
        if article:
            # Get text content, limit to first few paragraphs
            paragraphs = article.find_all('p')[:5]
            main_content = ' '.join(p.get_text(strip=True) for p in paragraphs)
        
        return {
            'success': True,
            'platform': 'blog',
            'url': url,
            'title': title.strip() if title else 'Untitled',
            'caption': description.strip() if description else main_content[:500],
            'image_url': image_url,
            'author': author,
            'media_type': 'article'
        }
    
    def extract_with_retry(self, url: str, max_retries: int = 3) -> Dict:
        """
        Extract content with retry logic
        
        Args:
            url: URL to extract
            max_retries: Maximum number of retry attempts
        
        Returns:
            Extracted content dictionary
        """
        for attempt in range(max_retries):
            result = self.extract(url)
            if result.get('success'):
                return result
            
            if attempt < max_retries - 1:
                import time
                time.sleep(1)  # Wait before retry
        
        return result


# Singleton instance
extractor = ContentExtractor()


def extract_content(url: str) -> Dict:
    """Convenience function to extract content from URL"""
    return extractor.extract(url)


def extract_content_with_retry(url: str, max_retries: int = 3) -> Dict:
    """Convenience function to extract content with retry"""
    return extractor.extract_with_retry(url, max_retries)
