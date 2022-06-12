from reportactivity.celery import celery_app
import logging
import time

from .serviсes.bitrix24 import requests_bx24
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




# задача по сохранению активности
@celery_app.task
def activity_task(id_activity, event):
    active = True
    if event == "ONCRMACTIVITYDELETE":
        active = False

    return update_or_save_activity(id_activity, active)


# задача по сохранению звонка
@celery_app.task
def calls_task(calls):
    data = {}
    event = calls.get("event", "")
    data["CALL_ID"] = calls.get("data[CALL_ID]", None)
    data["CALL_ID"] = calls.get("data[CALL_ID]", None)
    data["CALL_TYPE"] = calls.get("data[CALL_TYPE]", None)
    data["PHONE_NUMBER"] = calls.get("data[PHONE_NUMBER]", None)
    data["PORTAL_USER_ID"] = calls.get("data[PORTAL_USER_ID]", None)
    data["CALL_DURATION"] = calls.get("data[CALL_DURATION]", None)
    data["CALL_START_DATE"] = calls.get("data[CALL_START_DATE]", None)
    data["CRM_ACTIVITY_ID"] = calls.get("data[CRM_ACTIVITY_ID]", None)

    # обновление или сохранение активности
    res_save_activity = update_or_save_activity(data["CRM_ACTIVITY_ID"], True)

    if not data["CALL_ID"]:
        logger_tasks_error.error({
            "error": "Not transferred ID call",
            "message": "Отсутствует CALL_ID",
            "data": data,
        })
    if not data["CALL_TYPE"]:
        logger_tasks_error.error({
            "error": "Missing call type",
            "message": "Отсутствует CALL_TYPE",
            "data": data,
        })
    if not data["PORTAL_USER_ID"]:
        logger_tasks_error.error({
            "error": "Missing user ID",
            "message": "Отсутствует PORTAL_USER_ID",
            "data": data,
        })
    if not data["CALL_DURATION"]:
        logger_tasks_error.error({
            "error": "The duration of the call is missing",
            "message": "Отсутствует CALL_DURATION",
            "data": data,
        })
    if not data["CALL_START_DATE"]:
        logger_tasks_error.error({
            "error": "The date of the call is missing",
            "message": "Отсутствует CALL_START_DATE",
            "data": data,
        })
    if not data["CRM_ACTIVITY_ID"]:
        logger_tasks_error.error({
            "error": "The id of the related case is missing",
            "message": "Отсутствует CRM_ACTIVITY_ID",
            "data": data,
        })

    exist_activity = Phone.objects.filter(CALL_ID=data["CALL_ID"]).first()

    if exist_activity:
        serializer = CallsSerializer(exist_activity, data=data)
    else:
        serializer = CallsSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        logger_tasks_success.info({
            "message": "Звонок успешно сохранен",
            "id_call": data["CALL_ID"],
            "event": event,
            "result": serializer.data,
        })
        return serializer.data

    logger_tasks_error.error({
        "error": serializer.errors,
        "message": "Ошибка серриализации данных в объект звонка",
        "id_call": data["CALL_ID"],
    })
    return serializer.errors


# задача по сохранению пользователя
@celery_app.task
def user_task(user):
    data = {}
    event = user.get("event", "")
    data["ID"] = user.get("data[ID]", None)
    data["LAST_NAME"] = user.get("data[LAST_NAME]", None)
    data["NAME"] = user.get("data[NAME]", None)
    data["WORK_POSITION"] = user.get("data[WORK_POSITION]", None)

    # подразделение пользователя
    depart = user.get("data[UF_DEPARTMENT]", [])
    if depart:
        data["UF_DEPARTMENT"] = depart[0]

    # сотрудник уволен/не уволен
    active = user.get("ACTIVE", None)
    if active is not None:
        data["ACTIVE"] = active

    # url сотрудника в Битрикс
    data["URL"] = service.get_url_user(data["ID"])

    exist_user = User.objects.filter(ID=data["ID"]).first()

    if exist_user:
        serializer = UsersSerializer(exist_user, data=data)
    else:
        serializer = UsersSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        logger_tasks_success.info({
            "message": "Пользователь успешно сохранен",
            "id_user": data["ID"],
            "result": serializer.data,
        })
        return serializer.data

    logger_tasks_error.error({
        "error": serializer.errors,
        "message": "Ошибка серриализации данных в объект пользователя",
        "id_user": data["ID"]
    })
    return serializer.errors


