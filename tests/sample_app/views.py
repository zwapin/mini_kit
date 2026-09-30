# IMPORTING THIRD PARTY PACKAGES
from rest_framework.request import Request
from rest_framework.response import Response

# IMPORTING LOCAL PACKAGES
from mini_kit.views import BaseApiView
from tests.sample_app.managers import NoteManager, NoteSerializer


class NoteCollectionView(BaseApiView):
    manager_class = NoteManager

    def get(self, request: Request) -> Response:
        return self.respond_list(self.manager.list_notes(), NoteSerializer)

    def post(self, request: Request) -> Response:
        return self.respond_created(self.manager.create_note(request.data), NoteSerializer)


class NoteDetailView(BaseApiView):
    manager_class = NoteManager

    def get(self, request: Request, note_pk: int) -> Response:
        return self.respond_item(self.manager.get_note(note_pk), NoteSerializer)


class CrashView(BaseApiView):
    manager_class = NoteManager

    def get(self, request: Request) -> Response:
        raise RuntimeError("boom")
