import json
import pprint
import os
from django.conf import settings

from mainapp.models import Stage
from api_v1.serializers import StageSerializer
from api_v1.services.bitrix24 import requests_bx24


# Имя файла с параметрами стадий
PARAMS_STAGES_FILE_NAME = "params_stages.json"
# объект выполнения запросов к Битрикс
bx24 = requests_bx24.Bitrix24()


def create_or_update(id_direction):
    """ Сохранение всех стадий переданного направления сделки из BX24 """
    results = []
    params_stages = get_params_stages()

    response_stages = bx24.call(
        "crm.status.list",
        {
            "filter": {"CATEGORY_ID": id_direction}
        }
    )
    stages = response_stages.get("result", [])

    for stage in stages:
        stage["id_bx"] = stage["ID"]
        stage["abbrev"] = stage["STATUS_ID"]
        stage["name"] = stage["NAME"]
        stage["won"] = params_stages[stage["STATUS_ID"]]["won"] if params_stages.get(stage["STATUS_ID"]) else None
        stage["status"] = params_stages[stage["STATUS_ID"]]["status"] if params_stages.get(stage["STATUS_ID"]) else None
        stage["direction"] = stage["CATEGORY_ID"]
        # results.append(stage)
        exist_stage = Stage.objects.filter(id_bx=stage["id_bx"]).first()
        if not exist_stage:
            # при создании
            serializer = StageSerializer(data=stage)
        else:
            # при обновлении
            serializer = StageSerializer(exist_stage, data=stage)
        if serializer.is_valid():
            serializer.save()
            results.append(serializer.data)
            continue
        results.append(serializer.errors)

    return results


def get_params_stages():
    with open(os.path.join(settings.BASE_DIR, PARAMS_STAGES_FILE_NAME)) as params_stages_file:
        params_stages = json.load(params_stages_file)

    return params_stages

