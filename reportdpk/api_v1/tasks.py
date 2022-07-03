from reportdpk.celery import celery_app

from .services.tasks import company, stages, directions, deal, calls


@celery_app.task
def directions_create_or_update():
    return directions.create_or_update()


@celery_app.task
def stages_create_or_update(id_direction):
    return stages.create_or_update(id_direction)


@celery_app.task
def company_create_or_update(id_company):
    return company.create_or_update(id_company)


@celery_app.task
def deal_create_or_update(id_deal):
    return deal.create_or_update(id_deal)


@celery_app.task
def calls_create_or_update(id_call):
    return calls.create_or_update(id_call)
