from reportactivity.celery import celery_app
import logging
import time

from .services.bitrix24 import requests_bx24
from ..mainapp.models import (
    Direction,
    Stage,
    Company,
    Deal
)

# объект выполнения запросов к Битрикс
bx24 = requests_bx24.Bitrix24()





@celery_app.task
def create_or_update_company(id_company):
    company = get_company_data(id_company)
    exist_company = Company.objects.filter(id_bx=company["ID"]).first()
    if not exist_company:
        # при создании компании
        serializer = CompanySerializer(data=company)
    else:
        # при обновлении компании
        serializer = CompanySerializer(exist_company, data=company)

    if serializer.is_valid():
        serializer.save(url=company["url"])
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
    response_requisite = bx24.call(
        "crm.requisite.list",
        {
            "filter": {"ENTITY_ID": id_company, "ENTITY_TYPE_ID": 4},
            "select": ["RQ_INN"]
        }
    )
    response_address = bx24.call(
        "crm.address.list",
        {
            "filter": {"ENTITY_ID": id_company, "ENTITY_TYPE_ID": 4},
            "select": ["REGION", "CITY", "PROVINCE"]
        }
    )

    if not response_company or not response_requisite or response_address or \
        "result" not in response_company or "result" not in response_requisite or "result" not in response_address:
        pass

    # response = bx24.batch({
    #     "halt": 0,
    #     "cmd": {
    #         "DATA": f"crm.company.get?id={id_company}",
    #         "REQUISITES": f"crm.requisite.list?filter[ENTITY_ID]={id_company}&filter[ENTITY_TYPE_ID]=4&select[0]=RQ_INN",
    #         "ADDRESS": f"crm.address.list?filter[ENTITY_ID]={id_company}&filter[ENTITY_TYPE_ID]=4&select[]=REGION&select[]=CITY&select[]=PROVINCE",
    #     }
    # })
    # company = response.get("result", {}).get("DATA")
    # requisite = response.get("result", {}).get("REQUISITES")
    # address = response.get("result", {}).get("ADDRESS")

    company = response_company["result"]
    requisites = response_requisite["result"]
    address = response_address["result"]

    if requisites and isinstance(requisites, list):
        company = {**company, **requisites}

    if address and isinstance(address, list):
        company = {**company, **address}

    return company


