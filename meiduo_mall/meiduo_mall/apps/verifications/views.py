from django.shortcuts import render
from django_redis import get_redis_connection
from django.http.response import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
import random
from rest_framework.response import Response

from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.libs.yuntongxun.sms import CCP
from . import constants
from . import serializers
from users.models import User
from celery_tasks.sms.tasks import send_sms_code
# Create your views here.


class ImageCodeView(APIView):
    """
    图片验证码
    """

    def get(self, request, image_code_id):
        """
        获取图片验证码
        """
        # 生成验证码图片
        text, image = captcha.generate_captcha()

        redis_conn = get_redis_connection("verify_codes")
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 固定返回验证码图片数据，不需要REST framework框架的Response帮助我们决定返回响应数据的格式
        # 所以此处直接使用Django原生的HttpResponse即可
        return HttpResponse(image, content_type="images/jpg")


class SMSCodeView(GenericAPIView):
    serializer_class = serializers.CheckImageCodeSerializer

    def get(self, request, mobile):
        # 校验图片验证码和发送短信的频次
        # mobile 是被放到了类视图对象属性的 kwargs 中
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 校验通过
        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)

        print("短信验证码是：%s" % sms_code)

        # 保存验证码及发送记录
        redis_conn = get_redis_connection('verify_codes')
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 使用 redis 的 pipeline 管道一次执行多个命令  与redis数据库连接一次就好
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行 pl
        pl.execute()

        # # 发送短信
        # ccp = CCP()
        # time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
        # ccp.send_template_sms(mobile, [sms_code, time], constants.SMA_CODE_TEMP_ID)
        # 使用 celery 发布异步任务
        send_sms_code.delay(mobile, sms_code)

        # 返回
        return Response({'message': 'OK'})


class SMSCodeByTokenView():
    """
    根据 access_token 发送短信
    """
    def get(self, request):
        # 获取并校验 access_token
        access_token = request.query_params('access_token')
        if not access_token:
            return Response({"message": "缺少 access_token"}, status=status.HTTP_400_BAD_REQUEST)

        # 从 access_token 中取出手机号
        mobile = User.check_send_sms_code_token(access_token)
        if mobile is None:
            return Response({"message": "无效的 access_token"}, status=status.HTTP_400_BAD_REQUEST)

        # 判断手机号发送的次数
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return Response({"message": "发送短信次数过于频繁"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 生产短信验证码
        # 发送短信验证码
        # 校验通过
        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)

        print("短信验证码是：%s" % sms_code)

        # 保存验证码及发送记录
        redis_conn = get_redis_connection('verify_codes')
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 使用 redis 的 pipeline 管道一次执行多个命令  与redis数据库连接一次就好
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行 pl
        pl.execute()

        # # 发送短信
        # ccp = CCP()
        # time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
        # ccp.send_template_sms(mobile, [sms_code, time], constants.SMA_CODE_TEMP_ID)
        # 使用 celery 发布异步任务
        send_sms_code.delay(mobile, sms_code)

        # 返回
        return Response({'message': 'OK'})











