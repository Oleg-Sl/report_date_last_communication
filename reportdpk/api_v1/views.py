from rest_framework import generics, mixins
from rest_framework import views, viewsets, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse, JsonResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from django.conf import settings

from datetime import datetime, timedelta, timezone

import logging

from .services.bitrix24 import verification_app, tokens
from .services.converter import converting_list_to_dict
# from .tasks import (
#     create_or_update_stages,
#     create_or_update_company,
# )

from mainapp.models import (
    Direction,
    Stage,
    Company,
    Deal
)

from api_v1.serializers import (
    DirectionSerializer,
    StageSerializer,
    CompanySerializer,
    SectorCompanySerializer,
    RegionCompanySerializer,
    SourceCompanySerializer,
    RequisitesRegionCompanySerializer,
    RequisitesCityCompanySerializer,

    StatisticCompanySerializer

)

from .tasks import (
    directions_create_or_update,
    stages_create_or_update,
    company_create_or_update,
    deal_create_or_update,
    calls_create_or_update
)


from .services.tasks import directions, stages, company, deal, calls
from .services.filter_queryset import statistic_company

# логгер входные данные событий от Битрикс
logger_tasks_access = logging.getLogger('tasks_access')
logger_tasks_access.setLevel(logging.INFO)
fh_tasks_access = logging.handlers.TimedRotatingFileHandler('./logs/access.log', when='D', interval=1)
formatter_tasks_access = logging.Formatter('[%(asctime)s] %(levelname).1s %(message)s')
fh_tasks_access.setFormatter(formatter_tasks_access)
logger_tasks_access.addHandler(fh_tasks_access)


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'install': reverse('api_v1:install', request=request, format=format),
        'uninstall': reverse('api_v1:uninstall', request=request, format=format),
        'index': reverse('api_v1:index', request=request, format=format),

        'directions': reverse('api_v1:directions-list', request=request, format=format),
        'stages': reverse('api_v1:stages-list', request=request, format=format),
        'companies': reverse('api_v1:companies-list', request=request, format=format),
        'region_companies': reverse('api_v1:region_companies-list', request=request, format=format),
        'sector_companies': reverse('api_v1:sector_companies-list', request=request, format=format),
        'source_companies': reverse('api_v1:source_companies-list', request=request, format=format),
        'requisite_region': reverse('api_v1:requisite_region-list', request=request, format=format),
        'requisites_city': reverse('api_v1:requisites_city-list', request=request, format=format),

        'statistic-company': reverse('api_v1:statistic-company-list', request=request, format=format),
        'statistic-direction': reverse('api_v1:statistic-direction-list', request=request, format=format),
        'statistic-company-direction': reverse('api_v1:statistic-company-direction-list', request=request, format=format),

        'create-update-direction': reverse('api_v1:create_update_direction', request=request, format=format),
        'create-update-stages': reverse('api_v1:create_update_stages', request=request, format=format),
        'create-update-company': reverse('api_v1:create_update_company', request=request, format=format),
        'create-update-deal': reverse('api_v1:create_update_deal', request=request, format=format),
        'create-update-calls': reverse('api_v1:create_update_calls', request=request, format=format),
    })


# Обработчик установки приложения
class InstallAppApiView(views.APIView):
    permission_classes = [AllowAny]

    @xframe_options_exempt
    def post(self, request):
        data = {
            "domain": request.query_params.get("DOMAIN", "bits24.bitrix24.ru"),
            "auth_token": request.data.get("AUTH_ID", ""),
            "expires_in": request.data.get("AUTH_EXPIRES", 3600),
            "refresh_token": request.data.get("REFRESH_ID", ""),
            "application_token": request.query_params.get("APP_SID", ""),
            'client_endpoint': f'https://{request.query_params.get("DOMAIN", "bits24.bitrix24.ru")}/rest/',
        }
        tokens.save_secrets(request.data)
        return render(request, 'install.html')


# Обработчик удаления приложения
class UninstallAppApiView(views.APIView):
    permission_classes = [AllowAny]

    @xframe_options_exempt
    def post(self, request):
        return Response(status.HTTP_200_OK)


