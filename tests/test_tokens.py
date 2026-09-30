# IMPORTING STANDARD PACKAGES
from datetime import timedelta
from io import StringIO

# IMPORTING THIRD PARTY PACKAGES
import jwt
from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase

# IMPORTING LOCAL PACKAGES
from mini_kit.auth.tokens import ALGORITHM, InvalidTokenError, decode_token, issue_token
from mini_kit.auth.user import AuthenticatedUser


class TokenTest(SimpleTestCase):

    def _encode(self, payload: dict, secret: str | None = None) -> str:
        return jwt.encode(payload, secret or settings.MINI_KIT_JWT_SECRET, algorithm=ALGORITHM)

    def test_issued_token_decodes_to_same_user_and_team(self):
        token = issue_token(user_pk=10, team_pk=1)

        self.assertEqual(decode_token(token), AuthenticatedUser(user_pk=10, team_pk=1))

    def test_token_signed_with_other_secret_is_rejected(self):
        token = self._encode({"user_pk": 10, "team_pk": 1}, secret="another-secret-at-least-32-bytes-long")

        with self.assertRaisesMessage(InvalidTokenError, "Invalid token"):
            decode_token(token)

    def test_expired_token_is_rejected(self):
        token = issue_token(user_pk=10, team_pk=1, expires_in=timedelta(seconds=-1))

        with self.assertRaisesMessage(InvalidTokenError, "Expired token"):
            decode_token(token)

    def test_token_without_team_pk_is_rejected(self):
        token = self._encode({"user_pk": 10})

        with self.assertRaisesMessage(InvalidTokenError, "missing claim 'team_pk'"):
            decode_token(token)

    def test_token_with_non_integer_team_pk_is_rejected(self):
        token = self._encode({"user_pk": 10, "team_pk": "1"})

        with self.assertRaisesMessage(InvalidTokenError, "must be positive integers"):
            decode_token(token)

    def test_issue_token_command_prints_a_valid_token(self):
        output = StringIO()

        call_command("issue_token", "--user-pk", "20", "--team-pk", "2", stdout=output)

        self.assertEqual(decode_token(output.getvalue().strip()), AuthenticatedUser(user_pk=20, team_pk=2))

    def test_issue_token_command_with_zero_hours_issues_an_already_expired_token(self):
        output = StringIO()

        call_command("issue_token", "--user-pk", "20", "--team-pk", "2", "--expires-in-hours", "0", stdout=output)

        with self.assertRaisesMessage(InvalidTokenError, "Expired token"):
            decode_token(output.getvalue().strip())
