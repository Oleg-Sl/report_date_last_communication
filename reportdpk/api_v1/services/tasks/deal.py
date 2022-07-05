from mainapp.models import Deal, Stage
from api_v1.serializers import DealSerializer
from api_v1.services.bitrix24 import requests_bx24


# объект выполнения запросов к Битрикс
bx24 = requests_bx24.Bitrix24()


def create_or_update(id_deal):
    """ Сохранение компании из BX24 """
    response_deal = bx24.call(
        "crm.deal.get",
        {
            "id": id_deal
        }
    )

    if not response_deal or "result" not in response_deal:
        return

    direction = response_deal["result"]["CATEGORY_ID"]
    if direction in [43, "43"]:
        direction = response_deal["result"]["UF_CRM_1610523951"]

    stage_abbrev = response_deal["result"]["STAGE_ID"]
    stage = Stage.objects.get(abbrev=stage_abbrev)

    deal = {
        "id_bx": response_deal["result"]["ID"],
        "title": response_deal["result"]["TITLE"],
        "date_create": response_deal["result"]["DATE_CREATE"],
        "date_modify": response_deal["result"]["DATE_MODIFY"],
        "date_closed": response_deal["result"]["CLOSEDATE"] or None,
        "closed": True if response_deal["result"]["CLOSED"] == "Y" else False,
        "opportunity": response_deal["result"]["OPPORTUNITY"],
        "balance_on_payments": editing_numb(response_deal["result"]["UF_CRM_1575629957086"]),
        "amount_paid": editing_numb(response_deal["result"]["UF_CRM_1575375338"]),
        "company": response_deal["result"]["COMPANY_ID"],
        "direction": direction,
        "stage": stage.pk,
    }

    exist_deal = Deal.objects.filter(id_bx=deal["id_bx"]).first()
    if not exist_deal:
        # при создании
        serializer = DealSerializer(data=deal)
    else:
        # при обновлении
        serializer = DealSerializer(exist_deal, data=deal)

    if serializer.is_valid():
        serializer.save()
        return serializer.data

    return serializer.errors


def editing_numb(numb):
    """ Преобразует денежное значение из BX24 в число """
    numb = numb.split("|")[0] or "0"
    if numb:
        return f"{float(numb):.2f}"
    else:
        return None

