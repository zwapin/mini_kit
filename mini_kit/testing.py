# IMPORTING THIRD PARTY PACKAGES
from rest_framework.response import Response
from rest_framework.test import APITestCase

# IMPORTING LOCAL PACKAGES
from mini_kit.auth.tokens import issue_token


class KitAPITestCase(APITestCase):
    """
    Base class for API tests. `self.client` sends JSON by default.

        def test_other_team_note_is_not_found(self):
            self.as_user(team_pk=2)
            response = self.client.get("/api/v1/notes/1")
            self.assert_error(response, 404, "note_not_found")
    """

    def as_user(self, team_pk: int, user_pk: int = 1) -> None:
        """Send the next requests with a real signed token: tests go through the real authentication."""
        token = issue_token(user_pk=user_pk, team_pk=team_pk)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def logout(self) -> None:
        """Send the next requests without any token."""
        self.client.credentials()

    def assert_error(self, response: Response, http_status: int, code: str) -> None:
        """Assert the status and the `error.code` of a response in the standard error format."""
        self.assertEqual(response.status_code, http_status, response.content)
        self.assertEqual(response.json()["error"]["code"], code)
