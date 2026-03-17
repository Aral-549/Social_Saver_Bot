import os

import pytest
from bs4 import BeautifulSoup

import content_extractor as extractor_module
from content_extractor import ContentExtractor


def test_extract_instagram_reel_uses_video_meta(monkeypatch):
    extractor = ContentExtractor()
    soup = BeautifulSoup(
        '''
        <html>
            <meta property="og:description" content="Watch this coding reel" />
            <meta property="og:image" content="https://cdn.example.com/thumb.jpg" />
            <meta property="og:video" content="https://cdn.example.com/reel.mp4" />
        </html>
        ''',
        'html.parser'
    )

    monkeypatch.setattr(extractor, '_make_request', lambda url: soup)

    result = extractor._extract_instagram('https://www.instagram.com/reel/demo123/')

    assert result['success'] is True
    assert result['media_type'] == 'reel'
    assert result['media_url'] == 'https://cdn.example.com/reel.mp4'
    assert result['image_url'] == 'https://cdn.example.com/thumb.jpg'
    assert result['media_extraction_status'] == 'direct_media_found'
    assert result['media_extraction_error'] == ''


def test_instagram_reel_falls_back_to_ytdlp_when_meta_video_missing(monkeypatch):
    extractor = ContentExtractor()
    soup = BeautifulSoup(
        '''
        <html>
            <meta property="og:description" content="Watch this coding reel" />
            <meta property="og:image" content="https://cdn.example.com/thumb.jpg" />
        </html>
        ''',
        'html.parser'
    )

    monkeypatch.setattr(extractor, '_make_request', lambda url: soup)
    monkeypatch.setattr(
        extractor,
        '_extract_with_ytdlp',
        lambda url: {
            'title': 'Debugging reel',
            'caption': 'Three Python debugging mistakes',
            'image_url': 'https://cdn.example.com/fallback.jpg',
            'author': 'creator',
            'media_url': 'https://cdn.example.com/fallback.mp4',
            'media_type': 'reel',
            'media_extraction_status': 'yt_dlp_success',
            'media_extraction_error': '',
        }
    )

    result = extractor._extract_instagram('https://www.instagram.com/reel/demo123/')

    assert result['media_url'] == 'https://cdn.example.com/fallback.mp4'
    assert result['media_type'] == 'reel'
    assert result['media_extraction_status'] == 'yt_dlp_success'
    assert result['media_extraction_error'] == ''


def test_resolve_ytdlp_cookie_file_supports_relative_paths(monkeypatch):
    extractor = ContentExtractor()
    monkeypatch.setattr(extractor_module.Config, 'YTDLP_COOKIES_FILE', os.path.join('cookies', 'instagram.txt'))

    resolved = extractor._resolve_ytdlp_cookie_file()

    assert resolved.endswith(os.path.join('cookies', 'instagram.txt'))


def test_ytdlp_reports_missing_cookies_file(monkeypatch):
    extractor = ContentExtractor()
    monkeypatch.setattr(extractor_module.Config, 'YTDLP_ENABLED', True)
    monkeypatch.setattr(extractor_module.Config, 'YTDLP_COOKIES_FILE', 'missing-cookies.txt')
    monkeypatch.setattr(extractor_module, 'YoutubeDL', object())

    result = extractor._extract_with_ytdlp('https://www.instagram.com/reel/demo123/')

    assert result['media_extraction_status'] == 'cookies_file_missing'
    assert 'missing-cookies.txt' in result['media_extraction_error']


@pytest.mark.parametrize(
    ('error_message', 'expected_status'),
    [
        ('Login required to view this content. Use --cookies.', 'login_required'),
        ('HTTP Error 429: Too Many Requests', 'rate_limited'),
        ('Unsupported URL: https://example.com/demo', 'unsupported_extractor'),
    ]
)
def test_ytdlp_classifies_common_failure_modes(monkeypatch, error_message, expected_status):
    extractor = ContentExtractor()

    class RaisingYDL:
        def __init__(self, options):
            self.options = options

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def extract_info(self, url, download=False):
            raise Exception(error_message)

    monkeypatch.setattr(extractor_module.Config, 'YTDLP_ENABLED', True)
    monkeypatch.setattr(extractor_module.Config, 'YTDLP_COOKIES_FILE', '')
    monkeypatch.setattr(extractor_module, 'YoutubeDL', RaisingYDL)

    result = extractor._extract_with_ytdlp('https://www.instagram.com/reel/demo123/')

    assert result['media_extraction_status'] == expected_status
    assert result['media_extraction_error']
