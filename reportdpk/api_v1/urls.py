from django.urls import include, path
from rest_framework import routers

from .views import *

app_name = 'api_v1'


urlpatterns = [
    path('create-update-direction/', DirectionCreateUpdateViewSet.as_view()),
    path('create-update-stages/', StageCreateUpdateViewSet.as_view()),

    path(r'create-update-company/', CompanyCreateUpdateViewSet.as_view()),
    path(r'create-update-deal/', DealCreateUpdateViewSet.as_view()),
    path(r'create-update-calls/', CallsCreateUpdateViewSet.as_view()),

    path(r'statistic-company/', StatisticCompanyViewSet.as_view()),
    path(r'statistic-direction/', StatisticDirectionViewSet.as_view()),



]

