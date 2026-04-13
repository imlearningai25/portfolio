"""
Unit tests for the Portfolio Flask application.

Run with:
    python -m pytest tests/test_app.py -v
    # or
    python -m unittest tests/test_app.py -v
"""

import json
import unittest
from unittest.mock import patch, MagicMock

# Suppress prometheus_flask_exporter duplicate registration warnings in tests
import os
os.environ.setdefault('TESTING', 'true')

from app import app


VALID_PAYLOAD = {
    'name':    'John Doe',
    'email':   'john@example.com',
    'subject': 'Hello',
    'message': 'This is a test message.',
}


class TestIndexRoute(unittest.TestCase):
    """Tests for GET /"""

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    # ── Test 1 ──────────────────────────────────────────────────────────
    def test_index_returns_200(self):
        """Homepage responds with HTTP 200."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    # ── Test 2 ──────────────────────────────────────────────────────────
    def test_index_returns_html(self):
        """Homepage content-type is HTML."""
        response = self.client.get('/')
        self.assertIn('text/html', response.content_type)

    # ── Test 3 ──────────────────────────────────────────────────────────
    def test_index_body_not_empty(self):
        """Homepage response body is non-empty."""
        response = self.client.get('/')
        self.assertGreater(len(response.data), 0)

    # ── Test 4 ──────────────────────────────────────────────────────────
    def test_index_get_only(self):
        """POST to / is not allowed (405)."""
        response = self.client.post('/')
        self.assertEqual(response.status_code, 405)


class TestContactRoute(unittest.TestCase):
    """Tests for POST /contact"""

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def _post(self, payload):
        return self.client.post(
            '/contact',
            data=json.dumps(payload),
            content_type='application/json',
        )

    # ── Test 5 ──────────────────────────────────────────────────────────
    @patch('app.mail.send')
    def test_contact_valid_payload_returns_200(self, mock_send):
        """Valid contact form returns HTTP 200."""
        response = self._post(VALID_PAYLOAD)
        self.assertEqual(response.status_code, 200)

    # ── Test 6 ──────────────────────────────────────────────────────────
    @patch('app.mail.send')
    def test_contact_valid_payload_success_true(self, mock_send):
        """Valid contact form returns success=True."""
        response = self._post(VALID_PAYLOAD)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    # ── Test 7 ──────────────────────────────────────────────────────────
    @patch('app.mail.send')
    def test_contact_valid_payload_has_message_key(self, mock_send):
        """Valid response body contains a 'message' key."""
        response = self._post(VALID_PAYLOAD)
        data = json.loads(response.data)
        self.assertIn('message', data)

    # ── Test 8 ──────────────────────────────────────────────────────────
    @patch('app.mail.send')
    def test_contact_calls_mail_send_once(self, mock_send):
        """mail.send() is called exactly once on a valid submission."""
        self._post(VALID_PAYLOAD)
        mock_send.assert_called_once()

    # ── Test 9 ──────────────────────────────────────────────────────────
    def test_contact_missing_name_returns_400(self):
        """Missing 'name' field returns HTTP 400."""
        payload = {**VALID_PAYLOAD, 'name': ''}
        response = self._post(payload)
        self.assertEqual(response.status_code, 400)

    # ── Test 10 ─────────────────────────────────────────────────────────
    def test_contact_missing_email_returns_400(self):
        """Missing 'email' field returns HTTP 400."""
        payload = {**VALID_PAYLOAD, 'email': ''}
        response = self._post(payload)
        self.assertEqual(response.status_code, 400)

    # ── Test 11 ─────────────────────────────────────────────────────────
    def test_contact_missing_subject_returns_400(self):
        """Missing 'subject' field returns HTTP 400."""
        payload = {**VALID_PAYLOAD, 'subject': ''}
        response = self._post(payload)
        self.assertEqual(response.status_code, 400)

    # ── Test 12 ─────────────────────────────────────────────────────────
    def test_contact_missing_message_returns_400(self):
        """Missing 'message' field returns HTTP 400."""
        payload = {**VALID_PAYLOAD, 'message': ''}
        response = self._post(payload)
        self.assertEqual(response.status_code, 400)

    # ── Test 13 ─────────────────────────────────────────────────────────
    def test_contact_all_fields_empty_returns_400(self):
        """All-empty payload returns HTTP 400."""
        response = self._post({'name': '', 'email': '', 'subject': '', 'message': ''})
        self.assertEqual(response.status_code, 400)

    # ── Test 14 ─────────────────────────────────────────────────────────
    def test_contact_whitespace_only_name_returns_400(self):
        """Whitespace-only name is treated as missing (strip() removes it)."""
        payload = {**VALID_PAYLOAD, 'name': '   '}
        response = self._post(payload)
        self.assertEqual(response.status_code, 400)

    # ── Test 15 ─────────────────────────────────────────────────────────
    def test_contact_whitespace_only_message_returns_400(self):
        """Whitespace-only message is treated as missing."""
        payload = {**VALID_PAYLOAD, 'message': '\t\n  '}
        response = self._post(payload)
        self.assertEqual(response.status_code, 400)

    # ── Test 16 ─────────────────────────────────────────────────────────
    def test_contact_missing_field_error_message(self):
        """400 response body contains a descriptive 'error' key."""
        response = self._post({**VALID_PAYLOAD, 'name': ''})
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertFalse(data['success'])

    # ── Test 17 ─────────────────────────────────────────────────────────
    def test_contact_extra_fields_ignored(self):
        """Extra fields in the payload do not cause an error."""
        payload = {**VALID_PAYLOAD, 'honeypot': 'bot', 'extra': 123}
        with patch('app.mail.send'):
            response = self._post(payload)
        self.assertEqual(response.status_code, 200)

    # ── Test 18 ─────────────────────────────────────────────────────────
    def test_contact_response_is_json(self):
        """Contact endpoint always returns JSON content-type."""
        response = self._post(VALID_PAYLOAD)
        self.assertIn('application/json', response.content_type)

    # ── Test 19 ─────────────────────────────────────────────────────────
    def test_contact_get_not_allowed(self):
        """GET /contact is not allowed (405)."""
        response = self.client.get('/contact')
        self.assertEqual(response.status_code, 405)

    # ── Test 20 ─────────────────────────────────────────────────────────
    @patch('app.mail.send', side_effect=Exception('Authentication failed'))
    def test_contact_auth_error_returns_500(self, mock_send):
        """SMTP authentication error returns HTTP 500."""
        response = self._post(VALID_PAYLOAD)
        self.assertEqual(response.status_code, 500)

    # ── Test 21 ─────────────────────────────────────────────────────────
    @patch('app.mail.send', side_effect=Exception('Authentication failed'))
    def test_contact_auth_error_friendly_message(self, mock_send):
        """Authentication errors return a user-friendly error string."""
        response = self._post(VALID_PAYLOAD)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('not configured', data['error'])

    # ── Test 22 ─────────────────────────────────────────────────────────
    @patch('app.mail.send', side_effect=Exception('Username and Password not accepted'))
    def test_contact_username_error_friendly_message(self, mock_send):
        """'Username' in exception message triggers the friendly error path."""
        response = self._post(VALID_PAYLOAD)
        data = json.loads(response.data)
        self.assertIn('not configured', data['error'])

    # ── Test 23 ─────────────────────────────────────────────────────────
    @patch('app.mail.send', side_effect=Exception('Connection timed out'))
    def test_contact_generic_smtp_error_returns_500(self, mock_send):
        """Non-auth SMTP errors return a generic 500 error."""
        response = self._post(VALID_PAYLOAD)
        self.assertEqual(response.status_code, 500)

    # ── Test 24 ─────────────────────────────────────────────────────────
    @patch('app.mail.send', side_effect=Exception('Connection timed out'))
    def test_contact_generic_smtp_error_message(self, mock_send):
        """Generic SMTP error returns the generic error text, not the auth message."""
        response = self._post(VALID_PAYLOAD)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertNotIn('not configured', data['error'])

    # ── Test 25 ─────────────────────────────────────────────────────────
    @patch('app.mail.send', side_effect=Exception('bad password'))
    def test_contact_password_keyword_triggers_friendly_message(self, mock_send):
        """'password' (lowercase) in exception triggers the friendly error path."""
        response = self._post(VALID_PAYLOAD)
        data = json.loads(response.data)
        self.assertIn('not configured', data['error'])


class TestMetricsRoute(unittest.TestCase):
    """Tests for GET /metrics (Prometheus endpoint)"""

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    # ── Test 26 ─────────────────────────────────────────────────────────
    def test_metrics_returns_200(self):
        """/metrics endpoint responds with HTTP 200."""
        response = self.client.get('/metrics')
        self.assertEqual(response.status_code, 200)

    # ── Test 27 ─────────────────────────────────────────────────────────
    def test_metrics_content_type_is_text(self):
        """/metrics returns plain text (Prometheus exposition format)."""
        response = self.client.get('/metrics')
        self.assertIn('text/plain', response.content_type)

    # ── Test 28 ─────────────────────────────────────────────────────────
    def test_metrics_contains_flask_http_request_total(self):
        """/metrics output includes the flask_http_request_total counter."""
        self.client.get('/')  # generate at least one request first
        response = self.client.get('/metrics')
        self.assertIn(b'flask_http_request_total', response.data)

    # ── Test 29 ─────────────────────────────────────────────────────────
    def test_metrics_contains_app_info(self):
        """/metrics output includes the custom app_info gauge."""
        response = self.client.get('/metrics')
        self.assertIn(b'app_info', response.data)


class TestNotFoundRoute(unittest.TestCase):
    """Tests for non-existent routes"""

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    # ── Test 30 ─────────────────────────────────────────────────────────
    def test_unknown_route_returns_404(self):
        """Requesting a non-existent path returns HTTP 404."""
        response = self.client.get('/does-not-exist')
        self.assertEqual(response.status_code, 404)


class TestAppConfig(unittest.TestCase):
    """Tests for application configuration"""

    # ── Test 31 ─────────────────────────────────────────────────────────
    def test_mail_server_is_gmail(self):
        """MAIL_SERVER is configured to use Gmail SMTP."""
        self.assertEqual(app.config['MAIL_SERVER'], 'smtp.gmail.com')

    # ── Test 32 ─────────────────────────────────────────────────────────
    def test_mail_port_is_587(self):
        """MAIL_PORT is 587 (STARTTLS)."""
        self.assertEqual(app.config['MAIL_PORT'], 587)

    # ── Test 33 ─────────────────────────────────────────────────────────
    def test_mail_use_tls_is_true(self):
        """MAIL_USE_TLS is enabled."""
        self.assertTrue(app.config['MAIL_USE_TLS'])

    # ── Test 34 ─────────────────────────────────────────────────────────
    def test_secret_key_is_set(self):
        """SECRET_KEY is non-empty."""
        self.assertTrue(app.config['SECRET_KEY'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
