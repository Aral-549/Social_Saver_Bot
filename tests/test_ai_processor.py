from ai_processor import AIProcessor


def test_summarize_content_prefers_video_analysis(monkeypatch):
    processor = AIProcessor()
    processor.gemini_api_key = 'test-key'
    processor.groq_api_key = ''

    monkeypatch.setattr(
        processor,
        '_summarize_youtube_video',
        lambda *args, **kwargs: 'A developer walks through fixing a Flask API bug in real time.'
    )

    summary, source = processor.summarize_content(
        url='https://www.youtube.com/watch?v=abc123',
        title='Debugging a Flask API',
        caption='Fixing a production issue',
        platform='youtube',
        media_url='https://www.youtube.com/watch?v=abc123',
        media_type='video',
        image_url=''
    )

    assert source == 'video'
    assert summary == 'A developer walks through fixing a Flask API bug in real time.'


def test_summarize_content_falls_back_to_metadata(monkeypatch):
    processor = AIProcessor()
    processor.gemini_api_key = ''

    monkeypatch.setattr(
        processor,
        '_call_groq',
        lambda prompt: 'A creator explains three Python debugging mistakes and how to avoid them.'
    )

    summary, source = processor.summarize_content(
        url='https://www.instagram.com/reel/example/',
        title='Python Debugging Tips',
        caption='Three mistakes beginners make',
        platform='instagram',
        media_url='',
        media_type='reel',
        image_url=''
    )

    assert source == 'metadata_no_video'
    assert summary == 'A creator explains three Python debugging mistakes and how to avoid them.'


def test_reel_summary_does_not_fallback_to_thumbnail(monkeypatch):
    processor = AIProcessor()
    processor.gemini_api_key = 'test-key'
    processor.groq_api_key = ''

    monkeypatch.setattr(processor, '_summarize_uploaded_media', lambda *args, **kwargs: 'A person speaks to camera from a still image.')
    monkeypatch.setattr(processor, '_call_groq', lambda prompt: 'A creator explains three Python debugging mistakes and how to avoid them.')

    summary, source = processor.summarize_content(
        url='https://www.instagram.com/reel/example/',
        title='Python Debugging Tips',
        caption='Three mistakes beginners make',
        platform='instagram',
        media_url='',
        media_type='reel',
        image_url='https://example.com/thumb.jpg'
    )

    assert source == 'metadata_no_video'
    assert summary == 'A creator explains three Python debugging mistakes and how to avoid them.'


def test_clean_summary_keeps_complete_sentences_without_ellipsis():
    processor = AIProcessor()
    text = (
        "Akaash Singh performs stand-up comedy and jokes about a man's casual outfit. "
        "He asks whether the man knew he was going out and learns that he is Indian, married, a choreographer, and a lawyer. "
        "Singh keeps teasing him about his style while the crowd laughs."
    )

    summary = processor._clean_summary(text, max_words=20, complete_sentences=True)

    assert summary == "Akaash Singh performs stand-up comedy and jokes about a man's casual outfit."
    assert '...' not in summary
