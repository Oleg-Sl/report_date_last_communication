from django_filters import rest_framework as filters


from mainapp.models import (
    Direction,
    Stage,
    Company,
    Deal
)


class CompanyIdFilter(filters.RangeFilter, filters.DateFilter):
    pass


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class StatisticCompany(filters.FilterSet):
    company = NumberInFilter(field_name='pk', lookup_expr='in')
    responsible = NumberInFilter(field_name='responsible', lookup_expr='in')

    sector = filters.CharFilter()
    region = filters.CharFilter()
    source = filters.CharFilter()
    requisite_region = filters.CharFilter()
    requisites_city = filters.CharFilter()

    revenue = filters.RangeFilter()
    number_employees = filters.RangeFilter()
    date_created = filters.DateFromToRangeFilter()

    class Meta:
        model = Company
        fields = ["company", "responsible", "sector", "region", "source",
                  "requisite_region", "requisites_city", "number_employees", "revenue", "date_created"]


class StatisticCompanyByDirection(filters.FilterSet):
    company = NumberInFilter(field_name='pk', lookup_expr='in')

    class Meta:
        model = Company
        fields = ["company", ]


class StatisticByDirection(filters.FilterSet):
    direction = NumberInFilter(field_name='pk', lookup_expr='in')

    class Meta:
        model = Direction
        fields = ["direction", ]
