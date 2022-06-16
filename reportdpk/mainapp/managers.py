from django.db import models


DIRECTION_IGNORE_LIST = [21, 23, 27, 41, 45]


class DirectionActualManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(pk__in=DIRECTION_IGNORE_LIST).filter(new=True)


class CompanyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(id_bx=0)

    def statistic_company(self, directions):
        return self.annotate(
            summa_by_company_success=models.Sum(
                "deal__opportunity",
                filter=models.Q(deal__direction__in=directions, deal__stage__status="SUCCESSFUL"),
                output_field=models.FloatField()
            ),
            summa_by_company_work=models.Sum(
                "deal__opportunity",
                filter=models.Q(deal__direction__in=directions, deal__stage__status="WORK"),
                output_field=models.FloatField()
            ),
            dpk=models.Max("calls__start_date", filter=models.Q(calls__duration__gte=0))
        )


class DealManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(direction__pk__in=DIRECTION_IGNORE_LIST)

    def statistic_company_by_directions(self, companies, directions, lim_date_suspended_deals, lim_date_failed_deals):
        return self.filter(
            company__pk__in=companies,
            direction__pk__in=directions,
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
            # есть не просроченные сделки в работе
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

