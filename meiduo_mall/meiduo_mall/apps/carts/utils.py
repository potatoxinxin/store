import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response, user):
    """
    登录后合并购物车， cookie 保存到 redis 中
    :param request:
    :param response:
    :param user:
    :return:
    """
    # 从 cookie 中取出购物车数据
    cart_str = request.COOKIES.get('cart')

    if not cart_str:
        return response

    cookie_cart = pickle.loads(base64.b64decode(cart_str.encode()))

    # 从 redis 中取出购物车数据
    redis_conn = get_redis_connection('cart')
    cart_redis = redis_conn.hgetall('cart_%s' % user.id)

    # 把 redis 中取出的字典的键值对数据类型转换为 int
    cart = {}
    for sku_id, count in cart_redis.items():
        cart[int(sku_id)] = int(count)

    selected_sku_id_list = []
    for sku_id, selected_count_dict in cookie_cart.items():
        # 如果 redis 购物车中原有商品数据，数量覆盖，如果没有，添加记录
        cart[sku_id] = selected_count_dict['count']

        if selected_count_dict['selected']:
            selected_sku_id_list.append(sku_id)

    # 将 cookie 的购物车合并到 redis 中
    pl = redis_conn.pipeline()
    # 购物车数据
    pl.hmset('cart_%s' % user.id, cart)
    # 勾选状态
    pl.sadd('cart_selected_%s' % user.id, *selected_sku_id_list)

    pl.execute()

    # 清楚 cookie 中的购物车数据
    response.delete_cookie('cart')

    return response






