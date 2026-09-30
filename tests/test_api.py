# IMPORTING THIRD PARTY PACKAGES
from rest_framework import status

# IMPORTING LOCAL PACKAGES
from mini_kit.testing import KitAPITestCase
from tests.sample_app.models import NoteModel

NOTES_URL = "/api/v1/notes"


class AuthenticationTest(KitAPITestCase):

    def test_request_without_token_is_unauthorized(self):
        response = self.client.get(NOTES_URL)

        self.assert_error(response, status.HTTP_401_UNAUTHORIZED, "unauthorized")
        self.assertEqual(response["WWW-Authenticate"], "Token")

    def test_request_with_invalid_token_is_unauthorized(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token not-a-jwt")

        response = self.client.get(NOTES_URL)

        self.assert_error(response, status.HTTP_401_UNAUTHORIZED, "unauthorized")
        self.assertEqual(response.json()["error"]["message"], "Invalid token")

    def test_request_with_malformed_header_is_unauthorized(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token a b")

        response = self.client.get(NOTES_URL)

        self.assert_error(response, status.HTTP_401_UNAUTHORIZED, "unauthorized")


class TeamScopingTest(KitAPITestCase):

    def setUp(self):
        self.note = NoteModel.objects.create(team_pk=1, author_user_pk=10, title="Team 1 note")

    def test_team_sees_only_its_own_notes(self):
        NoteModel.objects.create(team_pk=2, author_user_pk=20, title="Team 2 note")
        self.as_user(team_pk=1)

        response = self.client.get(NOTES_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["title"], "Team 1 note")

    def test_empty_list_is_ok_with_zero_count(self):
        self.as_user(team_pk=3)

        response = self.client.get(NOTES_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"count": 0, "results": []})

    def test_other_team_note_is_not_found(self):
        self.as_user(team_pk=2)

        response = self.client.get(f"{NOTES_URL}/{self.note.pk}")

        self.assert_error(response, status.HTTP_404_NOT_FOUND, "note_not_found")


class CreateNoteTest(KitAPITestCase):

    def setUp(self):
        self.as_user(team_pk=1, user_pk=10)

    def test_create_note_uses_team_and_user_from_token(self):
        response = self.client.post(NOTES_URL, {"title": "Hello"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        note = NoteModel.objects.get(pk=response.json()["id"])
        self.assertEqual((note.team_pk, note.author_user_pk), (1, 10))

    def test_missing_field_is_invalid_payload_naming_the_field(self):
        response = self.client.post(NOTES_URL, {})

        self.assert_error(response, status.HTTP_400_BAD_REQUEST, "invalid_payload")
        self.assertTrue(response.json()["error"]["message"].startswith("title:"))

    def test_malformed_json_is_invalid_payload(self):
        response = self.client.post(NOTES_URL, data="{not json", content_type="application/json")

        self.assert_error(response, status.HTTP_400_BAD_REQUEST, "invalid_payload")

    def test_domain_conflict_uses_its_own_code(self):
        NoteModel.objects.create(team_pk=1, author_user_pk=10, title="Hello")

        response = self.client.post(NOTES_URL, {"title": "Hello"})

        self.assert_error(response, status.HTTP_409_CONFLICT, "duplicate_note")


class ErrorEnvelopeTest(KitAPITestCase):

    def setUp(self):
        self.as_user(team_pk=1)

    def test_unknown_route_uses_error_envelope(self):
        response = self.client.get("/api/v1/unknown")

        self.assert_error(response, status.HTTP_404_NOT_FOUND, "not_found")

    def test_unsupported_method_uses_error_envelope(self):
        response = self.client.delete(NOTES_URL)

        self.assert_error(response, status.HTTP_405_METHOD_NOT_ALLOWED, "method_not_allowed")

    def test_unhandled_exception_is_internal_error(self):
        with self.assertLogs("mini_kit.exception_handler", level="ERROR"):
            response = self.client.get("/api/v1/crash")

        self.assert_error(response, status.HTTP_500_INTERNAL_SERVER_ERROR, "internal_error")
