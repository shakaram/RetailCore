from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import ValidationError

class PriceFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        price_min = request.query_params.get('price_min')
        price_max = request.query_params.get('price_max')

        try:
            if price_min is not None:
                price_min = int(price_min)  
                queryset = queryset.filter(price__gte=price_min)
            
            if price_max is not None:
                price_max = int(price_max)
                queryset = queryset.filter(price__lte=price_max)
        except ValueError:
            raise ValidationError("مقدار قیمت باید عددی باشد.")

        return queryset
