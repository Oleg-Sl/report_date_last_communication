from django.urls import include, path
from .views import *

app_name = 'api_v1'


urlpatterns = [
    path('create-update-direction/', DirectionCreateUpdateViewSet.as_view()),
    path('create-update-stages/', StageCreateUpdateViewSet.as_view()),

    path(r'create-update-company/', CompanyCreateUpdateViewSet.as_view()),
    path(r'create-update-deal/', DealCreateUpdateViewSet.as_view()),
    path(r'create-update-calls/', CallsCreateUpdateViewSet.as_view()),



]

