from rest_framework import views, viewsets, filters, status
from rest_framework.response import Response

from datetime import datetime, timedelta, timezone

from .services.bitrix24 import tokens as tokens_bx24
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
    StatisticCompanySerializer
)




from .services.tasks import directions, stages, company, deal, calls, statistic


class DirectionCreateUpdateViewSet(views.APIView):
    def post(self, request):
        # application_token = request.data.get("auth[application_token]", None)
        # if application_token != tokens_bx24.get_secret("application_token"):
        #     return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)
        result = directions.create_or_update()
        return Response(result, status=status.HTTP_200_OK)
        # task = create_or_update_directions.delay(request.data)
        # return Response("OK", status=status.HTTP_200_OK)


class StageCreateUpdateViewSet(views.APIView):
    def post(self, request):
        # application_token = request.data.get("auth[application_token]", None)
        # if application_token != tokens_bx24.get_secret("application_token"):
        #     return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)
        id_direction = request.data.get("direction", None)
        if not id_direction:
            return Response("Not transferred ID direction", status=status.HTTP_400_BAD_REQUEST)

        result = stages.create_or_update(id_direction)
        return Response(result, status=status.HTTP_200_OK)
        # task = create_or_update_directions.delay(request.data)
        # return Response("OK", status=status.HTTP_200_OK)


class CompanyCreateUpdateViewSet(views.APIView):
    """ Контроллер обработки событий BX24: onCrmCompanyAdd, onCrmCompanyUpdate, onCrmCompanyDelete """
    def post(self, request):
        # тип события - ONCRMCOMPANYADD, ONCRMCOMPANYUPDATE, ONCRMCOMPANYDELETE
        event = request.data.get("event", "")
        id_company = request.data.get("data[FIELDS][ID]", None)
        # application_token = request.data.get("auth[application_token]", None)
        # if application_token != tokens_bx24.get_secret("application_token"):
        #     return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)

        if not id_company:
            return Response("Not transferred ID company", status=status.HTTP_400_BAD_REQUEST)

        if event == "ONCRMCOMPANYDELETE":
            result = Company.objects.filter(id_bx=id_company).delete()
            return Response(result, status=status.HTTP_200_OK)

        result = company.create_or_update(id_company)
        return Response(result, status=status.HTTP_200_OK)


class DealCreateUpdateViewSet(views.APIView):
    """ Контроллер обработки событий BX24: onCrmDealAdd, onCrmDealUpdate, onCrmDealDelete """
    def post(self, request):
        # тип события - ONCRMDEALADD, ONCRMDEALUPDATE, ONCRMDEALDELETE
        event = request.data.get("event", "")
        id_deal = request.data.get("data[FIELDS][ID]", None)
        # application_token = request.data.get("auth[application_token]", None)
        # if application_token != tokens_bx24.get_secret("application_token"):
        #     return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)

        if not id_deal:
            return Response("Not transferred ID deal", status=status.HTTP_400_BAD_REQUEST)

        if event == "ONCRMDEALDELETE":
            result = Deal.objects.filter(id_bx=id_deal).delete()
            return Response(result, status=status.HTTP_200_OK)

        result = deal.create_or_update(id_deal)
        return Response(result, status=status.HTTP_200_OK)


class CallsCreateUpdateViewSet(views.APIView):
    """ Контроллер обработки событий BX24: onVoximplantCallEnd """

    def post(self, request):
        id_call = request.data.get("data[CALL_ID]", None)
        # application_token = request.data.get("auth[application_token]", None)
        # if application_token != tokens_bx24.get_secret("application_token"):
        #     return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)
        if not id_call:
            return Response("Not transferred ID call", status=status.HTTP_400_BAD_REQUEST)

        result = calls.create_or_update(id_call)
        return Response(result, status=status.HTTP_200_OK)


class StatisticCompanyViewSet(views.APIView):
    def post(self, request):
        # id_call = request.data.get("data[CALL_ID]", None)
        # application_token = request.data.get("auth[application_token]", None)
        # if application_token != tokens_bx24.get_secret("application_token"):
        #     return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)

        directions_actual = Direction.direction_actual.values('pk')
        queryset = Company.objects.statistic_company(directions_actual)

        response = StatisticCompanySerializer(queryset, many=True).data

        return Response(response, status=status.HTTP_200_OK)


# количество дней по прошествии которых текущая сделка не учитывается в статистике
DEFAULT_DELTA_DEYS_SUSPENDED_DEALS = 183
# количество дней по прошествии которых провальная сделка не учитывается в статистике
DEFAULT_DELTA_DEYS_FAILED_DEALS = 92


class StatisticDirectionViewSet(views.APIView):

    def post(self, request):
        # id_call = request.data.get("data[CALL_ID]", None)
        # application_token = request.data.get("auth[application_token]", None)
        # if application_token != tokens_bx24.get_secret("application_token"):
        #     return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)

        companies_ids = request.data.get("companies", [])
        directions_ids = request.data.get("directions", [])
        delta_days_for_suspended_deals = request.data.get("days_for_suspended_deals", DEFAULT_DELTA_DEYS_SUSPENDED_DEALS)
        delta_days_for_failed_deals = request.data.get("days_for_failed_deals", DEFAULT_DELTA_DEYS_FAILED_DEALS)

        if not isinstance(companies_ids, list) or not isinstance(directions_ids, list):
            return Response(
                'The "companies" and "directions" variables should be a list',
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(delta_days_for_suspended_deals, int) or not isinstance(delta_days_for_failed_deals, int):
            return Response(
                'The "days_for_suspended_deals" and "days_for_failed_deals" variables must be a number',
                status=status.HTTP_400_BAD_REQUEST
            )

        limit_date_suspended_deals = datetime.now(timezone.utc) - timedelta(days=delta_days_for_suspended_deals)
        limit_date_failed_deals = datetime.now(timezone.utc) - timedelta(days=delta_days_for_failed_deals)

        queryset = Deal.objects.statistic_company_by_directions(
            [el for el in companies_ids if isinstance(el, int) or el.isdigit()],
            [el for el in directions_ids if isinstance(el, int) or el.isdigit()],
            limit_date_suspended_deals,
            limit_date_failed_deals
        )
        response = converting_list_to_dict(queryset, "company__pk", "direction")
        return Response(response, status=status.HTTP_200_OK)


# class StatisticViewSet(viewsets.ModelViewSet):
#     serializer_class = StatisticSerializer
#     pagination_class = CustomPageNumberPagination
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_class = service.StatisticDataFilter

