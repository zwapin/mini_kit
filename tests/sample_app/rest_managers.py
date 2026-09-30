# IMPORTING STANDARD PACKAGES
from functools import cached_property

# IMPORTING THIRD PARTY PACKAGES
from django.db.models import QuerySet

# IMPORTING LOCAL PACKAGES
from mini_kit.managers import BaseManager
from tests.sample_app.managers import NoteManager
from tests.sample_app.serializers import NoteInputSerializer


class NoteApiManager(BaseManager):
    """REST side of the notes: validates the API input and delegates to the core NoteManager."""

    def list_notes(self) -> QuerySet:
        return self._note_manager.list_notes()

    def get_note(self, note_pk: int) -> "NoteModel":
        return self._note_manager.get_note(note_pk)

    def create_note(self, payload: dict) -> "NoteModel":
        data = self._validate_payload(NoteInputSerializer, payload)
        return self._note_manager.create_note(title=data["title"], author_user_pk=self.user_pk)

    @cached_property
    def _note_manager(self) -> NoteManager:
        return NoteManager(team_pk=self.team_pk)
