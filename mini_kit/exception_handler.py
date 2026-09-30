# IMPORTING STANDARD PACKAGES
import logging

# IMPORTING THIRD PARTY PACKAGES
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    ParseError,
    ValidationError,
)
from rest_framework.response import Response

# IMPORTING LOCAL PACKAGES
from mini_kit.errors import InvalidPayloadError, KitError, NotFoundError, error_body

logger = logging.getLogger(__name__)

UNAUTHORIZED_CODE = "unauthorized"
MISSING_TOKEN_MESSAGE = "Missing token: send the 'Authorization: Token <jwt>' header"


def kit_exception_handler(exc: Exception, context: dict) -> Response:
    """
    DRF exception handler (settings.REST_FRAMEWORK["EXCEPTION_HANDLER"]).

    Every exception raised while handling a request ends up here and leaves as the standard error
    body, so views and managers never build error responses by hand:

    - KitError subclasses          -> their own http_status and code
    - serializer errors, bad JSON  -> 400 invalid_payload, message names the first invalid field
    - missing or invalid token     -> 401 unauthorized
    - other DRF errors (405, 415)  -> their status, DRF code
    - anything else                -> logged, 500 internal_error
    """
    if isinstance(exc, KitError):
        return _error_response(exc.http_status, exc.code, exc.message)
    if isinstance(exc, (ValidationError, ParseError)):
        return _error_response(InvalidPayloadError.http_status, InvalidPayloadError.code, _first_message(exc.detail))
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return _unauthorized_response(exc)
    if isinstance(exc, Http404):
        return _error_response(NotFoundError.http_status, NotFoundError.code, NotFoundError.default_message)
    if isinstance(exc, APIException):
        return _error_response(exc.status_code, exc.default_code, _first_message(exc.detail))
    logger.exception("Unhandled exception in %s", type(context["view"]).__name__)
    return _error_response(KitError.http_status, KitError.code, KitError.default_message)


def _error_response(http_status: int, code: str, message: str, headers: dict | None = None) -> Response:
    return Response(error_body(code, message), status=http_status, headers=headers)


def _unauthorized_response(exc: NotAuthenticated | AuthenticationFailed) -> Response:
    message = MISSING_TOKEN_MESSAGE if isinstance(exc, NotAuthenticated) else str(exc.detail)
    headers = {"WWW-Authenticate": exc.auth_header} if getattr(exc, "auth_header", None) else None
    return _error_response(status.HTTP_401_UNAUTHORIZED, UNAUTHORIZED_CODE, message, headers)


def _first_message(detail: dict | list | str) -> str:
    # DRF errors are nested dicts/lists ({"email": ["Enter a valid email address."]}): keep the first one.
    if isinstance(detail, dict):
        field, errors = next(iter(detail.items()))
        return f"{field}: {_first_message(errors)}"
    if isinstance(detail, list):
        return _first_message(detail[0])
    return str(detail)
