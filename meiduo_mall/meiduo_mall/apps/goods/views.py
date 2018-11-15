from django.shortcuts import render
from rest_framework.generics import ListAPIView

from .serializers import SKUSerializer
from .models import SKU
from . import constants

# Create your views here.


from rest_framework_extensions.cache.mixins import ListCacheResponseMixin

class HotSKUListView(ListCacheResponseMixin, ListAPIView):
    """
    热销商品, 使用缓存扩展
    """
    serializer_class = SKUSerializer
    pagination_class = None

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:constants.HOT_SKUS_COUNT_LIMIT]
