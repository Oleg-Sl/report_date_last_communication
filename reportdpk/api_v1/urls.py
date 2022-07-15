from django.urls import include, path
from rest_framework import routers

from .views import *


app_name = 'api_v1'


router = routers.DefaultRouter()
router.register(r'directions', DirectionViewSet, basename='directions')
router.register(r'stages', StageViewSet, basename='stages')
router.register(r'companies', CompanyViewSet, basename='companies')
router.register(r'region_companies', RegionCompanyViewSet, basename='region_companies')
router.register(r'sector_companies', SectorCompanyViewSet, basename='sector_companies')
router.register(r'source_companies', SourceCompanyViewSet, basename='source_companies')
router.register(r'requisite_region', RequisitesRegionCompanyViewSet, basename='requisite_region')
router.register(r'requisites_city', RequisitesCityCompanyViewSet, basename='requisites_city')

router.register(r'statistic-company', StatisticCompanyViewSet, basename='statistic-company')
# router.register(r'statistic-company-new', StatisticCompanyNewViewSet, basename='statistic-company-new')
router.register(r'statistic-company-direction', StatisticCompanyDirectionViewSet, basename='statistic-company-direction')
router.register(r'statistic-direction', StatisticDirectionViewSet, basename='statistic-direction')


urlpatterns = [
    path('', api_root),
    path('install/', InstallAppApiView.as_view(), name='install'),
    path('uninstall/', UninstallAppApiView.as_view(), name='uninstall'),
    path('index/', IndexApiView.as_view(), name='index'),

    path('create-update-direction/', DirectionCreateUpdateViewSet.as_view(), name='create_update_direction'),
    path('create-update-stages/', StageCreateUpdateViewSet.as_view(), name='create_update_stages'),

    path(r'create-update-company/', CompanyCreateUpdateViewSet.as_view(), name='create_update_company'),
    path(r'create-update-deal/', DealCreateUpdateViewSet.as_view(), name='create_update_deal'),
    path(r'create-update-calls/', CallsCreateUpdateViewSet.as_view(), name='create_update_calls'),

    # path(r'statistic-company-new/', StatisticCompanyNewViewSet.as_view(), name='statistic-company-new'),

]

urlpatterns += router.urls

