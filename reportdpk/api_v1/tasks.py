from reportdpk.celery import celery_app

from .services.tasks import company, stages, directions, deal, calls


@celery_app.task
def directions_create_or_update():
    directions.create_or_update()


@celery_app.task
def stages_create_or_update(id_direction):
    stages.create_or_update(id_direction)


@celery_app.task
def company_create_or_update(id_company):
    company.create_or_update(id_company)


@celery_app.task
def deal_create_or_update(id_deal):
    deal.create_or_update(id_deal)


@celery_app.task
def calls_create_or_update(id_call):
    calls.create_or_update(id_call)
