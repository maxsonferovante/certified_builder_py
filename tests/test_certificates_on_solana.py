import pytest
from unittest.mock import patch, MagicMock
from certified_builder.certificates_on_solana import (
    CertificatesOnSolana,
    CertificatesOnSolanaException,
)
from certified_builder import certificates_on_solana as module_under_test


@pytest.fixture
def sample_payload():
    return {
        "name": "User Test",
        "event": "Evento X",
        "email": "user@example.com",
        "certificate_code": "ABC-123-XYZ",
    }


def test_register_certificate_success(sample_payload, monkeypatch):
    # Configura URLs/chaves do módulo
    monkeypatch.setattr(
        module_under_test.config,
        "SERVICE_URL_REGISTRATION_API_SOLANA",
        "https://api.test/solana",
    )
    monkeypatch.setattr(
        module_under_test.config,
        "SERVICE_API_KEY_REGISTRATION_API_SOLANA",
        "secret-key",
    )

    # Mock do client httpx
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ok": True,
        "blockchain": {"verificacao_url": "https://verify"},
    }
    mock_response.raise_for_status.return_value = None

    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.__exit__.return_value = False

    with patch(
        "certified_builder.certificates_on_solana.httpx.Client",
        return_value=mock_client_instance,
    ) as mock_client_cls:
        result = CertificatesOnSolana.register_certificate_on_solana(sample_payload)

        # Retorno
        assert result["ok"] is True
        assert result["blockchain"]["verificacao_url"] == "https://verify"

        # Chamada correta
        mock_client_cls.assert_called_once()
        mock_client_instance.post.assert_called_once()
        call_kwargs = mock_client_instance.post.call_args.kwargs
        assert call_kwargs["url"] == "https://api.test/solana"
        assert call_kwargs["headers"]["x-api-key"] == "secret-key"
        assert call_kwargs["headers"]["Content-Type"] == "application/json"
        assert call_kwargs["json"] == sample_payload


def test_register_certificate_http_error_raises(sample_payload, monkeypatch):
    monkeypatch.setattr(
        module_under_test.config,
        "SERVICE_URL_REGISTRATION_API_SOLANA",
        "https://api.test/solana",
    )
    monkeypatch.setattr(
        module_under_test.config,
        "SERVICE_API_KEY_REGISTRATION_API_SOLANA",
        "secret-key",
    )

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"ok": False}

    # raise_for_status levanta erro
    def _raise():
        raise Exception("boom")

    mock_response.raise_for_status.side_effect = _raise

    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.__exit__.return_value = False

    with patch(
        "certified_builder.certificates_on_solana.httpx.Client",
        return_value=mock_client_instance,
    ):
        with pytest.raises(CertificatesOnSolanaException) as exc:
            CertificatesOnSolana.register_certificate_on_solana(sample_payload)

        assert "boom" in str(exc.value.details)


@pytest.fixture
def no_retry_sleep(monkeypatch):
    import retry.api

    monkeypatch.setattr(retry.api.time, "sleep", lambda _: None)


def _client_raising_on_post(error):
    mock_client_instance = MagicMock()
    mock_client_instance.post.side_effect = error
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.__exit__.return_value = False
    return mock_client_instance


def test_register_certificate_dns_failure_stage(sample_payload, no_retry_sleep):
    import socket
    import httpx

    dns_error = httpx.ConnectError("[Errno -2] Name or service not known")
    dns_error.__cause__ = socket.gaierror(-2, "Name or service not known")

    with patch(
        "certified_builder.certificates_on_solana.httpx.Client",
        return_value=_client_raising_on_post(dns_error),
    ):
        with pytest.raises(CertificatesOnSolanaException) as exc:
            CertificatesOnSolana.register_certificate_on_solana(sample_payload)

    assert exc.value.stage == "dns"
    assert "[stage=dns]" in str(exc.value)


def test_register_certificate_auth_failure_stage(sample_payload, no_retry_sleep):
    import httpx

    request = httpx.Request("POST", "https://example.test/solana/register")
    response = httpx.Response(401, request=request, json={"detail": "Invalid API Key"})

    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = response
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.__exit__.return_value = False

    with patch(
        "certified_builder.certificates_on_solana.httpx.Client",
        return_value=mock_client_instance,
    ):
        with pytest.raises(CertificatesOnSolanaException) as exc:
            CertificatesOnSolana.register_certificate_on_solana(sample_payload)

    assert exc.value.stage == "auth"


def test_register_certificate_failure_log_has_no_secrets(
    sample_payload, no_retry_sleep, caplog
):
    import httpx

    with patch(
        "certified_builder.certificates_on_solana.httpx.Client",
        return_value=_client_raising_on_post(httpx.ConnectError("refused")),
    ):
        with pytest.raises(CertificatesOnSolanaException):
            CertificatesOnSolana.register_certificate_on_solana(sample_payload)

    assert "stage=connect" in caplog.text
    assert "test-api-key" not in caplog.text
    assert sample_payload["email"] not in caplog.text
    assert sample_payload["name"] not in caplog.text
