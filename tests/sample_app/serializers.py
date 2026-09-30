# IMPORTING THIRD PARTY PACKAGES
from django.apps import apps
from rest_framework import serializers


class NoteInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)


class NoteSerializerModel(serializers.ModelSerializer):

    class Meta:
        model = apps.get_model("sample_app", "NoteModel")
        fields = ["id", "title", "author_user_pk", "created_at"]
