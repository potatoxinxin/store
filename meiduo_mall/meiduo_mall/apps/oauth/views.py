from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .utils import OAuthQQ
from .exceptions import QQAPIException
from .models import OAuthQQUser

# Create your views here.


class OAuthQQURLView(APIView):
    """
    提供 QQ 的登录网址
    前端请求的接口网址 /oauth/qq/authorization/?state=xxxxxx
    state 是由前端传递，参数值为在 QQ 登录成功后，后端把用户引导到哪个美多商城页面
    """
    def get(self, request):
        # 提取 state 参数
        state = request.query_params.get("state")
        if not state:
            state = '/'  # 如果前端未生命，我们设置用户 QQ 登录成功后，跳转到主页

        # 按照 QQ 的说明文档，拼接用户 QQ 登录的链接地址
        oauth = OAuthQQ(state=state)
        auth_url = oauth.get_qq_login_url()

        # 返回链接地址
        return Response({'auth_url': auth_url})


class OAuthQQUserView(APIView):
    """
    获取 QQ 用户对应的美多商城用户
    """
    def get(self, request):
        # 提取 code 参数
        code = request.query_params.get('code')
        if not code:
            return Response({"message": "缺少code"}, status=status.HTTP_400_BAD_REQUEST)

        # 凭借 code 向 qq 服务器发起请求，获取 access_token
        oauth_qq = OAuthQQ()
        try:
            access_token = oauth_qq.get_access_token()

            # 凭借 access_token 向 qq 服务器发起请求，获取openid
            openid = oauth_qq.get_openid()
        except QQAPIException:
            return Response({"message": "获取QQ用户数据异常"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 根据 openid 查询此用户是否之前在美多中绑定用户
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果未绑定，手动创建接下来绑定身份使用的 access_token
            pass
        else:
            # 如果已经绑定，直接生成登录凭证 JWT token， 并返回
            pass
















