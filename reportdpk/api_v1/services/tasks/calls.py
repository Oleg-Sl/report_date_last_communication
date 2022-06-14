from mainapp.models import Calls, Company
from api_v1.serializers import CallSerializer
from api_v1.services.bitrix24 import requests_bx24
from . import company

# объект выполнения запросов к Битрикс
bx24 = requests_bx24.Bitrix24()


def create_or_update(id_call):
    """ Сохранение звонка из BX24 """
    response_calls = bx24.call(
        "voximplant.statistic.get",
        {
            "filter": {"CALL_ID": id_call},
            # "SORT": "CALL_START_DATE",
            # "ORDER": "DESC",
        }
    )

    if not response_calls or "result" not in response_calls or not response_calls["result"]:
        return

    response_call = response_calls["result"][0]

    call = {
        "id_bx": response_call.get("ID"),
        "call_type": response_call.get("CALL_TYPE"),
        "duration": response_call.get("CALL_DURATION"),
        "start_date": response_call.get("CALL_START_DATE"),
        "activity_id": response_call.get("CRM_ACTIVITY_ID"),
        "company": get_company_id_entity(
            entity_type=response_call["CRM_ENTITY_TYPE"],
            entity_id=response_call["CRM_ENTITY_ID"]
        )
    }

    check_exist_or_create_company(call["company"])
    update_date_last_communication_for_company(call["company"], call["start_date"])

    exist_call = Calls.objects.filter(id_bx=call["id_bx"]).first()
    if not exist_call:
        # при создании
        serializer = CallSerializer(data=call)
    else:
        # при обновлении
        serializer = CallSerializer(exist_call, data=call)

    if serializer.is_valid():
        serializer.save()
        return serializer.data

    return serializer.errors


def get_company_id_entity(entity_type, entity_id):
    if entity_type == "COMPANY":
        return entity_id
    if entity_type == "CONTACT":
        response = bx24.call(
            "crm.contact.company.items.get",
            {
                "id": entity_id
            }
        ).get("result")[0]
    if entity_type == "LEAD":
        response = bx24.call(
            "crm.lead.get",
            {
                "id": entity_id
            }
        ).get("result")
    if entity_type == "DEAL":
        response = bx24.call(
            "crm.deal.get",
            {
                "id": entity_id
            }
        ).get("result")

    return response.get("COMPANY_ID", None)


def check_exist_or_create_company(id_company):
    if id_company and not Company.objects.filter(id_bx=id_company).exists():
        company.create_or_update(id_company)


from django.db.models import F, Q, Value, When, Case
from django.db.models.functions import Greatest
from datetime import datetime
def update_date_last_communication_for_company(id_company, dpk):
    if id_company and dpk:
        company = Company.objects.get(id_bx=id_company)
        company.date_last_communication = Case(
            When(Q(date_last_communication__isnull=True), then=Value(datetime.strptime(dpk, "%Y-%m-%dT%H:%M:%S%z"))),
            default=Greatest(F('date_last_communication'), Value(datetime.strptime(dpk, "%Y-%m-%dT%H:%M:%S%z")))
        )
        company.save()

