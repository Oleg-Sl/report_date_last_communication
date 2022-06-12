from mainapp.models import Direction
from api_v1.serializers import DirectionSerializer
from api_v1.services.bitrix24 import requests_bx24
from . import stages

# объект выполнения запросов к Битрикс
bx24 = requests_bx24.Bitrix24()


def create_or_update():
    """ Сохранение всех направлений сделок из BX24 """
    categories_old = get_directions_old()
    categories_new = get_directions_new()
    results = []

    for category in categories_old + categories_new:
        exist_category = Direction.objects.filter(id_bx=category["id_bx"]).first()
        if not exist_category:
            # при создании
            serializer = DirectionSerializer(data=category)
        else:
            # при обновлении
            serializer = DirectionSerializer(exist_category, data=category)
        if serializer.is_valid():
            serializer.save()
            response = serializer.data
        else:
            response = serializer.errors

        stage = stages.create_or_update(category["id_bx"])
        response["stage"] = stage
        results.append(response)

    return results


def get_directions_old():
    """ Влзвращает все направления сделок"""
    entity_type_id = 2    # тип сущности: 2 - сделка
    response_directions = bx24.call(
        "crm.category.list",
        {
            "entityTypeId": entity_type_id
        }
    )
    categories = response_directions.get("result", {}).get("categories", [])

    results = []
    for category in categories:
        results.append({
            "id_bx": category["id"],
            "name": category["name"],
            "new": False,
            "general_id_bx": category["id"],
        })

    return results


def get_directions_new():
    """ Возвращвет новые направления с точкой из 43-го """
    response_directions = bx24.call(
        "crm.deal.fields",
        {}
    )
    categories = response_directions.get("result", {}).get("UF_CRM_1610523951", {}).get("items", [])

    results = []
    for category in categories:
        results.append({
            "id_bx": category["ID"],
            "name": category["VALUE"],
            "new": True,
            "general_id_bx": 43,
        })

    return results




