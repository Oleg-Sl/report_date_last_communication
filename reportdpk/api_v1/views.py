from rest_framework import views, viewsets, filters, status
from rest_framework.response import Response

from .services.bitrix24 import tokens as tokens_bx24
# from .tasks import (
#     create_or_update_stages,
#     create_or_update_company,
# )

# TEMP
from .services.tasks import directions, stages, company


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
        application_token = request.data.get("auth[application_token]", None)

        # if application_token != tokens_bx24.get_secret("application_token"):
        #     return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)

        if not id_company:
            return Response("Not transferred ID company", status=status.HTTP_400_BAD_REQUEST)

        if event == "ONCRMCOMPANYDELETE":
            pass

        result = company.create_or_update(id_company)
        return Response(result, status=status.HTTP_200_OK)



