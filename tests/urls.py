# IMPORTING THIRD PARTY PACKAGES
from django.urls import path

# IMPORTING LOCAL PACKAGES
from tests.sample_app.views import CrashView, NoteCollectionView, NoteDetailView

handler404 = "mini_kit.views.not_found_view"
handler500 = "mini_kit.views.server_error_view"

urlpatterns = [
    path("api/v1/notes", NoteCollectionView.as_view()),
    path("api/v1/notes/<int:note_pk>", NoteDetailView.as_view()),
    path("api/v1/crash", CrashView.as_view()),
]