# получение или сохранение активности
def update_or_save_activity(id_activity, active=True):
    # результат выполнения запроса на получение данных активности
    result_req_activity = bx24.call("crm.activity.get", {"id": id_activity})

    if not result_req_activity or "result" not in result_req_activity:
        logger_tasks_error.error({
            "error": "No response came from BX24",
            "message": "При получении данных активности из Битрикс возникла ошибка",
            "id_activity": id_activity,
            "active": active,
            "result": result_req_activity,
        })
        return "No response came from BX24"

    # получение данных активности
    data_activity = result_req_activity["result"]
    # добавление статуса активности: удалена или нет
    data_activity["active"] = active

    # id ответственного
    id_responsible = data_activity.get("RESPONSIBLE_ID", None)

    # получение или создание пользователя
    responsible = get_or_save_user(id_responsible)

    # список ссылок на фаилы прикрепленные к активности
    files = data_activity.get("FILES", None)

    # получение файла с телефонным разговором
    if files and isinstance(files, list) and len(files) > 0:
        file = data_activity["FILES"][0]
        data_activity["FILES"] = file.get("url", "")
    else:
        data_activity["FILES"] = ""

    # пробразование даты в объект даты
    data_activity["CREATED"] = service.convert_date_to_obj(data_activity["CREATED"])
    data_activity["END_TIME"] = service.convert_date_to_obj(data_activity["END_TIME"])

    company_id = None

    # получение ID компании из лида
    if data_activity["OWNER_TYPE_ID"] == "1" and data_activity["OWNER_ID"]:
        data = bx24.call("crm.lead.get", {"id": data_activity["OWNER_ID"]})
        company_id = data.get("result").get("COMPANY_ID")
        data_activity["OWNER_NAME"] = data.get("result").get("TITLE", None)

    # получение ID компании из сделки
    if data_activity["OWNER_TYPE_ID"] == "2" and data_activity["OWNER_ID"]:
        data = bx24.call("crm.deal.get", {"id": data_activity["OWNER_ID"]})
        company_id = data.get("result").get("COMPANY_ID")
        data_activity["OWNER_NAME"] = data.get("result").get("TITLE", None)

    # получение ID компании из контакта
    if data_activity["OWNER_TYPE_ID"] == "3" and data_activity["OWNER_ID"]:
        data = bx24.call("crm.contact.get", {"id": data_activity["OWNER_ID"]})
        company_id = data.get("result").get("COMPANY_ID")
        lastname = data.get("result").get("LAST_NAME", "")
        name = data.get("result").get("NAME", "")
        data_activity["OWNER_NAME"] = f"{lastname} {name}"

    # получение ID компании из компании
    if data_activity["OWNER_TYPE_ID"] == "4" and data_activity["OWNER_ID"]:
        data = bx24.call("crm.company.get", {"id": data_activity["OWNER_ID"]})
        company_id = data_activity["OWNER_ID"]
        data_activity["OWNER_NAME"] = data.get("result", {}).get("TITLE", None)

    # если id компании владельца активности не найден
    if not company_id:
        logger_tasks_error.error({
            "error": "There are no companies tied to the case",
            "message": "Не удалось получить id компании владельца активности",
            "id_activity": id_activity,
            "active": active,
            "result": result_req_activity,
        })
        return "There are no companies tied to the case"

    data_activity["COMPANY_ID"] = company_id

    # получение активности
    exist_activity = Activity.objects.filter(ID=id_activity).first()

    if exist_activity:
        serializer = ActivityFullSerializer(exist_activity, data=data_activity)
    else:
        serializer = ActivityFullSerializer(data=data_activity)

    if serializer.is_valid():
        serializer.save()
        logger_tasks_success.info({
            "message": "Активность успешно сохранена",
            "id_activity": id_activity,
            "active": active,
            "result": serializer.data,
        })
        return serializer.data

    logger_tasks_error.error({
        "error": serializer.errors,
        "message": "Ошибка серриализации данных в объект активности",
        "id_activity": id_activity
    })
    return serializer.errors


# получение или сохранение пользователя
def get_or_save_user(id_user):
    exist_user = User.objects.filter(ID=id_user).first()

    if exist_user:
        return exist_user

    # результат выполнения запроса на получение данных пользователей
    data_user = bx24.call("user.get", {"id": id_user})

    if not data_user or "result" not in data_user or len(data_user["result"]) == 0:
        logger_tasks_error.error({
            "error": "No response came from BX24",
            "message": "При получении данных пользователя из Битрикс возникла ошибка",
            "id_user": id_user,
            "result": data_user,
        })
        return "No response came from BX24"

    # данные пользователя
    data = data_user["result"][0]

    # url пользователя в Битрикс
    data["URL"] = service.get_url_user(id_user)

    # подразделение пользователя
    department = data["UF_DEPARTMENT"]

    if isinstance(department, list) and len(department) != 0:
        data["UF_DEPARTMENT"] = department[0]
    else:
        data["UF_DEPARTMENT"] = None

    serializer = UsersSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        logger_tasks_success.info({
            "message": "Пользователь успешно сохранен",
            "id_user": id_user,
            "result": serializer.data,
        })
        return serializer.data

    logger_tasks_error.error({
        "error": serializer.errors,
        "message": "Ошибка серриализации данных в объект пользователя",
        "id_user": id_user
    })
    return serializer.errors



