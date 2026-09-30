# IMPORTING THIRD PARTY PACKAGES
from django.apps import apps
from django.db.models import QuerySet

# IMPORTING LOCAL PACKAGES
from mini_kit.errors import ConflictError, NotFoundError


class NoteNotFoundError(NotFoundError):
    code = "note_not_found"
    default_message = "Note not found"


class DuplicateNoteError(ConflictError):
    code = "duplicate_note"
    default_message = "A note with this title already exists"


class NoteManager:
    """Core manager of the notes of one team: plain data in, model instances out."""

    def __init__(self, team_pk: int):
        self._team_pk = team_pk

    def list_notes(self) -> QuerySet:
        return self._note_model().for_team(self._team_pk).order_by("-created_at")

    def get_note(self, note_pk: int) -> "NoteModel":
        note = self.list_notes().filter(pk=note_pk).first()
        if note is None:
            raise NoteNotFoundError()
        return note

    def create_note(self, title: str, author_user_pk: int) -> "NoteModel":
        if self.list_notes().filter(title=title).exists():
            raise DuplicateNoteError()
        return self._note_model().objects.create(team_pk=self._team_pk, author_user_pk=author_user_pk, title=title)

    @staticmethod
    def _note_model() -> type["NoteModel"]:
        return apps.get_model("sample_app", "NoteModel")
