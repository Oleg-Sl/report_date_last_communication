from django.urls import include, path
from .views import *

app_name = 'api_v1'


urlpatterns = [
    path(r'create-update-company/', CompanyCreateUpdateViewSet.as_view()),

]