# Обработчик установленного приложения
class IndexApiView(views.APIView):
    permission_classes = [AllowAny]

    @xframe_options_exempt
    def post(self, request):
        return render(request, 'index.html')

    @xframe_options_exempt
    def get(self, request):
        return render(request, 'index.html')


class DirectionViewSet(viewsets.ModelViewSet):
    queryset = Direction.objects.filter(new=True)
    serializer_class = DirectionSerializer
    # permission_classes = [AllowAny]
    http_method_names = ['get', 'options']
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    # filterset_class = service.DirectionDataFilter
    permission_classes = [IsAuthenticated]


class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'options']


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["^id_bx", "name", "^inn"]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'options']


class SectorCompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.filter(sector__isnull=False).values("sector").distinct("sector")
    serializer_class = SectorCompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["^sector", ]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'options']


class RegionCompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.filter(region__isnull=False).values("region").distinct("region")
    serializer_class = RegionCompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["^region", ]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'options']


class SourceCompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.filter(source__isnull=False).values("source").distinct("source")
    serializer_class = SourceCompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["^source", ]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'options']


class RequisitesRegionCompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.filter(requisite_region__isnull=False).values("requisite_region").distinct("requisite_region")
    serializer_class = RequisitesRegionCompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["^requisite_region", ]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'options']


class RequisitesCityCompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.filter(requisites_city__isnull=False).values("requisites_city").distinct("requisites_city")
    serializer_class = RequisitesCityCompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["^requisites_city", ]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'options']


class DirectionCreateUpdateViewSet(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        application_token = request.data.get("auth[application_token]", None)

        if not verification_app.verification(application_token):
            return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)

        result = directions_create_or_update.delay()
        return Response(result, status=status.HTTP_200_OK)


class StageCreateUpdateViewSet(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        application_token = request.data.get("auth[application_token]", None)
        id_direction = request.data.get("direction", None)

        if not verification_app.verification(application_token):
            return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)

        if not id_direction:
            return Response("Not transferred ID direction", status=status.HTTP_400_BAD_REQUEST)

        result = stages_create_or_update.delay(id_direction)
        return Response(result, status=status.HTTP_200_OK)


class CompanyCreateUpdateViewSet(views.APIView):
    permission_classes = [AllowAny]

    """ Контроллер обработки событий BX24: onCrmCompanyAdd, onCrmCompanyUpdate, onCrmCompanyDelete """
    def post(self, request):
        # тип события - ONCRMCOMPANYADD, ONCRMCOMPANYUPDATE, ONCRMCOMPANYDELETE
        logger_tasks_access.info(request.data)

        event = request.data.get("event", "")
        id_company = request.data.get("data[FIELDS][ID]", None)
        application_token = request.data.get("auth[application_token]", None)

        if not verification_app.verification(application_token):
            return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)

        if not id_company:
            return Response("Not transferred ID company", status=status.HTTP_400_BAD_REQUEST)

        if event == "ONCRMCOMPANYDELETE":
            result = Company.objects.filter(id_bx=id_company).delete()
            return Response(result, status=status.HTTP_200_OK)

        result = company_create_or_update.delay(id_company)
        return Response(result, status=status.HTTP_200_OK)


class DealCreateUpdateViewSet(views.APIView):
    permission_classes = [AllowAny]

    """ Контроллер обработки событий BX24: onCrmDealAdd, onCrmDealUpdate, onCrmDealDelete """
    def post(self, request):
        # тип события - ONCRMDEALADD, ONCRMDEALUPDATE, ONCRMDEALDELETE
        logger_tasks_access.info(request.data)
        event = request.data.get("event", "")
        id_deal = request.data.get("data[FIELDS][ID]", None)
        application_token = request.data.get("auth[application_token]", None)

        if not verification_app.verification(application_token):
            return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)

        if not id_deal:
            return Response("Not transferred ID deal", status=status.HTTP_400_BAD_REQUEST)

        if event == "ONCRMDEALDELETE":
            result = Deal.objects.filter(id_bx=id_deal).delete()
            return Response(result, status=status.HTTP_200_OK)

        result = deal_create_or_update.delay(id_deal)
        # result = deal.create_or_update(id_deal)
        return Response(result, status=status.HTTP_200_OK)


