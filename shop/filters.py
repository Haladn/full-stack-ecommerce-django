import django_filters
from end_point.models import Laptop

class LapotopFilter(django_filters.FilterSet):
    description=django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model=Laptop
        fields=['description']