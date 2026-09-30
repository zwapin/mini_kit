# IMPORTING STANDARD PACKAGES
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticatedUser:
    """
    The caller of a request, decoded from its token and exposed as `request.user`.

    There is no user table: the token is the only source of `user_pk` and `team_pk`.
    """

    user_pk: int
    team_pk: int

    @property
    def is_authenticated(self) -> bool:
        return True
