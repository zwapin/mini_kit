# IMPORTING THIRD PARTY PACKAGES
from django.db.models import QuerySet
from rest_framework import serializers

# IMPORTING LOCAL PACKAGES
from mini_kit.errors import ConflictError, NotFoundError
from mini_kit.managers import BaseManager
from tests.sample_app.models import NoteModel


class NoteNotFoundError(NotFoundError):
    code = "note_not_found"
    default_message = "Note not found"


class DuplicateNoteError(ConflictError):
    code = "duplicate_note"
    default_message = "A note with this title already exists"


class NoteInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)


class NoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = NoteModel
        fields = ["id", "title", "author_user_pk", "created_at"]


class NoteManager(BaseManager):

    def list_notes(self) -> QuerySet[NoteModel]:
        return NoteModel.for_team(self.team_pk).order_by("-created_at")

    def get_note(self, note_pk: int) -> NoteModel:
        note = self.list_notes().filter(pk=note_pk).first()
        if note is None:
            raise NoteNotFoundError()
        return note

    def create_note(self, payload: dict) -> NoteModel:
        data = self._validate_payload(NoteInputSerializer, payload)
        if self.list_notes().filter(title=data["title"]).exists():
            raise DuplicateNoteError()
        return NoteModel.objects.create(team_pk=self.team_pk, author_user_pk=self.user_pk, **data)
