from celery import Celery

# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'


celery_app = Celery('meiduo')

# 导入配置文件
celery_app.config_from_object('celery_tasks.config')

# 自动注册celery任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.emails', 'celery_tasks.htmls'])

# 开启 celery 命令
# celery -A 应用路径 (.包路径) worker -l info
# 运行方式： 跳转到这个路径： /Desktop/meiduo/meiduo_mall
# celery -A celery_tasks.main worker -l info

