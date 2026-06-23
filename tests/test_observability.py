"""Unit tests for request logging and the error boundary's 500 handling."""

import logging

import pytest

from randomgen.app import create_app


@pytest.fixture
def client():
    return create_app().test_client()


class TestRequestLogging:
    def test_request_emits_single_access_log_line(self, client, caplog):
        with caplog.at_level(logging.INFO):
            response = client.get('/health')

        assert response.status_code == 200
        access_lines = [r for r in caplog.records if 'GET /health 200' in r.getMessage()]
        assert len(access_lines) == 1

    def test_access_line_includes_client_address(self, client, caplog):
        with caplog.at_level(logging.INFO):
            client.get('/health')

        access_lines = [r for r in caplog.records if 'GET /health 200' in r.getMessage()]
        assert access_lines
        # The test client's default remote address leads the line.
        assert access_lines[0].getMessage().startswith('127.0.0.1 ')

    def test_static_asset_request_is_not_logged(self, client, caplog):
        with caplog.at_level(logging.INFO):
            response = client.get('/static/css/style.css')

        assert response.status_code == 200
        static_lines = [r for r in caplog.records if '/static/' in r.getMessage()]
        assert static_lines == []


class TestValidationLogging:
    def test_rejected_request_logs_cause_at_warning(self, client, caplog):
        # Probabilities that do not sum to 1 -> a domain validation rejection.
        with caplog.at_level(logging.INFO):
            response = client.get('/api/v1/randomgen?dist=1:0.2,2:0.2')

        assert response.status_code == 400

        # The cause is logged once, at WARNING, naming the rule that failed.
        warnings = [
            r
            for r in caplog.records
            if r.levelno == logging.WARNING and 'Rejected' in r.getMessage()
        ]
        assert len(warnings) == 1
        assert 'Probabilities must sum to 1.' in warnings[0].getMessage()

        # The bare access line is still emitted exactly once alongside it.
        access_lines = [r for r in caplog.records if 'GET /api/v1/randomgen 400' in r.getMessage()]
        assert len(access_lines) == 1


class TestErrorBoundaryLogging:
    def test_unexpected_error_returns_generic_500_without_leaking_detail(
        self, client, caplog, monkeypatch
    ):
        def _boom(*args, **kwargs):
            raise RuntimeError('secret internal detail')

        monkeypatch.setattr('randomgen.blueprints.api.service.generate', _boom)

        with caplog.at_level(logging.INFO):
            response = client.get('/api/v1/randomgen')

        # The client sees a generic message, never the internal detail.
        assert response.status_code == 500
        assert response.get_json() == {'error': 'Internal Server Error'}
        assert 'secret internal detail' not in response.get_data(as_text=True)

        # The detail is logged in full (with the traceback) for diagnosis.
        errors = [r for r in caplog.records if 'Unhandled error' in r.getMessage()]
        assert errors
        assert errors[0].levelno == logging.ERROR
        assert errors[0].exc_info is not None
