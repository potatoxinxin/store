from django.conf import settings
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
import logging
import json
import re

from .exceptions import QQAPIException

logger = logging.getLogger('django')


class OAuthQQ(object):
    """
    用户 QQ 登录的工具类
    提供了 QQ 登录可能使用的方法
    """
    def __init__(self, app_id=None, app_key=None, redirect_uri=None, state=None):
        self.app_id = app_id or settings.QQ_APP_ID
        self.app_key = app_key or settings.QQ_APP_KEY
        self.redirect_url = redirect_uri or settings.QQ_REDIRECT_URL
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
            'redirect_uri': self.redirect_url,
            'state': self.state,
            'scope': 'get_user_info',  # 获取用户的 openid
        }
        query_string = urlencode(data)
        url += query_string
        print("QQ 登录的链接地址： %s" % url)

        return url

    def get_access_token(self, code):
        """
        获取 qq 的 access_token
        :param code: 调用的凭据
        :return: access_token
        """
        url = 'https://graph.qq.com/oauth2.0/token?'

        req_data = {
            'grant_type': 'authorization_code',
            'client_id': self.app_id,
            'client_secret': self.app_key,
            'code': code,
            'redirect_uri': self.redirect_url
        }

        url += urlencode(req_data)

        try:
            # 发起请求
            response = urlopen(url)

            # 读取 QQ 返回的响应体数据
            response = response.read().decode()

            # 将返回的数据转为字典
            resp_dict = parse_qs(response)

            access_token = resp_dict.get('access_token')[0]

            # access_token = parse_qs(urlopen(url).read().decode()).get('access_token')[0]
        except Exception as e:
            logger.error(e)
            raise QQAPIException("获取 access_token 异常")

        return access_token

    def get_openid(self, access_token):
        """
        获取用户的openid
        :param access_token: qq提供的access_token
        :return: open_id
        """
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token

        try:
            response = urlopen(url)
            response_data = response.read().decode()
            # 返回的数据 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            # data = json.loads(response_data[10:-4])
            # 使用正则来提取参数
            data = json.loads(re.match(r'callback\( (.*) \)', response_data).group(1))
        except Exception:
            data = parse_qs(response_data)
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIException('获取openid异常')

        openid = data.get('openid', None)

        return openid












