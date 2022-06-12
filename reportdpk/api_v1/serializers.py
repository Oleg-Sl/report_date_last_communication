from rest_framework import serializers
from django.db import models


from mainapp.models import (
    Direction,
    Stage,
    Company,
    Deal
)


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = '__all__'


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    url = serializers.URLField(read_only=True)

    class Meta:
        model = Company
        fields = '__all__'

