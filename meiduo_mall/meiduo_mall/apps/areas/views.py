from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .models import Area
from . import serializers

# Create your views here.


class AreasViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    """
    list:
    返回所有省份的信息

    retrieve:
    返回特定省或市的下属行政规划区域
    """
    # queryset = Area.objects.all()
    pagination_class = None  # 关闭分页处理

    def get_queryset(self):
        """
        提供数据集
        """
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        """
        提供序列化器
        """
        if self.action == 'list':
            return serializers.AreaSerializer
        else:
            return serializers.SubAreaSerializer



