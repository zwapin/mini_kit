# IMPORTING THIRD PARTY PACKAGES
from rest_framework.request import Request
from rest_framework.response import Response

# IMPORTING LOCAL PACKAGES
from mini_kit.views import BaseApiView
from tests.sample_app.rest_managers import NoteApiManager
from tests.sample_app.serializers import NoteSerializerModel


class NotesApiView(BaseApiView):
    manager_class = NoteApiManager

    def get(self, request: Request) -> Response:
        return self.respond_list(self.manager.list_notes(), NoteSerializerModel)

    def post(self, request: Request) -> Response:
        return self.respond_created(self.manager.create_note(request.data), NoteSerializerModel)


class SingleNoteApiView(BaseApiView):
    manager_class = NoteApiManager

    def get(self, request: Request, note_pk: int) -> Response:
        return self.respond_item(self.manager.get_note(note_pk), NoteSerializerModel)


class CrashApiView(BaseApiView):
    manager_class = NoteApiManager

    def get(self, request: Request) -> Response:
        raise RuntimeError("boom")
