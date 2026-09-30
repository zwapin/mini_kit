# IMPORTING STANDARD PACKAGES
from datetime import datetime, timedelta, timezone

# IMPORTING THIRD PARTY PACKAGES
import jwt
from django.conf import settings

# IMPORTING LOCAL PACKAGES
from mini_kit.auth.user import AuthenticatedUser

ALGORITHM = "HS256"
REQUIRED_CLAIMS = ["user_pk", "team_pk"]


class InvalidTokenError(Exception):
    """The token cannot be trusted: bad signature, expired, missing or malformed claims."""


def issue_token(user_pk: int, team_pk: int, expires_in: timedelta | None = None) -> str:
    """
    Sign a JWT for a user of a team with settings.MINI_KIT_JWT_SECRET.

    Without `expires_in` the token never expires. Used by the `issue_token` management command
    and by KitAPITestCase.as_user().
    """
    issued_at = datetime.now(tz=timezone.utc)
    payload = {"user_pk": user_pk, "team_pk": team_pk, "iat": issued_at}
    if expires_in is not None:
        payload["exp"] = issued_at + expires_in
    return jwt.encode(payload, settings.MINI_KIT_JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> AuthenticatedUser:
    """Verify a token and return its caller. Raises InvalidTokenError when it cannot be trusted."""
    payload = _decode_payload(token)
    user_pk, team_pk = payload["user_pk"], payload["team_pk"]
    if not (_is_pk(user_pk) and _is_pk(team_pk)):
        raise InvalidTokenError("Invalid token: user_pk and team_pk must be positive integers")
    return AuthenticatedUser(user_pk=user_pk, team_pk=team_pk)


def _decode_payload(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.MINI_KIT_JWT_SECRET,
            algorithms=[ALGORITHM],
            options={"require": REQUIRED_CLAIMS},
        )
    except jwt.ExpiredSignatureError as error:
        raise InvalidTokenError("Expired token") from error
    except jwt.MissingRequiredClaimError as error:
        raise InvalidTokenError(f"Invalid token: missing claim '{error.claim}'") from error
    except jwt.InvalidTokenError as error:
        raise InvalidTokenError("Invalid token") from error


def _is_pk(value: object) -> bool:
    # type() instead of isinstance(): bool is a subclass of int and must not pass as a pk.
    return type(value) is int and value > 0
