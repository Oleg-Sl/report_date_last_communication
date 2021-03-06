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
    def statistic_company(self, duration):
        return self.annotate(
            summa_by_company_success=models.functions.Coalesce(
                models.Sum(
                    "deal__opportunity",
                    filter=models.Q(deal__stage__status="SUCCESSFUL"),
                    output_field=models.FloatField()
                ),
                models.Value(0),
                output_field=models.FloatField()
            ),
            summa_by_company_work=models.functions.Coalesce(
                models.Sum(
                    "deal__opportunity",
                    filter=models.Q(deal__stage__status="WORK"),
                    output_field=models.FloatField()
                ),
                models.Value(0),
                output_field=models.FloatField()
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
        from .models import Deal, Company
        return self.filter(
            company__pk__in=companies,
        ).values(
            "company__pk", "direction"
        ).annotate(
            name=models.F("direction__name"),
            # ???????? ???????????????????? ?????????????????? ????????????
            date_last_modify=models.Max("date_modify"),
            # ??????-???? ???????????? ?? ????????????
            count_deals_in_work=models.Count("pk", filter=models.Q(closed=False)),
            # ???????? ???? ???????????????????????? ???????????? ?? ????????????
            actual_deal_work=models.ExpressionWrapper(
                models.Q(stage__status="WORK") & models.Q(date_modify__gte=lim_date_suspended_deals),
                output_field=models.BooleanField()
            ),
            # ???????? ???? ???????????????????????? ???????????? ???? ???????????????????? ?? ????????????
            actual_deal_preparation=models.ExpressionWrapper(
                models.Q(stage__status="PREPARATION") & models.Q(date_modify__gte=lim_date_suspended_deals),
                output_field=models.BooleanField()
            ),
            # ???????? ???? ???????????????????????? ???????????????????? ????????????
            actual_deal_failed=models.ExpressionWrapper(
                models.Q(stage__status="FAILURE") & models.Q(date_modify__gte=lim_date_failed_deals),
                output_field=models.BooleanField()
            ),
            # ?????????? ???????????????????? ???????????????? ????????????
            # opportunity_success=models.Sum("opportunity", filter=models.Q(stage__status="SUCCESSFUL")),
            opportunity_success=models.Subquery(
                    Company.statistic.filter(
                        pk=models.OuterRef('company__pk'),
                        deal__direction=models.OuterRef('direction__pk'),
                        deal__stage__status="SUCCESSFUL"
                    ).annotate(
                        s=models.Sum('deal__opportunity')
                    ).values('s')[:1]
                ),
            # ?????????? ???????????????????? ???????????? ?? ????????????
            opportunity_work=models.Subquery(
                    Company.statistic.filter(
                        pk=models.OuterRef('company__pk'),
                        deal__direction=models.OuterRef('direction__pk'),
                        deal__stage__status="WORK"
                    ).annotate(
                        s=models.Sum('deal__opportunity')
                    ).values('s')[:1]
                ),
            # summa_by_company_success=models.Subquery(
            #     Deal.objects.filter(
            #         company=models.OuterRef('company__pk'),
            #         direction__new=True
            #         # stage__status="SUCCESSFUL"
            #     ).annotate(
            #         s=models.Sum('opportunity')
            #     ).values('s')[:1]
            # ),
            # summa_by_company_work=models.Subquery(
            #     Deal.objects.filter(
            #         company=models.OuterRef('company__pk'),
            #         direction__new=True
            #         # stage__status="WORK"
            #     ).annotate(
            #         s=models.Sum('opportunity')
            #     ).values('s')[:1]
            # ),
            # models.Sum("opportunity", filter=models.Q(stage__status="WORK")),
        )

    def statistic_company_summary(self, companies):
        from .models import Deal
        return self.filter(
            company__pk__in=companies,
        ).values(
            "company__pk"
        ).annotate(
            summa_by_company_success=models.Sum("opportunity", filter=models.Q(direction__new=True, stage__status="SUCCESSFUL")),
            # summa_by_company_success=models.Subquery(
            #     Deal.objects.filter(
            #         company=models.OuterRef('company__pk'),
            #         direction__new=True,
            #         stage__status="SUCCESSFUL"
            #     ).annotate(
            #         s=models.Sum('opportunity')
            #     ).values('s')[:1]
            # ),
            summa_by_company_work=models.Subquery(
                Deal.objects.filter(
                    company=models.OuterRef('company__pk'),
                    direction__new=True,
                    stage__status="WORK"
                ).annotate(
                    s=models.Sum('opportunity')
                ).values('s')[:1]
            ),
        )


class CompanyNewQuerySet(models.QuerySet):
    def statistic_company_new(self, directions, duration):
        return self
        #     .annotate(
        #     summa_by_company_success=models.Sum(
        #         "deal__opportunity",
        #         filter=models.Q(deal__direction__in=directions, deal__stage__status="SUCCESSFUL"),
        #         output_field=models.FloatField()
        #     ),
        #     summa_by_company_work=models.Sum(
        #         "deal__opportunity",
        #         filter=models.Q(deal__direction__in=directions, deal__stage__status="WORK"),
        #         output_field=models.FloatField()
        #     ),
        #     dpk=models.functions.Coalesce(
        #         models.Max("calls__start_date", filter=models.Q(calls__duration__gte=duration)),
        #         datetime.date(2000, 1, 1)
        #     )
        # )


class CompanyNewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(id_bx=0)

    def statistic_company_by_directions(self, companies, lim_date_suspended_deals, lim_date_failed_deals):
        from .models import Deal
        return self.filter(
            pk__in=companies,
        ).values(
            "pk", "deal__direction"
        ).annotate(
            name=models.F("deal__direction__name"),
            # ???????? ???????????????????? ?????????????????? ????????????
            date_last_modify=models.Max("deal__date_modify"),
            # ??????-???? ???????????? ?? ????????????
            count_deals_in_work=models.Count("deal", filter=models.Q(closed=False)),
            # ???????? ???? ???????????????????????? ???????????? ?? ????????????
            actual_deal_work=models.ExpressionWrapper(
                models.Q(deal__stage__status="WORK") & models.Q(deal__date_modify__gte=lim_date_suspended_deals),
                output_field=models.BooleanField()
            ),
            # ???????? ???? ???????????????????????? ???????????? ???? ???????????????????? ?? ????????????
            actual_deal_preparation=models.ExpressionWrapper(
                models.Q(deal__stage__status="PREPARATION") & models.Q(deal__date_modify__gte=lim_date_suspended_deals),
                output_field=models.BooleanField()
            ),
            # ???????? ???? ???????????????????????? ???????????????????? ????????????
            actual_deal_failed=models.ExpressionWrapper(
                models.Q(deal__stage__status="FAILURE") & models.Q(deal__date_modify__gte=lim_date_failed_deals),
                output_field=models.BooleanField()
            ),
            # ?????????? ???????????????????? ???????????????? ????????????
            opportunity_success=models.Sum("deal__opportunity", filter=models.Q(deal__stage__status="SUCCESSFUL")),
            # ?????????? ???????????????????? ???????????? ?? ????????????
            # opportunity_work=models.Sum("opportunity", filter=models.Q(stage__status="WORK")),
            opportunity_work=models.Subquery(
                    Deal.objects.filter(
                        company=models.OuterRef('pk'),
                        direction=models.OuterRef('deal__direction__pk'),
                        stage__status="WORK"
                    ).annotate(
                        s=models.Sum('opportunity')
                    ).values('s')[:1]
                ),
            summa_by_company_success=models.Subquery(
                Deal.objects.filter(
                    company=models.OuterRef('pk'),
                    direction__new=True
                    # stage__status="SUCCESSFUL"
                ).annotate(
                    s=models.Sum('opportunity')
                ).values('s')[:1]
            ),
            summa_by_company_work=models.Subquery(
                Deal.objects.filter(
                    company=models.OuterRef('pk'),
                    direction__new=True
                    # stage__status="WORK"
                ).annotate(
                    s=models.Sum('opportunity')
                ).values('s')[:1]
            ),
            # models.Sum("opportunity", filter=models.Q(stage__status="WORK")),
        )

    def statistic_company_summary(self, companies):
        from .models import Deal, Company
        return self.filter(
            pk__in=companies,
        ).annotate(
            summa_by_company_success=models.Subquery(
                Company.statistic.filter(
                    pk=models.OuterRef('pk'),
                    deal__direction__new=True,
                    deal__stage__status="SUCCESSFUL"
                ).annotate(
                    s=models.Sum('deal__opportunity')
                ).values('s')[:1]
            ),
            summa_by_company_work=models.Subquery(
                Company.statistic.filter(
                    pk=models.OuterRef('pk'),
                    deal__direction__new=True,
                    deal__stage__status="WORK"
                ).annotate(
                    s=models.Sum('deal__opportunity')
                ).values('s')[:1]
            ),
        ).values(
            "pk", "summa_by_company_success", "summa_by_company_work"
        )



#
# class CompanyQuerySetOld(models.QuerySet):
#     def statistic_company(self, directions, duration):
#         from .models import Deal
#         return self.annotate(
#             summa_by_company_success=models.functions.Coalesce(
#                 models.Subquery(
#                     Deal.objects.filter(
#                         company=models.OuterRef('pk'),
#                         direction__in=directions,
#                         stage__status="SUCCESSFUL"
#                     ).annotate(
#                         s=models.Sum('opportunity')
#                     ).values('s')[:1]
#                 ),
#                 # models.Sum(
#                 #     "deal__opportunity",
#                 #     filter=models.Q(deal__direction__in=directions, deal__stage__status="SUCCESSFUL"),
#                 #     output_field=models.FloatField()
#                 # ),
#                 models.Value(0),
#                 output_field=models.FloatField()
#             ),
#             summa_by_company_work=models.functions.Coalesce(
#                 models.Subquery(
#                     Deal.objects.filter(
#                         company=models.OuterRef('pk'),
#                         direction__in=directions,
#                         stage__status="WORK"
#                     )
#                     # .aggregate(
#                     #     s=models.Sum('opportunity')
#                     # ).values('s')[:1]
#                     # .annotate(
#                     .annotate(
#                         s=models.Sum('opportunity')
#                     ).values('s')[:1]
#                 ),
#                 models.Value(0),
#                 output_field=models.FloatField()
#                 # models.Sum(
#                 #     "deal__opportunity",
#                 #     filter=models.Q(deal__direction__in=directions, deal__stage__status="WORK"),
#                 #     output_field=models.FloatField()
#                 # ),
#                 # 0.0
#             ),
#             dpk=models.functions.Coalesce(
#                 models.Max("calls__start_date", filter=models.Q(calls__duration__gte=duration)),
#                 datetime.date(2000, 1, 1)
#             )
#         )
#

# Deal.objects.filter(company__pk__in=[162, 172, 202]).values("company__pk", "direction").annotate(opportunity=models.Subquery(Deal.objects.filter(company=models.OuterRef('company__pk'), direction=models.OuterRef('direction__pk'), stage__status="WORK").aggregate(s=models.Sum('opportunity'))))
# Deal.objects.filter(company__pk__in=[162, 172, 202]).values("company__pk", "direction").annotate(opportunity=models.Subquery(Deal.objects.filter(company=162, stage__status="WORK").aggregate(s=models.functions.Cast(models.Sum('opportunity'), output_field=models.FloatField()))["s"]))
# Deal.objects.filter(company__pk__in=[162, 172, 202]).values("company__pk", "direction").annotate(opportunity=models.Subquery(Deal.objects.filter(company=162, stage__status="WORK").aggregate(s=models.Sum('opportunity')).values()))
#
# Deal.objects.filter(company=162, stage__status="WORK").aggregate(s=models.Sum('opportunity'))
# Deal.objects.filter(company=162, stage__status="WORK").annotate(s=models.Sum('opportunity')).values('company')[:1]
#
#
# Company.statistic.filter(pk=162, deal__stage__status="WORK").annotate(s=models.Sum('deal__opportunity')).values('s')[:1]
# Company.statistic.filter(pk=162, deal__stage__status="SUCCESSFUL").annotate(s=models.Sum('deal__opportunity')).values('s')[:1]

