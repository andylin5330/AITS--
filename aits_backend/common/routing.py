from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/logs/(?P<task_id>\w+)/$', consumers.LogConsumer.as_asgi()),
]
