import logging
import socket
import ssl
import time
from urllib.parse import urlparse

import httpx
from retry import retry
from pydantic import BaseModel
from config import config

logger = logging.getLogger(__name__)

RESPONSE_BODY_LOG_LIMIT = 500


class CertificatesOnSolanaException(Exception):
    """Custom exception for CertificatesOnSolana errors."""

    def __init__(
        self,
        message: str = "Error registering certificate on Solana",
        details: str = "",
        cause: Exception = None,
        stage: str = "unexpected",
    ):
        super().__init__(f"{message} [stage={stage}]: {details}")
        self.details = details
        self.cause = cause
        self.stage = stage


def _exception_chain(exc: BaseException) -> list:
    """Return exc followed by its __cause__/__context__ chain."""
    chain = []
    while exc is not None and exc not in chain:
        chain.append(exc)
        exc = exc.__cause__ or exc.__context__
    return chain


def _classify_error(exc: BaseException) -> str:
    """Name the layer where the registration failed."""
    chain = _exception_chain(exc)
    if any(isinstance(e, socket.gaierror) for e in chain):
        return "dns"
    if any(isinstance(e, ssl.SSLError) for e in chain):
        return "tls"
    if isinstance(exc, httpx.TimeoutException):
        return "timeout"
    if isinstance(exc, httpx.ConnectError):
        return "connect"
    if isinstance(exc, httpx.HTTPStatusError):
        if exc.response.status_code in (401, 403):
            return "auth"
        return "http_status"
    if isinstance(exc, httpx.RequestError):
        return "network"
    if isinstance(exc, ValueError):
        return "response_parse"
    return "unexpected"


def _describe_chain(exc: BaseException) -> str:
    return " <- ".join(
        f"{type(e).__module__}.{type(e).__name__}(errno={getattr(e, 'errno', None)})"
        for e in _exception_chain(exc)
    )


class CertificatesOnSolana:
    """
    A class to manage certificates on the Solana blockchain Service."""

    @staticmethod
    @retry(
        tries=3,
        delay=3,
        backoff=2,
        exceptions=(httpx.RequestError, CertificatesOnSolanaException, Exception),
        logger=logger,
    )
    def register_certificate_on_solana(certificate_data: dict) -> dict:
        """
        Registers a certificate on the Solana blockchain.

        Args:
            certificate_data (dict): A dictionary containing certificate details.

        Returns:
            dict: A dictionary with the registration result.
        """
        target = urlparse(config.SERVICE_URL_REGISTRATION_API_SOLANA)
        logger.info(
            "Registering certificate on Solana: host=%s path=%s certificate_code=%s event=%s",
            target.netloc,
            target.path,
            certificate_data.get("certificate_code"),
            certificate_data.get("event"),
        )
        started = time.monotonic()
        response = None
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    url=config.SERVICE_URL_REGISTRATION_API_SOLANA,
                    headers={
                        "x-api-key": config.SERVICE_API_KEY_REGISTRATION_API_SOLANA,
                        "Content-Type": "application/json",
                    },
                    json=certificate_data,
                )
                logger.info(f"Solana response status code: {response.status_code}")
                response.raise_for_status()
                solana_response = response.json()
                return solana_response
        except Exception as e:
            stage = _classify_error(e)
            status = getattr(response, "status_code", None)
            body = response.text[:RESPONSE_BODY_LOG_LIMIT] if response is not None else None
            logger.exception(
                "Error registering certificate on Solana: stage=%s host=%s elapsed_ms=%d "
                "status=%s certificate_code=%s chain=%s body=%s",
                stage,
                target.netloc,
                (time.monotonic() - started) * 1000,
                status,
                certificate_data.get("certificate_code"),
                _describe_chain(e),
                body,
            )
            raise CertificatesOnSolanaException(details=str(e), cause=e, stage=stage)
