# IMPORTING THIRD PARTY PACKAGES
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

# IMPORTING LOCAL PACKAGES
from mini_kit.auth.tokens import InvalidTokenError, decode_token
from mini_kit.auth.user import AuthenticatedUser


class TokenAuthentication(BaseAuthentication):
    """
    DRF authentication for the `Authorization: Token <jwt>` header.

    - no header (or another scheme): returns None, then the IsAuthenticated permission answers 401
    - invalid token: raises AuthenticationFailed with the reason, answered as 401
    - valid token: request.user becomes an AuthenticatedUser(user_pk, team_pk)
    """

    keyword = "Token"

    def authenticate(self, request: Request) -> tuple[AuthenticatedUser, str] | None:
        token = self._extract_token(request)
        if token is None:
            return None
        try:
            return decode_token(token), token
        except InvalidTokenError as error:
            raise AuthenticationFailed(str(error)) from error

    def authenticate_header(self, request: Request) -> str:
        # Returning a value makes DRF answer 401 (with WWW-Authenticate) instead of 403.
        return self.keyword

    def _extract_token(self, request: Request) -> str | None:
        parts = request.META.get("HTTP_AUTHORIZATION", "").split()
        if not parts or parts[0].lower() != self.keyword.lower():
            return None
        if len(parts) != 2:
            raise AuthenticationFailed(f"Malformed Authorization header: expected '{self.keyword} <jwt>'")
        return parts[1]
