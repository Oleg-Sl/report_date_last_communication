from rest_framework import serializers
from django.db import models


class CompanySerializer(serializers.ModelSerializer):
    url = serializers.URLField(read_only=True)

    class Meta:
        model = Company
        fields = '__all__'