from rest_framework import views, viewsets, filters, status
from rest_framework.response import Response

from .services.bitrix24 import tokens as tokens_bx24
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


from .services.tasks import directions, stages, company, deal, calls


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


