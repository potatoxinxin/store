from rest_framework.renderers import JSONRenderer as DRF_JSONRenderer


class JSONRender(DRF_JSONRenderer):
    charset = 'utf-8'