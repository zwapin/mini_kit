# IMPORTING STANDARD PACKAGES
from collections.abc import Iterable
from functools import cached_property

# IMPORTING THIRD PARTY PACKAGES
from django.db import models
from django.http import HttpRequest, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

# IMPORTING LOCAL PACKAGES
from mini_kit.errors import KitError, NotFoundError, error_body
from mini_kit.managers import BaseManager


class BaseApiView(APIView):
    """
    Base class of every REST view.

    A view is a thin adapter: read the request, call ONE method of its REST manager
    (`manager_class`, a mini_kit BaseManager), return one of the respond_* helpers. No queries,
    no domain rules, no error handling here: errors raised below are turned into responses by
    the kit exception handler.

        class NotesApiView(BaseApiView):
            manager_class = NoteApiManager

            def post(self, request):
                return self.respond_created(self.manager.create_note(request.data), NoteSerializerModel)

    Authentication (token required) comes from the kit REST_FRAMEWORK settings.
    """

    manager_class: type[BaseManager]

    @cached_property
    def manager(self) -> BaseManager:
        """The REST manager of this view, bound to the team and user of the request token."""
        return self.manager_class(team_pk=self.request.user.team_pk, user_pk=self.request.user.user_pk)

    @staticmethod
    def respond_item(instance: models.Model, serializer_class: type[Serializer]) -> Response:
        """200 with one serialized object."""
        return Response(serializer_class(instance).data, status=status.HTTP_200_OK)

    @staticmethod
    def respond_created(instance: models.Model, serializer_class: type[Serializer]) -> Response:
        """201 with the serialized object that has just been created."""
        return Response(serializer_class(instance).data, status=status.HTTP_201_CREATED)

    @staticmethod
    def respond_list(items: Iterable[models.Model], serializer_class: type[Serializer]) -> Response:
        """200 with {"count": N, "results": [...]}; an empty list is still a 200."""
        results = serializer_class(items, many=True).data
        return Response({"count": len(results), "results": results}, status=status.HTTP_200_OK)


def not_found_view(request: HttpRequest, exception: Exception) -> JsonResponse:
    """handler404 for routes that match no view. Active only with DEBUG = False."""
    return JsonResponse(error_body(NotFoundError.code, NotFoundError.default_message), status=NotFoundError.http_status)


def server_error_view(request: HttpRequest) -> JsonResponse:
    """handler500 for errors raised outside DRF views. Active only with DEBUG = False."""
    return JsonResponse(error_body(KitError.code, KitError.default_message), status=KitError.http_status)
