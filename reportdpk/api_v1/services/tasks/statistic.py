from datetime import datetime, timedelta, timezone
from django.db import models
# import django_filters.rest_framework
# django_filters.rest_framework.DjangoFilterBackend
# from rest_framework import generics, views, viewsets
# from django_filters import rest_framework

from mainapp.models import Company, Direction, Deal
from api_v1.serializers import StatisticCompanySerializer


def get_summary_data_on_companies():
    directions_actual = Direction.direction_actual.values('pk')

    queryset = Company.objects.annotate(
        summa_by_company_success=models.Sum(
            "deal__opportunity",
            filter=models.Q(deal__direction__in=directions_actual, deal__stage__status="SUCCESSFUL"),
            output_field=models.FloatField()
        ),
        summa_by_company_work=models.Sum(
            "deal__opportunity",
            filter=models.Q(deal__direction__in=directions_actual, deal__stage__status="WORK"),
            output_field=models.FloatField()
        ),
        dpk=models.Max("calls__start_date", filter=models.Q(calls__duration__gte=0))
    )

    return StatisticCompanySerializer(queryset, many=True).data


def get_summary_data_on_companies_and_directories(companies_ids, directions_ids,
                                                  delta_days_for_suspended_deals, delta_days_for_failed_deals):
    limit_date_suspended_deals = datetime.now(timezone.utc) - timedelta(days=delta_days_for_suspended_deals)
    limit_date_failed_deals = datetime.now(timezone.utc) - timedelta(days=delta_days_for_failed_deals)

    queryset = Deal.objects.values(
        "company__pk", "direction"
    ).filter(
        company__pk__in=companies_ids,
        direction__pk__in=directions_ids,
    ).annotate(
        name=models.F("direction__name"),
        # дата последнего изменения сделки
        date_last_modify=models.Max("date_modify"),
        # кол-во сделок в работе
        count_deals_in_work=models.Count("pk", filter=models.Q(closed=False)),
        # есть не просроченные сделки в работе
        actual_deal_work=models.ExpressionWrapper(
            models.Q(stage__status="WORK") & models.Q(date_modify__gte=limit_date_suspended_deals),
            output_field=models.BooleanField()
        ),
        # есть не просроченные сделки в работе
        actual_deal_preparation=models.ExpressionWrapper(
            models.Q(stage__status="PREPARATION") & models.Q(date_modify__gte=limit_date_suspended_deals),
            output_field=models.BooleanField()
        ),
        # есть не просроченные провальные сделки
        actual_deal_failed=models.ExpressionWrapper(
            models.Q(stage__status="FAILURE") & models.Q(date_modify__gte=limit_date_failed_deals),
            output_field=models.BooleanField()
        ),
        # сумма стоимостей успешных сделок
        opportunity_success=models.Sum("opportunity", filter=models.Q(stage__status="SUCCESSFUL")),
        # сумма стоимостей сделок в работе
        opportunity_work=models.Sum("opportunity", filter=models.Q(stage__status="WORK")),
    )

    return converting_list_to_dict(queryset, "company__pk", "direction")


def converting_list_to_dict(queryset, key_depth_first, key_depth_second):
    response = {}
    for element in queryset:
        if not response.get(element[key_depth_first]):
            response[element[key_depth_first]] = {}

        response[element[key_depth_first]][element[key_depth_second]] = element

    return response


# queryset = Company.objects.exclude(id_bx=0).annotate(
#         summa_by_company_success=models.functions.Coalesce(
#             models.Sum(
#                 "deal__opportunity",
#                 filter=models.Q(deal__direction__in=directions_actual, deal__stage__won=True),
#                 output_field=models.FloatField()
#             ),
#             models.Value("0")
#         ),
#         summa_by_company_work=models.functions.Coalesce(
#             models.Sum(
#                 "deal__opportunity",
#                 filter=models.Q(deal__direction__new=True, deal__stage__status="WORK"),
#                 output_field=models.FloatField()
#             ),
#             models.Value("0")
#         ),
#         dpk=models.Max("calls__start_date", filter=models.Q(calls__duration__gte=0))
#     )
