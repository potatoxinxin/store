from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .utils import OAuthQQ

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









