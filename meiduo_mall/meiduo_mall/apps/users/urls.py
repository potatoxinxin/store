from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [
    url(r'^users/$', views.UserView.as_view()),
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),  # 登录，获取 JWT token
    url(r'^accounts/(?P<account>\w{4,20})/sms/token/$', views.SMSCodeTokenView.as_view()),  # 获取发送短信验证码的 token
    url(r'^accounts/(?P<account>\w{4,20})/password/token/$', views.PasswordTokenView.as_view()),  # 获取修改密码的 token
    url(r'^users/(?P<pk>\d+)/password/$', views.PasswordView.as_view()),  # 重置密码
    url(r'^user/$', views.UserDetailView.as_view()),  # 用户个人中心数据
    url(r'^emails/$', views.EmailView.as_view()),  # 设置邮箱
    url(r'^emails/verification/$', views.EmailVerifyView.as_view()),  # 设置邮箱
]