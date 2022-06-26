from django.db import models
from django.conf import settings


import datetime

# from .models import Deal as Dea


class DirectionActualManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(pk__in=settings.DIRECTION_IGNORE_LIST).filter(new=True)

    def count_active_deals(self):
        return self.annotate(
            count_active_deal=models.Count(
                "deal",
                filter=models.Q(deal__closed=False)
            )
        ).values('count_active_deal', 'id_bx', 'name')
            # .values('count_active_deal', 'id_bx')
            # annotate(direction=models.F("id_bx"))


class CompanyQuerySet(models.QuerySet):
    def statistic_company(self, directions, duration):
        return self.annotate(
            summa_by_company_success=models.functions.Coalesce(
                # models.Subquery(
                #     Deal.objects.filter(
                #         company=models.OuterRef('pk'),
                #         direction__in=directions,
                #         stage__status="SUCCESSFUL"
                #     ).annotate(
                #         s=models.Sum('summa')
                #     ).values('s')[:1]
                # ),
                models.Sum(
                    "deal__opportunity",
                    filter=models.Q(deal__direction__in=directions, deal__stage__status="SUCCESSFUL"),
                    output_field=models.FloatField()
                ),
                0.0
            ),
            summa_by_company_work=models.functions.Coalesce(
                models.Sum(
                    "deal__opportunity",
                    filter=models.Q(deal__direction__in=directions, deal__stage__status="WORK"),
                    output_field=models.FloatField()
                ),
                0.0
            ),
            dpk=models.functions.Coalesce(
                models.Max("calls__start_date", filter=models.Q(calls__duration__gte=duration)),
                datetime.date(2000, 1, 1)
            )
        )


class CompanyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(id_bx=0)


class DealManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(direction__pk__in=settings.DIRECTION_IGNORE_LIST)

    def statistic_company_by_directions(self, companies, directions, lim_date_suspended_deals, lim_date_failed_deals):
        return self.filter(
            company__pk__in=companies,
            # direction__pk__in=directions,
        ).values(
            "company__pk", "direction"
        ).annotate(
            name=models.F("direction__name"),
            # дата последнего изменения сделки
            date_last_modify=models.Max("date_modify"),
            # кол-во сделок в работе
            count_deals_in_work=models.Count("pk", filter=models.Q(closed=False)),
            # есть не просроченные сделки в работе
            actual_deal_work=models.ExpressionWrapper(
                models.Q(stage__status="WORK") & models.Q(date_modify__gte=lim_date_suspended_deals),
                output_field=models.BooleanField()
            ),
            # есть не просроченные сделки на подготовке к работе
            actual_deal_preparation=models.ExpressionWrapper(
                models.Q(stage__status="PREPARATION") & models.Q(date_modify__gte=lim_date_suspended_deals),
                output_field=models.BooleanField()
            ),
            # есть не просроченные провальные сделки
            actual_deal_failed=models.ExpressionWrapper(
                models.Q(stage__status="FAILURE") & models.Q(date_modify__gte=lim_date_failed_deals),
                output_field=models.BooleanField()
            ),
            # сумма стоимостей успешных сделок
            opportunity_success=models.Sum("opportunity", filter=models.Q(stage__status="SUCCESSFUL")),
            # сумма стоимостей сделок в работе
            opportunity_work=models.Sum("opportunity", filter=models.Q(stage__status="WORK")),
        )

