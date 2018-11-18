import base64
import pickle

from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.response import Response

from goods.models import SKU
from .serializers import CartSerializer, CartsSKUSerializer

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

    def get(self, request):
        """查询购物车数据"""
        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            # 前端携带了错误的 JWT，或者用户未登录
            user = None

        if user is not None and user.is_authenticated:
            # 如果用户登录，从 redis 中查询
            redis_conn = get_redis_connection('cart')
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)
            cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)

            # 将 redis 中的数据进行整合，形成一个字典，与 cookie 中解读的一致，方便数据库查询
            cart_dict ={}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }

        else:
            # 如果用户未登录，从 cookie 中查询
            cart_str = request.COOKIES.get('cart')

            if cart_str is not None:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        sku_id_list = cart_dict.keys()

        # 数据库查询 sku 对象
        sku_obj_list = SKU.objects.filter(id__in=sku_id_list)

        # 向结果集中补充 count 和 selected 字段
        for sku in sku_obj_list:
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']

        # 将数据序列化返回
        serializer = CartsSKUSerializer(sku_obj_list, many=True)
        return Response(serializer.data)

    def put(self, request):
        """修改购物车数据"""
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

        if user is not None and user.is_authenticated:
            # 用户已登录，修改 redis 中的数据
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hset('cart_%s' % user.id, sku_id, count)

            if selected:
                # 勾选增加记录
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                # 未勾选，删除记录
                pl.srem('cart_selected_%s' % user.id, sku_id)

            pl.execute()
            return Response(serializer.data)

        else:
            # 用户未登录，修改 cookie 中的数据
            cart_str = request.COOKIES.get('cart')

            if cart_str:
                cart_dict = pickle.loads(base64.b16decode(cart_str.encode()))
            else:
                cart_dict = {}

            if sku_id in cart_dict:
                cart_dict[sku_id] = {
                    'count': count,
                    'selected': selected
                }

            cookie_cart = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 返回
            response = Response(serializer.data)
            response.set_cookie('cart', cookie_cart)

            return response






























