from rest_framework import serializers
from .models import WhichSex
from groups.serializers import GroupSerializer
from traits.serializers import TraitSerializer


class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=128)
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(
        choices=WhichSex.choices,
        default=WhichSex.NOT_INFORMED
    )
    group = GroupSerializer()
    traits = TraitSerializer(many=True)
