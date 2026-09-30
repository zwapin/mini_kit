# IMPORTING THIRD PARTY PACKAGES
from django.db import models


class KitBaseModel(models.Model):
    """Abstract base of every model: adds creation and last-update timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TeamScopedModel(KitBaseModel):
    """
    Abstract base of the models that belong to a team (multi-tenant roots).

    `team_pk` is a plain integer, not a foreign key: teams live in another service. `objects` is
    the plain Django manager and is NOT filtered: query through `XModel.for_team(team_pk)` so that
    a team can never read another team's rows. Models that hang off a team-scoped parent (e.g.
    through a ForeignKey) can inherit KitBaseModel and be filtered through the parent's team_pk.
    """

    team_pk = models.PositiveIntegerField(db_index=True)

    class Meta:
        abstract = True

    @classmethod
    def for_team(cls, team_pk: int) -> models.QuerySet:
        """Rows of one team only. Start every query on a team-scoped model from here."""
        return cls.objects.filter(team_pk=team_pk)
