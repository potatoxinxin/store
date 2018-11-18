from rest_framework import serializers

from carts.serializers import CartsSKUSerializer


class OrderSettlementSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartsSKUSerializer(many=True, read_only=True)

