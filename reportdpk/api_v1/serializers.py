from rest_framework import serializers
from django.db import models


from mainapp.models import (
    Direction,
    Stage,
    Company,
    Deal,
    Calls
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
    class Meta:
        model = Company
        fields = '__all__'


class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = '__all__'


class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calls
        fields = '__all__'



