from django.conf import settings
from urllib.parse import urlencode


class OAuthQQ(object):
    """
    用户 QQ 登录的工具类
    提供了 QQ 登录可能使用的方法
    """
    def __init__(self, app_id=None, app_key=None, redirect_uri=None, state=None):
        self.app_id = app_id or settings.QQ_APP_ID
        self.app_key = app_key or settings.QQ_APP_KEY
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE  # 用于保存登录成功后的跳转页面路径

    def get_qq_login_url(self):
        """
        拼接用户 QQ 登录的链接地址
        :return: 链接地址
        """
        url = 'https://graph.qq.com/oauth2.0/authorize?'
        data = {
            'response_type': 'code',
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'get_user_info',  # 获取用户的 openid
        }
        query_string = urlencode(data)
        url += query_string
        print("QQ 登录的链接地址： %s" % url)

        return url







