from rest_framework import views, viewsets, filters, status
from rest_framework.response import Response

from .serviсes.bitrix24 import tokens as tokens_bx24


class CompanyCreateUpdateViewSet(views.APIView):
    """ Контроллер обработки событий BX24: onCrmCompanyAdd, onCrmCompanyUpdate, onCrmCompanyDelete """
    def post(self, request):
        # тип события - ONCRMCOMPANYADD, ONCRMCOMPANYUPDATE, ONCRMCOMPANYDELETE
        event = request.data.get("event", "")
        id_company = request.data.get("data[FIELDS][ID]", None)
        application_token = request.data.get("auth[application_token]", None)

        if application_token != tokens_bx24.get_secret("application_token"):
            return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)

        if not id_company:
            return Response("Not transferred ID company", status=status.HTTP_400_BAD_REQUEST)

        if event == "ONCRMCOMPANYDELETE":
            pass

        task = calls_task.delay(request.data)
        return Response("OK", status=status.HTTP_200_OK)



