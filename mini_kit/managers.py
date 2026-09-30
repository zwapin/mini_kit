# IMPORTING STANDARD PACKAGES
from typing import Any

# IMPORTING THIRD PARTY PACKAGES
from rest_framework.serializers import Serializer


class BaseManager:
    """
    Base class of the REST managers (`rest_apis/managers/`): the bridge between the API and the
    service's core managers (`managers/`).

    A REST manager is created per request by BaseApiView, already bound to the caller: `team_pk`
    and `user_pk` come from the token, never from the body or the query string. Its methods take
    the raw request data, validate its shape with `_validate_payload`, and delegate to a core
    manager, returning what the core manager returns (model instances or querysets).

    The domain rules do NOT live here: they live in the core managers, black boxes that go from
    plain data to results (no request, no serializer, no JSON) and raise a KitError subclass when
    something is wrong. The same core manager can then serve REST, a command or a test.

        class NoteApiManager(BaseManager):

            def create_note(self, payload: dict) -> "NoteModel":
                data = self._validate_payload(NoteInputSerializer, payload)
                return NoteManager(team_pk=self.team_pk).create_note(title=data["title"])
    """

    def __init__(self, team_pk: int, user_pk: int):
        self.team_pk = team_pk
        self.user_pk = user_pk

    @staticmethod
    def _validate_payload(serializer_class: type[Serializer], payload: Any) -> dict:
        """
        Validate `payload` (request body or query params) with a DRF serializer.

        Returns the serializer's validated_data. On invalid data it raises a DRF ValidationError,
        which the kit turns into 400 invalid_payload: no need to catch it.
        """
        serializer = serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
