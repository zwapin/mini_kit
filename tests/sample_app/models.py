# IMPORTING THIRD PARTY PACKAGES
from django.db import models

# IMPORTING LOCAL PACKAGES
from mini_kit.models import TeamScopedModel


class NoteModel(TeamScopedModel):
    title = models.CharField(max_length=100)
    author_user_pk = models.PositiveIntegerField()

    def __str__(self) -> str:
        return self.title
