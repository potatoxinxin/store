import base64
import pickle

from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.response import Response

from .serializers import CartSerializer

# Create your views here.


class CartView(APIView):
    """
    购物车
    """
    def perform_authentication(self, request):
        """重新检查 JWT token 是否正确   忽略掉"""
        pass

    def post(self, request):
        """保存购物车数据"""
        # 检查前端发送的数据是否正确
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        # 保存购物车数据
        if user is not None and user.is_authenticated:
            # 用户已登录， 保存到 redis 中
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()

            # 购物车数据 hash
            pl.hincrby('cart_%s' % user.id, sku_id, count)

            # 勾选 set
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)

            pl.execute()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            # 用户未登录，保存到 cookie 中
            # 尝试从 cookie 中读取购物车数据
            cart_str = request.COOKIES.get('cart')
            if cart_str is not None:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            # 如果有相同商品，求和
            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            cookie_cart = base64.b64encode(pickle.dump(cart_dict)).decode()

            response = Response(serializer.data, status=status.HTTP_201_CREATED)

            response.set_cookie('cart', cookie_cart)

            # 返回
            return response