class CallsCreateUpdateViewSet(views.APIView):
    permission_classes = [AllowAny]

    """ Контроллер обработки событий BX24: onVoximplantCallEnd """
    def post(self, request):
        logger_tasks_access.info(request.data)
        id_call = request.data.get("data[CALL_ID]", None)
        application_token = request.data.get("auth[application_token]", None)

        if not verification_app.verification(application_token):
            return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)

        if not id_call:
            return Response("Not transferred ID call", status=status.HTTP_400_BAD_REQUEST)

        result = calls_create_or_update.delay(id_call)
        return Response(result, status=status.HTTP_200_OK)


class StatisticCompanyViewSet(viewsets.GenericViewSet):
    queryset = Company.objects.all()
    serializer_class = StatisticCompanySerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = statistic_company.StatisticCompany
    ordering_fields = ["id_bx", "name", "responsible", "dpk", "summa_by_company_success", "summa_by_company_work"]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        duration = self.request.query_params.get("duration", "0")
        direction = Direction.direction_actual.all() #.values('pk')
        return super().get_queryset().statistic_company(direction, duration)

    def list(self, request, *args, **kwargs):
        duration = request.query_params.get("duration", "0")

        if not duration.isdigit():
            return Response('The "duration" value must be an integer', status=status.HTTP_400_BAD_REQUEST)

        queryset = self.filter_queryset(
            self.get_queryset()
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class StatisticCompanyDirectionViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    # queryset = Company.objects.all()
    # filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # filterset_class = statistic_company.StatisticCompanyByDirection
    # ordering_fields = ["id_bx", "name", "responsible", ]

    def get_queryset(self, companies_ids, directions_ids, limit_date_suspended_deals, limit_date_failed_deals):
        return Deal.objects.statistic_company_by_directions(
            companies_ids,
            directions_ids,
            limit_date_suspended_deals,
            limit_date_failed_deals
        )

    def list(self, request, *args, **kwargs):
        companies_str = request.query_params .get("companies", "")
        directions_str = request.query_params.get("directions", "")
        days_for_suspended_deals_str = request.query_params.get("days_for_suspended_deals",
                                                                  settings.DEFAULT_DELTA_DEYS_SUSPENDED_DEALS)
        days_for_failed_deals_str = request.query_params.get("days_for_failed_deals",
                                                               settings.DEFAULT_DELTA_DEYS_FAILED_DEALS)

        companies_ids = [int(el) for el in companies_str.split(",") if isinstance(el, str) and el.isdigit()]
        directions_ids = [int(el) for el in directions_str.split(",") if isinstance(el, str) and el.isdigit()]

        if not days_for_suspended_deals_str.isdigit() or not days_for_failed_deals_str.isdigit():
            return Response(
                'The "days_for_suspended_deals" and "days_for_failed_deals" variables must be a number',
                status=status.HTTP_400_BAD_REQUEST
            )

        limit_date_suspended_deals = datetime.now(timezone.utc) - timedelta(days=int(days_for_suspended_deals_str))
        limit_date_failed_deals = datetime.now(timezone.utc) - timedelta(days=int(days_for_failed_deals_str))

        queryset = self.filter_queryset(
            self.get_queryset(companies_ids, directions_ids, limit_date_suspended_deals, limit_date_failed_deals)
        )

        response = converting_list_to_dict(queryset, "company__pk", "direction")
        return Response(response, status=status.HTTP_200_OK)


class StatisticDirectionViewSet(viewsets.GenericViewSet):
    queryset = Direction.direction_actual.count_active_deals()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = statistic_company.StatisticByDirection
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = converting_list_to_dict(queryset, "id_bx")
        return Response(response, status=status.HTTP_200_OK)


