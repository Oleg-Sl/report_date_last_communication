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


class StatisticCompanySerializer(serializers.ModelSerializer):
    summa_by_company_success = serializers.FloatField()
    summa_by_company_work = serializers.FloatField()
    dpk = serializers.DateTimeField()
    deal = DealSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        # fields = ("dpk", "summa_by_company_success", "summa_by_company_work", "deal")
        fields = '__all__'

