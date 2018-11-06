from rest_framework import serializers
from django_redis import get_redis_connection


class CheckImageCodeSerializer(serializers.Serializer):
    """
    图片验证码校验序列化器
    """
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(min_length=4, max_length=4)

    def validate(self, attrs):
        """校验图片验证码是否正确"""
        image_code_id = attrs['image_code_id']  # attrs 中以字典的形式存了上面所有的数据
        text = attrs['text']

        # 查询 redis 数据库，查询真实的验证码
        redis_conn = get_redis_connection('velify_codes')
        real_image_code = redis_conn.get('img_%s' % image_code_id)

        if real_image_code is None:
            # 说明验证码过期或者不存在
            raise serializers.ValidationError('无效的图片验证码')

        # 进行对比
        real_image_code = real_image_code.decode()  # 数据库中的验证码是字节类型，需要转码
        if real_image_code.lower() != text.lower():
            raise serializers.ValidationError('图片验证码错误')

        # redis 中发送短信验证码的标志 send_flag_<mobile>: 1, 由 redis 维护 60s 的有效期
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            raise serializers.ValidationError('发送短信次数过于频繁')

        return attrs












