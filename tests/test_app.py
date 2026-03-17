import app as app_module


def test_whatsapp_webhook_acknowledges_url_immediately(monkeypatch):
    captured = {}

    monkeypatch.setattr(app_module, 'check_duplicate', lambda url: None)

    def fake_start(url, from_phone, base_url):
        captured['url'] = url
        captured['from_phone'] = from_phone
        captured['base_url'] = base_url

    monkeypatch.setattr(app_module, 'start_whatsapp_url_processing', fake_start)

    client = app_module.app.test_client()
    response = client.post(
        '/whatsapp/webhook',
        data={
            'Body': 'save this https://www.instagram.com/reel/demo123/',
            'From': 'whatsapp:+911234567890'
        }
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Processing your URL now. I'll send the result shortly." in body
    assert captured['url'] == 'https://www.instagram.com/reel/demo123/'
    assert captured['from_phone'] == 'whatsapp:+911234567890'
    assert captured['base_url'].startswith('http://localhost')
