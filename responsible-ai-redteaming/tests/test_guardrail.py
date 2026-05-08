'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from unittest.mock import patch, MagicMock
from app.utility.guardrail import ModerationHandler


def test_moderation_missing_url(monkeypatch):
    monkeypatch.delenv('MODERATION_API', raising=False)
    handler = ModerationHandler(moderation_url=None)
    res = handler.check_moderation("hello")
    assert res['moderationResults']['summary']['status'] == 'FAILED'
    assert 'not configured' in res['moderationResults']['summary']['reason'][0].lower()


@patch('app.utility.guardrail.requests.post')
def test_moderation_success(mock_post):
    mock_resp = MagicMock(status_code=200, json=lambda: {"ok": True})
    mock_post.return_value = mock_resp
    handler = ModerationHandler(moderation_url="https://example.com/mod")
    out = handler.check_moderation("test prompt")
    assert out == {"ok": True}
    mock_post.assert_called_once()


@patch('app.utility.guardrail.requests.post')
def test_moderation_http_error(mock_post):
    mock_resp = MagicMock(status_code=500, text='err', json=lambda: {})
    mock_post.return_value = mock_resp
    handler = ModerationHandler(moderation_url="https://example.com/mod")
    out = handler.check_moderation("test prompt")
    assert out['moderationResults']['summary']['status'] == 'FAILED'
    assert '500' in out['moderationResults']['summary']['reason'][0]


@patch('app.utility.guardrail.requests.post')
def test_moderation_invalid_json(mock_post):
    def _raise():
        raise ValueError('bad json')
    mock_resp = MagicMock(status_code=200)
    mock_resp.json = _raise
    mock_post.return_value = mock_resp
    handler = ModerationHandler(moderation_url="https://example.com/mod")
    out = handler.check_moderation("test prompt")
    assert out['moderationResults']['summary']['status'] == 'FAILED'
    assert 'invalid json' in out['moderationResults']['summary']['reason'][0].lower()
