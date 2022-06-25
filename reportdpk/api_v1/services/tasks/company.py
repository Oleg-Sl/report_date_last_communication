from mainapp.models import Company
from api_v1.serializers import CompanySerializer
from api_v1.services.bitrix24 import requests_bx24


# объект выполнения запросов к Битрикс
bx24 = requests_bx24.Bitrix24()


def create_or_update(id_company):
    """ Сохранение компании из BX24 """
    company = get_company_data(id_company)
    if not company:
        return

    company = {
        **company,
        **get_company_requisite(id_company),
        **get_company_requisite_address(id_company)
    }

    exist_company = Company.objects.filter(id_bx=company["id_bx"]).first()
    if not exist_company:
        # при создании компании
        serializer = CompanySerializer(data=company)
    else:
        # при обновлении компании
        serializer = CompanySerializer(exist_company, data=company)

    if serializer.is_valid():
        serializer.save()
        return serializer.data

    return serializer.errors


def get_company_data(id_company):
    """ Запрос к BX24 на получение данных компании по ее ID """
    response_company = bx24.call(
        "crm.company.get",
        {
            "id": id_company
        }
    )

    if not response_company or "result" not in response_company or not response_company["result"]:
        return

    return {
        "id_bx": response_company["result"].get("ID", None) or None,
        "name": response_company["result"].get("TITLE", None) or None,
        "responsible": response_company["result"].get("ASSIGNED_BY_ID", None) or None,
        "industry": response_company["result"].get("INDUSTRY", None) or None,
        "sector": response_company["result"].get("UF_CRM_1640828035", None) or None,
        "region": response_company["result"].get("UF_CRM_1639121988", None) or None,
        "source": response_company["result"].get("UF_CRM_1639121612", None) or None,
        "number_employees": response_company["result"].get("UF_CRM_1639121303", None) or None,
        "address": response_company["result"].get("ADDRESS", None) or None,
        "district": response_company["result"].get("UF_CRM_1639121341", None) or None,
        "main_activity": response_company["result"].get("UF_CRM_1617767435", None) or None,
        "other_activities": response_company["result"].get("UF_CRM_1639121225", None) or None,
        "revenue": response_company["result"].get("REVENUE", None) or None,
        "profit": response_company["result"].get("UF_CRM_1639121262", None) or None,
    }


def get_company_requisite(id_company):
    """ Запрос к BX24 на получение реквизитов компании по ее ID """
    entity_type_id = 4  # тип сущности: 4 - компания
    response_requisite = bx24.call(
        "crm.requisite.list",
        {
            "filter": {"ENTITY_ID": id_company, "ENTITY_TYPE_ID": entity_type_id},
            "select": ["RQ_INN"]
        }
    )

    if not response_requisite or "result" not in response_requisite or not response_requisite["result"]:
        return {}

    return {
        "inn": response_requisite["result"][0].get("RQ_INN", None),
    }


def get_company_requisite_address(id_company):
    """ Запрос к BX24 на получение адреса компании по ее ID """
    entity_type_id = 4  # тип сущности: 4 - компания
    response_address = bx24.call(
        "crm.address.list",
        {
            "filter": {"ENTITY_ID": id_company, "ENTITY_TYPE_ID": entity_type_id},
            "select": ["ENTITY_ID", "REGION", "CITY", "PROVINCE"]
        }
    )

    if not response_address or "result" not in response_address or not response_address["result"]:
        return {}

    address_list = [item for item in response_address["result"] if item.get("REGION") or item.get("CITY") or item.get("PROVINCE")]

    if not address_list:
        return {}

    return {
        "requisite_region": address_list[0].get("REGION", None),
        "requisites_city": address_list[0].get("CITY", None),
        "requisites_province": address_list[0].get("PROVINCE", None),
    }

