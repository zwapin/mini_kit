# IMPORTING THIRD PARTY PACKAGES
from rest_framework import status


def error_body(code: str, message: str) -> dict:
    """Build the standard error payload: {"error": {"code": ..., "message": ...}}."""
    return {"error": {"code": code, "message": message}}


class KitError(Exception):
    """
    Base class of every error a manager can raise.

    Raise it (never return it): the kit exception handler turns it into an HTTP response with
    `http_status` and the standard error body. Define domain errors as subclasses that override
    `code` and `default_message`, e.g.:

        class NoteNotFoundError(NotFoundError):
            code = "note_not_found"
            default_message = "Note not found"

    Pass a message to the constructor only when it must carry runtime details.
    """

    http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_error"
    default_message: str = "Internal server error"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class InvalidPayloadError(KitError):
    """400: the request data is well-formed JSON but breaks a rule."""

    http_status = status.HTTP_400_BAD_REQUEST
    code = "invalid_payload"
    default_message = "Invalid payload"


class NotFoundError(KitError):
    """404: the resource does not exist, or belongs to another team."""

    http_status = status.HTTP_404_NOT_FOUND
    code = "not_found"
    default_message = "Resource not found"


class ConflictError(KitError):
    """409: the request is valid but clashes with the current state (duplicates, closed resources...)."""

    http_status = status.HTTP_409_CONFLICT
    code = "conflict"
    default_message = "The request conflicts with the current state of the resource"
